# -*- coding: utf-8 -*-
from GBot.core import GeneralBotCore
from GBot.data.voice import VoiceState
from discord.ext import commands
from discord.ext.commands import Context
from .core import AudioStatus
from typing import Dict
from . import core
import importlib


class DiscordMusicPlayer(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.audio_statuses: Dict[int, AudioStatus] = {}

    @commands.command()
    async def join(self, ctx: commands.Context):
        # VoiceChannel未参加
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('先にボイスチャンネルに参加してください')
        vc = await ctx.author.voice.channel.connect()
        self.audio_statuses[ctx.guild.id] = AudioStatus(ctx, vc)

    @commands.command()
    async def play(self, ctx: commands.Context, *, title: str = ''):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            await ctx.invoke(self.join)
            status = self.audio_statuses[ctx.guild.id]

    @commands.command()
    async def stop(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('Botはまだボイスチャンネルに参加していません')
        if not status.is_playing:
            return await ctx.send('既に停止しています')
        await status.stop()
        await ctx.send('停止しました')

    @commands.command()
    async def leave(self, ctx: commands.Context):
        status = self.audio_statuses.get(ctx.guild.id)
        if status is None:
            return await ctx.send('ボイスチャンネルにまだ未参加です')
        await status.leave()
        del self.audio_statuses[ctx.guild.id]

    @commands.command()
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
