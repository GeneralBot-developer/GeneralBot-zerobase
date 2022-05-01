# -*- coding: utf-8 -*-
from GBot.core import GeneralBotCore
from GBot.data.voice import VoiceState, VoiceManager
from discord.ext import commands
import discord
from .core import AudioStatus, YTDLSource
from typing import Dict
from . import core
import importlib
from GBot.functions.Paginator import Simple


class DiscordMusicPlayer(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.audio_statuses: Dict[int, AudioStatus] = {}

    @commands.hybrid_group(name='music', aliases=['音楽'])
    async def music(self, ctx) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="エラー",
                description="コマンドが指定されていません。",
                color=0xFF0000
            )
            embed.add_field(name="指定可能なコマンド",
                            value="\n".join([
                                f"```{command.name}```"
                                for command in self.music.walk_commands()
                                if isinstance(command, commands.Command)
                            ]),
                            inline=False)
            await ctx.send(embed=embed)

    @music.command()
    async def join(self, ctx: commands.Context):
        # VoiceChannel未参加
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('先にボイスチャンネルに参加してください')
        voice = VoiceManager(ctx.guild.id).get()
        if not voice:
            voice = VoiceManager.create(ctx.guild.id).get()
        if voice.state is not VoiceState.NOT_PLAYED:
            return await ctx.send('使用中です。')
        vc = await ctx.author.voice.channel.connect()
        VoiceManager(ctx.guild.id).get().set(VoiceState.MUSIC)
        self.audio_statuses[ctx.guild.id] = AudioStatus(ctx, vc)

    @music.command()
    async def play(self, ctx: commands.Context, *, url: str):
        async with ctx.typing():
            status = self.audio_statuses.get(ctx.guild.id)
            if status is None:
                await ctx.invoke(self.join)
                status = self.audio_statuses[ctx.guild.id]
            data = await YTDLSource.from_url(
                url,
                loop=self.bot.loop,
                stream=True
            )
            if isinstance(data, list):
                for d in data:
                    await status.add_audio(d.title, d)
                return
            await status.add_audio(data.title, data)
            if status.is_playing():
                await ctx.send("追加しました。")

    @music.command()
    async def stop(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('既に停止しています')
        await status.stop()
        await ctx.reply('停止しました')

    @music.command()
    async def leave(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('ボイスチャンネルにまだ未参加です')
        await status.leave()
        VoiceManager(ctx.guild.id).get().set(VoiceState.NOT_PLAYED)
        del self.audio_statuses[ctx.guild.id]
        await ctx.reply('退出しました')

    @music.command()
    async def queue(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('先にボイスチャンネルに参加してください')
        queue = status.get_list()
        if not queue:
            return await ctx.send("キューは空っぽだよ。曲入れよう")
        embeds = []
        # 10個ずつ表示
        for i in range(0, len(queue), 10):
            embed = discord.Embed(
                title="キュー",
                description="\n".join([
                    f"{i + 1}. {song[0]}"
                    for i, song in enumerate(queue[i:i + 10])
                ]),
                color=0x00FF00
            )
            embeds.append(embed)
        await Simple().start(ctx=ctx, pages=embeds)

    @music.command(name="now_playing", aliases=["now, playing", "np"])
    async def now_playing(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('音楽はまだ再生されていません')
        embed = discord.Embed(
            title="再生中",
            description=status.get_now_playing(),
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @music.command(name="skip", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('音楽はまだ再生されていません')
        status.skip()
        await ctx.send("次の曲へ")

    @music.command(name="volume", aliases=["v"])
    async def volume(self, ctx: commands.Context, volume: int):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('音楽はまだ再生されていません')
        if volume < 0 or volume > 100:
            return await ctx.send('音量は0から100までです')
        status.set_volume(volume)
        await ctx.send(f"音量を{volume}に設定しました")

    @music.command(name="shuffle", aliases=["sh"])
    async def shuffle(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('音楽はまだ再生されていません')
        status.shuffle()
        await ctx.send("シャッフルしました")

    @music.command(name="repeat", aliases=["r"])
    async def repeat(self, ctx: commands.Context, on_off: bool = False):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('音楽はまだ再生されていません')
        if on_off:
            status.set_repeat(True)
            await ctx.send("リピートしました")
        else:
            status.set_repeat(False)
            await ctx.send("リピートを解除しました")

    @music.command(name="loop", aliases=["l"])
    async def loop(self, ctx: commands.Context, on_off: bool = False):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('音楽はまだ再生されていません')
        if on_off:
            status.set_loop(True)
            await ctx.send("ループしました")
        else:
            status.set_loop(False)
            await ctx.send("ループを解除しました")


async def setup(bot: GeneralBotCore):
    await bot.add_cog(DiscordMusicPlayer(bot))
    importlib.reload(core)
