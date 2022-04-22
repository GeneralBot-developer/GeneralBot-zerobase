from discord.ext import commands
import discord
from GBot.data.voice import VoiceState
from GBot.core import GeneralBotCore
import os
import subprocess
from pydub import AudioSegment
from discord.ext.commands import Context
from discord import Message
import re


class CreateVoice:
    def __init__(self):
        self.conf = {
            "voice_configs": {
                "htsvoice_resource": "/usr/share/hts-voice/",
                "jtalk_dict": "/var/lib/mecab/dic/open-jtalk/naist-jdic"
            }
        }

    def make_by_jtalk(
            self,
            text,
            filepath='voice_message',
            voicetype='mei',
            emotion='normal'):
        htsvoice = {
            'mei': {
                'normal': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ]
                        [
                            'htsvoice_resource'
                        ],
                        'mei/mei_normal.htsvoice'
                    )
                ]
            }
        }

        open_jtalk = ['open_jtalk']
        mech = ['-x', self.conf['voice_configs']['jtalk_dict']]
        speed = ['-r', '0.5']
        outwav = ['-ow', filepath + '.wav']
        cmd = open_jtalk + mech + htsvoice[voicetype][emotion] + speed + outwav
        c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        c.stdin.write(text.encode())
        c.stdin.close()
        c.wait()
        audio_segment = AudioSegment.from_wav(filepath + '.wav')
        os.remove(filepath + '.wav')
        audio_segment.export(filepath + '.mp3', format='mp3')
        return filepath + '.mp3'


class Text_To_Speech(commands.Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.voice_processings = []
        self.using_textchannel = []

    def remove_custom_emoji(self, text):
        pattern = r'<:[a-zA-Z0-9_]+:[0-9]+>'  # カスタム絵文字のパターン
        return re.sub(pattern, '', text)  # 置換処理

    # urlAbb
    # URLなら省略
    def urlAbb(self, text):
        pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        return re.sub(pattern, 'URLは省略するのデス！', text)  # 置換処理

    def register_processing(
        self,
        text: str,
        channel: discord.TextChannel,
    ):
        self.voice_processings.append({channel.id: text})
        return

    def create_voice(self, ctx: Context):
        vc = CreateVoice()
        text = self.voice_processings[-1]
        text = text[ctx.channel.id]
        text = self.remove_custom_emoji(text)
        text = self.urlAbb(text)
        voice_file = vc.make_by_jtalk(text, "tts_voice")
        return discord.FFmpegPCMAudio(voice_file)

    async def play_only(self, ctx):
        text = self.create_voice(ctx)
        ctx.guild.voice_client.play(
            text,
            after=lambda _: self.bot.loop.create_task(self.play_end(ctx)))

    async def play_end(self, ctx):
        if len(self.voice_processings) < 0:
            return
        self.voice_processings.pop(-1)

    @commands.group(name="tts", aliases=["text_to_speech"], help="テキストを読み上げる")
    async def tts(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @tts.command(name="join", aliases=["j"], help="Botをボイスチャンネルに参加させる")
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("あなたはボイスチャンネルに参加していません")
        vs = self.bot.voice[ctx.guild.id]
        print(vs)
        if not VoiceState.NOT_PLAYED == vs:
            return await ctx.send("Botは既にボイスチャンネルに参加しています")
        else:
            self.using_textchannel.append(ctx.channel.id)
            self.bot.voice[ctx.guild.id] = VoiceState.YOMIAGE
            await ctx.author.voice.channel.connect()
            await ctx.send("Botをボイスチャンネルに参加しました")

    @tts.command(name="leave", aliases=["l"], help="Botをボイスチャンネルから離脱させる")
    async def leave(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("あなたはボイスチャンネルに参加していません")
        voice_state = self.bot.voice[ctx.guild.id]
        if not VoiceState.NOT_PLAYED == voice_state:
            self.bot.voice[ctx.guild.id] = VoiceState.NOT_PLAYED
            self.using_textchannel.remove(ctx.channel.id)
            await ctx.guild.voice_client.disconnect()
            self.using_textchannel.remove(ctx.channel.id)
            await ctx.send("Botをボイスチャンネルから離脱しました")
        else:
            await ctx.send("Botはボイスチャンネルに参加していません")

    @tts.command(name="volume", aliases=["v"], help="ボリュームを変更する")
    async def volume(self, ctx, volume: int):
        if volume < 0 or volume > 100:
            await ctx.reply("0から100の間で指定してください。")
            return
        ctx.voice_client.source.volume = volume / 100
        await ctx.reply(f"音量を{volume}%にしました。")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id not in self.using_textchannel:
            return
        if message.author.bot:
            return
        if message.author.voice is None:
            return
        if self.bot.voice[message.guild.id] == VoiceState.NOT_PLAYED or \
                self.bot.voice[message.guild.id] == VoiceState.MUSIC:
            return
        self.register_processing(message.content, message.channel)
        ctx = await self.bot.get_context(message)
        if ctx.guild.voice_client.is_playing():
            return
        await self.play_only(ctx)


async def setup(bot):
    return await bot.add_cog(Text_To_Speech(bot))
