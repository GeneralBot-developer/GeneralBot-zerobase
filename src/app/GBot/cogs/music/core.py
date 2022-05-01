import youtube_dl
import discord
import asyncio
from discord.ext import commands
from typing import Union, List, Optional
import random

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title: str = data.get('title')
        self.url: str = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration: int = data.get('duration')
        self.channel: str = data.get('channel')

    @classmethod
    async def from_url(
            cls,
            url,
            *,
            loop=None,
            stream=True
    ) -> Union[List['YTDLSource'], 'YTDLSource']:
        data, filename = await cls._from_url(url, loop=loop, stream=stream)
        if isinstance(data, list):
            datas = []
            for data in data:
                filename = data.get('url')
                datas.append(
                    cls(
                        discord.FFmpegPCMAudio(
                            filename,
                            **ffmpeg_options
                        ),
                        data=data
                    )
                )
            return datas
        else:
            return cls(
                discord.FFmpegPCMAudio(
                    filename,
                    **ffmpeg_options
                ),
                data=data
            )

    @staticmethod
    async def _from_url(url, *, loop=None, stream=False) -> Union[list, 'YTDLSource']:
        loop = loop or asyncio.get_event_loop()
        data: Union[dict, "YTDLSource"] = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            return data['entries'], None
        filename: str = data['url'] if stream else ytdl.prepare_filename(data)
        return data, filename


class AudioQueue(asyncio.Queue):
    def __init__(self):
        super().__init__(100)

    def __getitem__(self, idx):
        return self._queue[idx]

    def to_list(self):
        return list(self._queue)

    def reset(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)


class CommonModules:
    def _convert_m_s(self, time) -> str:
        m, s = divmod(time, 60)
        return f'{m:02d}:{s:02d}'

    @classmethod
    def make_embed(cls, data: YTDLSource) -> discord.Embed:
        cls = cls()
        embed = discord.Embed(
            title=data.title,
            url=data.url,
            description=f'{data.channel}',
            color=0x00ff00
        )
        embed.set_thumbnail(url=data.thumbnail)
        embed.set_footer(text=f'Duration: {cls._convert_m_s(data.duration)}')
        return embed


class AudioStatus:
    def __init__(self, ctx: commands.Context, vc: discord.VoiceClient):
        self.vc: discord.VoiceClient = vc
        self.ctx: commands.Context = ctx
        self.queue = AudioQueue()
        self.playing = asyncio.Event()
        asyncio.create_task(self.playing_task())

    async def add_audio(self, title, data):
        await self.queue.put([title, data])

    def get_list(self) -> List[str]:
        return self.queue.to_list()

    async def playing_task(self) -> None:
        while True:
            self.playing.clear()
            try:
                data = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=180
                )
            except asyncio.TimeoutError:
                asyncio.create_task(self.leave())
            self.vc.play(data[1], after=self.play_next)
            embed = CommonModules.make_embed(data[1])
            await self.ctx.send(embed=embed)
            await self.playing.wait()

    def play_next(self, err=None) -> None:
        self.playing.set()

    async def leave(self) -> None:
        self.queue.reset()
        if self.vc:
            await self.vc.disconnect()
            self.vc = None

    @property
    def is_playing(self) -> bool:
        return self.vc.is_playing()

    def get_now_playing(self) -> Optional[str]:
        return self.queue.get()[0]

    def stop(self) -> None:
        self.vc.stop()

    def skip(self) -> None:
        self.vc.stop()

    def remove(self, index: int) -> None:
        self.queue.remove(index)

    def set_volume(self, volume: float) -> None:
        self.vc.source.volume = volume

    def shuffle(self) -> None:
        self.queue.shuffle()

    def set_repeat(self, repeat: bool) -> None:
        self.vc.source.repeat = repeat

    def set_loop(self, loop: bool) -> None:
        self.vc.source.loop = loop
