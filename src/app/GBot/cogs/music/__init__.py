# -*- coding: utf-8 -*-
from GBot.core import GeneralBotCore
from GBot.data.voice import VoiceState, VoiceManager
from discord.ext import commands
import discord
from .core import AudioStatus, YTDLSource
from typing import Dict
from . import core
import importlib


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
        if voice.state is not VoiceState.NOT_PLAYED:
            return await ctx.send('使用中です。')
        vc = await ctx.author.voice.channel.connect()
        VoiceManager(ctx.guild.id).get().set(VoiceState.MUSIC)
        self.audio_statuses[ctx.guild.id] = AudioStatus(ctx, vc)

    @music.command()
    async def play(self, ctx: commands.Context, *, url: str):
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
        await status.add_audio(data.title, data)

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
        songs = ""
        for i, (title, _) in enumerate(queue):
            songs += f"{i+1}. {title}\n"
        await ctx.send(songs)


async def setup(bot: GeneralBotCore):
    await bot.add_cog(DiscordMusicPlayer(bot))
    importlib.reload(core)
