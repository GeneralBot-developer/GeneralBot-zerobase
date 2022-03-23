# -*- coding: utf-8 -*-
import asyncio

from GBot.core import GeneralBotCore
from GBot.data.voice import VoiceState
import discord
from discord import ui
from discord.ext import commands
from discord.ext.commands import Context
from .core import Player


class DiscordMusicPlayer(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot

    @commands.command(name='join', aliases=['j'])
    async def join(self, ctx: Context):
        """Join voice channel"""
        if ctx.author.voice is None:
            await ctx.reply("あなたはボイスチャンネルに接続していません。")
            return
        if ctx.guild.voice_client is None \
                or VoiceState.NOT_PLAYED == self.bot.voice[ctx.guild.id]:
            Player.create(
                guild_id=ctx.guild.id,
                voice_client=ctx.voice_client,
                loop=self.bot.loop
            )
            await ctx.author.voice.channel.connect()
            self.bot.voice[ctx.guild.id] = VoiceState.MUSIC
            await ctx.reply("接続しました。")
        else:
            await ctx.reply("使用中です。")

    @commands.command(name='leave', aliases=['l'])
    async def leave(self, ctx: Context):
        """Leave voice channel"""
        if ctx.guild.voice_client is None:
            await ctx.reply("接続していません。")
            return
        if not VoiceState.NOT_PLAYED == self.bot.voice[ctx.guild.id]:
            ctx.voice_client.stop()
            await ctx.reply("停止しました。")
        else:
            await ctx.reply("使用中です。")

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx: Context, url: str):
        """Play music"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        if VoiceState.NOT_PLAYED == self.bot.voice[ctx.guild.id]:
            await ctx.reply("使用中です。")
            return
        player.queue_add(url)
        player.play()
        await ctx.reply("キューに追加しました。")

    @commands.command(name='pause', aliases=['p'])
    async def pause(self, ctx: Context):
        """Pause music"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        player.pause()
        await ctx.reply("一時停止しました。")

    @commands.command(name='resume', aliases=['r'])
    async def resume(self, ctx: Context):
        """Resume music"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        player.resume()
        await ctx.reply("再生しました。")

    @commands.command(name='stop', aliases=['s'])
    async def stop(self, ctx: Context):
        """Stop music"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        player.stop()
        await ctx.reply("停止しました。")

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx: Context):
        """Queue list"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        await ctx.send(embed=player.queue_list())

    @commands.command(name='now', aliases=['n'])
    async def now(self, ctx: Context):
        """Now playing"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        await ctx.send(player.queue_now())

    @commands.command(name='volume', aliases=['v'])
    async def volume(self, ctx: Context, volume: int):
        """Volume"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        if not 0 <= volume <= 100:
            await ctx.reply("0から100の間で指定してください。")
        player = Player(ctx.guild.id)
        player.volume(volume)
        await ctx.reply("音量を{}にしました。".format(volume))

    @commands.command(name='shuffle', aliases=['s'])
    async def shuffle(self, ctx: Context):
        """Shuffle"""
        player = Player(ctx.guild.id).get()
        if not player:
            await ctx.send("接続していません。")
        player = Player(ctx.guild.id)
        player.queue_shuffle()
        await ctx.reply("シャッフルしました。")


async def setup(bot: GeneralBotCore):
    await bot.add_cog(DiscordMusicPlayer(bot))