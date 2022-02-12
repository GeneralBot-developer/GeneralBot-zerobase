import asyncio

from GBot.core import GeneralBotCore
import nextcord
from nextcord.ext import commands
import youtube_dl
from GBot.models.songlist import SongList

import json

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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        print(self.data)
        self.title: str = data.get('title')
        self.url: str = data.get('url')
        self.thumbnail: str = data.get('thumbnail')
        self.end_time: int = data.get('duration')
        self.channel: int = data.get('channel')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
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
            nextcord.FFmpegPCMAudio(
                filename,
                **ffmpeg_options
                ),
            data=data
            )


class Music_Player(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.queue = {}

    @commands.group(name="music", aliases=["m"], invoke_without_command=True)
    async def music(self, ctx):
        """Music commands"""
        if ctx.invoked_subcommand is None:
            return

    async def create_embed(self, ctx, source: YTDLSource):
        embed = nextcord.Embed(title="再生中...", color=0x00ff00)
        embed.add_field(name="曲名", value=source.title)
        embed.add_field(name="再生時間", value=source.duration)
        embed.add_field(name="URL", value=source.url)
        embed.add_field(name="チャンネル名 ", value=source.channel)
        embed.set_image(source.thumbnail)
        return embed

    async def play_only(self, ctx, url):
        """Play only"""
        async with ctx.typing():
            source = await YTDLSource.from_url(
                url,
                loop=self.bot.loop,
                stream=True
                )
            self.queue[ctx.guild.id].append(source)

            await ctx.send(embed=await self.create_embed(ctx, source))

    async def play_end(self, ctx):
        """play_end"""

    @music.command(name="play", aliases=["p"])
    async def play(self, ctx, url):
        if ctx.author.voice is None:
            await ctx.reply("あなたはボイスチャンネルに接続していません。")
            return
        await ctx.author.voice.channel.connect()
        await ctx.reply("接続しました。")
        await self.play_only(ctx, url)

    @music.command(name="stop", aliases=["s"])
    async def stop(self, ctx):
        ctx.voice_client.stop()
        await ctx.reply("停止しました。")
