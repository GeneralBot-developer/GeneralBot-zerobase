import youtube_dl
import discord
import asyncio
from typing import Dict, List
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
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.channel: str = data.get('channel')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False) -> 'YTDLSource':
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(
                url,
                download=not stream
            )
        )

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(
            discord.FFmpegPCMAudio(filename,
                                   **ffmpeg_options), data=data
        )


class Player:
    player_list: Dict[int: "Player"] = {}

    def __init__(self, guild_id, voice_client: discord.VoiceClient, loop=None):
        self.guild_id: int = guild_id
        self.voice_client = voice_client
        self.queue: List[YTDLSource] = []
        self.current_song: YTDLSource = None
        self.loop: asyncio.AbstractEventLoop = loop
        self.repeat: bool = False
        self.player_list[guild_id] = self

    def get_h_m_s(td) -> str:
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s

    def get(self) -> bool:
        if self.player_list.get(self.guild_id) is None:
            return False
        else:
            return True

    # YTDLSouce.from_urlで取得したdataをqueueに追加
    def queue_add(self, url: str, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = YTDLSource.from_url(url, loop=loop)
        self.queue.append(data)

    def queue_remove(self, index: int):
        self.queue.pop(index)

    def is_repeat(self) -> bool:
        return self.repeat

    def repeat_toggle(self):
        self.repeat = not self.repeat

    def get_queue(self) -> List[YTDLSource]:
        return self.queue

    def get_current_song(self) -> YTDLSource:
        return self.current_song

    def get_current_song_index(self) -> int:
        return self.queue.index(self.current_song)

    # dataを元にタイトル、URL、時間、サムネイルを含むdiscord.Embedを作成
    def create_embed(self, data: YTDLSource, is_playing: bool = False)-> discord.Embed:
        if is_playing:
            status = "キューに追加"
        else:
            status = "再生中"
        embed = discord.Embed(
            title=f"{status}：{data.title}",
            url=data.url,
            color=0x00ff00
        )
        embed.set_thumbnail(url=data.thumbnail)
        embed.set_author(name=data.channel)
        embed.set_footer(text=f'{data.duration}')
        return embed

    async def after_playback(self, ctx: discord.commands.Context):
        if self.repeat:
            self.play()
        else:
            self.queue[self.guild_id].pop(-1)
            if len(self.queue[self.guild_id]) > 0:
                self.play()
            else:
                self.current_song = None
                self.voice_client.stop()
                await ctx.send("再生を停止しました。")

    async def play(self, ctx: discord.commands.Context):
        self.current_song = self.queue[-1]
        embed = self.create_embed(
            self.current_song,
            self.voice_client.is_playing()
        )
        await ctx.send(embed=embed)
        self.voice_client.play(
            self.current_song,
            after=lambda _: self.loop.create_task(
                self.after_playback(ctx)
            )
        )

    def stop(self):
        self.current_song = None
        self.voice_client.stop()

    def pause(self):
        self.voice_client.pause()

    def resume(self):
        self.voice_client.resume()

    def skip(self):
        self.queue.pop(-1)
        self.voice_client.stop()

    def queue_clear(self):
        self.queue = []
        self.voice_client.stop()

    def queue_list(self) -> discord.Embed:
        embed = discord.Embed(
            title="キュー",
            color=0x00ff00
        )
        for i, data in enumerate(self.queue):
            embed.add_field(
                name=f"{i + 1}",
                value=self.create_embed(data, False).title,
                inline=False
            )
        return embed

    def queue_now(self) -> discord.Embed:
        embed = discord.Embed(
            title="再生中",
            color=0x00ff00
        )
        embed.add_field(
            name="再生中",
            value=self.create_embed(self.current_song, True).title,
            inline=False
        )
        return embed

    def queue_shuffle(self):
        random.shuffle(self.queue)

    def volume(self, volume: int):
        self.voice_client.source.volume = volume

    @classmethod
    def create(cls, **kwargs):
        self = cls(**kwargs)
        self.player_list[self.guild_id] = self
        return self
