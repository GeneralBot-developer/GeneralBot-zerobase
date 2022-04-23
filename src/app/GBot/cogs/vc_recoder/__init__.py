from .voice_websocket import MyVoiceClient
from discord.ext import commands
from GBot.data.voice import VoiceManager, VoiceState
from typing import Dict
import discord
from GBot.core import GeneralBotCore
import asyncio


class Voice_Recoder(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.audio_status: Dict[int, MyVoiceClient] = {}

    @commands.group(name="voice_recoder", aliases=["vcr", "voice_rec", "voice_record"])
    async def voice_recoder(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @voice_recoder.command(name="join", aliases=["j"])
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.reply("ボイスチャンネルに参加してください。")
        elif VoiceManager(ctx.guild.id).get() is None:
            VoiceManager.create(ctx.guild.id)
        elif VoiceManager(ctx.guild.id).get() is not VoiceState.NOT_PLAYED:
            return await ctx.reply("使用中です。")
        VoiceManager(ctx.guild.id).set(VoiceState.VC_RECORD)
        vc = await ctx.author.voice.channel.connect(cls=MyVoiceClient)
        self.audio_status[ctx.guild.id] = vc

    @voice_recoder.command(name="start", aliases=["s"])
    async def start(self, ctx: commands.Context, record_time: int):
        loop = asyncio.get_event_loop()
        if self.audio_status.get(ctx.guild.id) is None:
            return await ctx.reply("先にボイスチャンネルに参加してください。")
        vc: MyVoiceClient = self.audio_status[ctx.guild.id]
        await ctx.reply("録音を開始しました。秒数：{}".format(record_time))
        recode_file = await vc.record(record_time)
        file = discord.File(
            recode_file,
            filename="voice_recoder {}s".format(record_time)
        )
        await ctx.reply("録音を終了しました。", file=file)


async def setup(bot):
    await bot.add_cog(Voice_Recoder(bot))
