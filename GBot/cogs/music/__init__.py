# -*- coding: utf-8 -*-
from GBot.core import GeneralBotCore
from GBot.data.voice import VoiceState
from discord.ext import commands
from discord.ext.commands import Context
from .core import Player
from . import core
import importlib


class DiscordMusicPlayer(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot

    @commands.group(name="music", aliases=["m"], help="音楽を再生します。")
    async def music(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @music.command(name='join', aliases=['j'])
    async def join(self, ctx: Context):
        """Join voice channel"""
        if ctx.author.voice is None:
            await ctx.reply("あなたはボイスチャンネルに接続していません。")
            return
        if ctx.guild.voice_client is None \
                or VoiceState.NOT_PLAYED == self.bot.voice[ctx.guild.id]:
            Player.create(
                guild_id=ctx.guild.id,
                loop=self.bot.loop
            )
            await ctx.author.voice.channel.connect()
            self.bot.voice[ctx.guild.id] = VoiceState.MUSIC
            await ctx.reply("接続しました。")
        else:
            await ctx.reply("使用中です。")

    @music.command(name='leave', aliases=['l'])
    async def leave(self, ctx: Context):
        """Leave voice channel"""
        player = Player.get(guild_id=ctx.guild.id)
        if ctx.guild.voice_client is None:
            await ctx.reply("接続していません。")
            return
        if not VoiceState.NOT_PLAYED == self.bot.voice[ctx.guild.id]:
            player.leave(ctx)
            await ctx.reply("停止しました。")
        else:
            await ctx.reply("使用中です。")

    @music.command(name='play', aliases=['p'])
    async def play(self, ctx: Context, url: str):
        """Play music"""
        player = Player.found(ctx.guild.id)
        if not player:
            return await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        if VoiceState.NOT_PLAYED == self.bot.voice[ctx.guild.id]:
            return await ctx.reply("使用中です。")
        await player.queue_add(url)
        await player.play(ctx)

    @music.command(name='pause')
    async def pause(self, ctx: Context):
        """Pause music"""
        player = Player.found(ctx.guild.id)
        if not player:
            await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        player.pause(ctx)
        await ctx.reply("一時停止しました。")

    @music.command(name='resume', aliases=['r'])
    async def resume(self, ctx: Context):
        """Resume music"""
        player = Player.found(ctx.guild.id)
        if not player:
            await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        player.resume(ctx)
        await ctx.reply("再生しました。")

    @music.command(name='stop', aliases=['s'])
    async def stop(self, ctx: Context):
        """Stop music"""
        player = Player.found(ctx.guild.id)
        if not player:
            await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        player.stop(ctx)
        await ctx.reply("停止しました。")

    @music.command(name='queue', aliases=['q'])
    async def queue(self, ctx: Context):
        """Queue list"""
        player = Player.found(ctx.guild.id)
        if not player:
            await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        await ctx.send(embed=player.queue_list())

    @music.command(name='now', aliases=['n'])
    async def now(self, ctx: Context):
        """Now playing"""
        player = Player.found(ctx.guild.id)
        if not player:
            await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        await ctx.send(embed=player.queue_now())

    @music.command(name='volume', aliases=['v'])
    async def volume(self, ctx: Context, volume: int):
        """Volume"""
        player = Player.found(ctx.guild.id)
        if not player:
            return await ctx.send("接続していません。")
        elif not 0 <= volume <= 100:
            return await ctx.reply("0から100の間で指定してください。")
        player = Player.get(ctx.guild.id)
        player.volume(ctx, volume)
        await ctx.reply("音量を{}にしました。".format(volume))

    @music.command(name='shuffle', aliases=['random, r'])
    async def shuffle(self, ctx: Context):
        """Shuffle"""
        player = Player.found(ctx.guild.id)
        if not player:
            await ctx.send("接続していません。")
        player = Player.get(ctx.guild.id)
        player.queue_shuffle()
        await ctx.reply("シャッフルしました。")


async def setup(bot: GeneralBotCore):
    await bot.add_cog(DiscordMusicPlayer(bot))
    importlib.reload(core)
