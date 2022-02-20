from nextcord.ext import commands
import nextcord
from GBot.data.voice import VoiceState
from GBot.core import GeneralBotCore
import MeCab
import json
import os
import subprocess
from pydub import AudioSegment
from nextcord.ext.commands import Context
from nextcord import Message
import re


class CommonModule:
    def load_json(self, file, encoding):
        with open(file, 'r', encoding=encoding) as f:
            json_data = json.load(f)
        return json_data


class NLP:
    def __init__(self):
        self.cm = CommonModule()

    def morphological_analysis(self, text, keyword='-Ochasen'):
        words = []
        tagger = MeCab.Tagger(keyword)
        result = tagger.parse(text)
        result = result.split('\n')
        result = result[:-2]

        for word in result:
            temp = word.split('\t')
            print(word)
            word_info = {
                'surface': temp[0],
                'kana': temp[1],
                'base': temp[2],
                'pos': temp[3],
                'conjugation': temp[4],
                'form': temp[5]
            }
            words.append(word_info)
        return words

    def evaluate_pn_ja_wordlist(self, wordlist, word_pn_dictpath=None):
        if word_pn_dictpath is None:
            word_pn_dict = self.cm.load_json(file='./GBot/data/pn_ja.json', encoding='cp932')
        else:
            word_pn_dict = self.cm.load_json(word_pn_dictpath)

        pn_value = 0
        for word in wordlist:
            pn_value += self.evaluate_pn_ja_word(word, word_pn_dict)

        return pn_value

    def evaluate_pn_ja_word(self, word, word_pn_dict: dict):
        if isinstance(word, dict):
            word = word['base']
        elif isinstance(word, str):
            pass
        else:
            raise TypeError

        if word in word_pn_dict.keys():
            pn_value = float(word_pn_dict[word]['value'])
            return pn_value
        return 0

    def analysis_emotion(self, text):
        split_words = self.morphological_analysis(text, "-Ochasen")
        pn_value = self.evaluate_pn_ja_wordlist(split_words)
        if pn_value > 0.5:
            emotion = 'happy'
        elif pn_value < -1.0:
            emotion = 'angry'
        elif pn_value < -0.5:
            emotion = 'sad'
        else:
            emotion = 'normal'
        return emotion


class VoiceChannel:
    def __init__(self):
        self.conf = {
            "voice_configs": {
                "htsvoice_resource": "/usr/share/hts-voice/",
                "jtalk_dict": "/var/lib/mecab/dic/open-jtalk/naist-jdic"}}

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
                        ][
                            'htsvoice_resource'
                        ],
                        'mei/mei_normal.htsvoice'
                    )
                ],
                'angry': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'mei/mei_angry.htsvoice'
                    )
                ],
                'bashful': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'mei/mei_bashful.htsvoice'
                    )
                ],
                'happy': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'mei/mei_happy.htsvoice'
                    )],
                'sad': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'mei/mei_sad.htsvoice'
                    )
                ]
            },
            'm100': {
                'normal': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'm100/nitech_jp_atr503_m001.htsvoice'
                    )
                ]
            },
            'tohoku-f01': {
                'normal': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'htsvoice-tohoku-f01-master/tohoku-f01-neutral.htsvoice'
                    )
                ],
                'angry': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'htsvoice-tohoku-f01-master/tohoku-f01-angry.htsvoice'
                    )
                ],
                'happy': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'htsvoice-tohoku-f01-master/tohoku-f01-happy.htsvoice'
                    )
                ],
                'sad': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                        ][
                            'htsvoice_resource'
                        ],
                        'htsvoice-tohoku-f01-master/tohoku-f01-sad.htsvoice'
                    )
                ]
            }
        }

        open_jtalk = ['open_jtalk']
        mech = ['-x', self.conf['voice_configs']['jtalk_dict']]
        speed = ['-r', '1.0']
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

    def remove_custom_emoji(self, text):
        pattern = r'<:[a-zA-Z0-9_]+:[0-9]+>'    # カスタム絵文字のパターン
        return re.sub(pattern, '', text)   # 置換処理

    # urlAbb
    # URLなら省略
    def urlAbb(self, text):
        pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        return re.sub(pattern, 'URLは省略するのデス！', text)   # 置換処理

    def register_processing(
        self,
        text: str,
        channel: nextcord.TextChannel,
    ):
        self.voice_processings.append({
            channel.id: text
        }
        )
        return

    def create_voice(self, ctx: Context):
        nlp = NLP()
        vc = VoiceChannel()
        text = self.voice_processings[-1]
        text = text[ctx.channel.id]
        text = self.remove_custom_emoji(text)
        text = self.urlAbb(text)
        emotion = nlp.analysis_emotion(text)
        voice_file = vc.make_by_jtalk(text, "tts_voice", emotion=emotion)
        return nextcord.FFmpegPCMAudio(voice_file)

    async def play_only(self, ctx):
        text = self.create_voice(ctx)
        ctx.guild.voice_client.play(
            text,
            after=lambda _: self.bot.loop.create_task(
                self.play_end(
                    ctx
                )
            )
        )

    async def play_end(self, ctx):
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
            await ctx.guild.voice_client.disconnect()
            del self.voice_processings[ctx.channel.id]
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
        if message.author.bot:
            return
        if message.content.startswith(await self.bot.get_prefix(message)):
            return
        if message.author.voice is None:
            return
        if self.bot.voice[message.guild.id] == VoiceState.NOT_PLAYED or \
                self.bot.voice[message.guild.id] == VoiceState.MUSIC:
            return
        self.register_processing(message.content, message.channel)
        ctx = await self.bot.get_context(message)
        await self.play_only(ctx)


def setup(bot):
    bot.add_cog(Text_To_Speech(bot))
