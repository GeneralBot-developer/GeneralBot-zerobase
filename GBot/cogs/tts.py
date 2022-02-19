import gTTS
from nextcord.ext import commands
import nextcord
from GBot.data.voice import VoiceState
from GBot.core import GeneralBotCore
import MeCab
import json
import os
import subprocess
from pydub import AudioSegment


class CommonModule:
    def load_json(self, file):
        with open(file, 'r', encoding='utf-8') as f:
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
            word_pn_dict = self.cm.load_json('pn_ja.json')
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
                "htsvoice_resource": "/usr/local/Cellar/open-jtalk/1.11/voice/",
                "jtalk_dict": "/usr/local/Cellar/open-jtalk/1.11/dic"}}

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
                    ],
                'angry': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                            ]
                        [
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
                            ]
                        [
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
                            ]
                        [
                            'htsvoice_resource'
                            ],
                        'mei/mei_happy.htsvoice'
                        )
                    ],
                'sad': [
                    '-m',
                    os.path.join(
                        self.conf[
                            'voice_configs'
                            ]
                        [
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
                            ]
                        [
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
                            ]
                        [
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
                            ]
                        [
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
                            ]
                        [
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
                            ]
                        [
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
        self.voice_processings = {}

    async def generate_voicefile(self, ctx):
        message = self.voice_processings[ctx.guild.id]
        tts = gTTS(text=message.content, lang="ja")
        return nextcord.FFmpegPCMAudio(tts)

    @commands.group(name="tts", aliases=["text_to_speech"], help="テキストを読み上げる")
    async def tts(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @tts.command(name="join", aliases=["j"], help="Botをボイスチャンネルに参加させる")
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("あなたはボイスチャンネルに参加していません")
        voice_state = self.bot.voice[ctx.guild.id]
        if not VoiceState.NOT_PLAYED == voice_state(1):
            return await ctx.send("Botは既にボイスチャンネルに参加しています")

        else:
            voice_state = VoiceState.YOMIAGE
            await ctx.author.voice.channel.connect()
            await ctx.send("Botをボイスチャンネルに参加しました")

    @tts.command(name="leave", aliases=["l"], help="Botをボイスチャンネルから離脱させる")
    async def leave(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("あなたはボイスチャンネルに参加していません")
        voice_state = self.bot.voice[ctx.guild.id]
        if not VoiceState.NOT_PLAYED == voice_state(0):
            voice_state = VoiceState.NOT_PLAYED
            await ctx.author.voice.channel.disconnect()
            await ctx.send("Botをボイスチャンネルから離脱しました")
        else:
            await ctx.send("Botはボイスチャンネルに参加していません")

    @commands.Cog.listener()
    async def text_to_speech(self, message):
        if message.author.voice is None:
            return
        if self.bot.voice[message.guild.id] == VoiceState.NOT_PLAYED or \
                self.bot.voice[message.guild.id] == VoiceState.MUSIC:
            return
        self.voice_processings[
            message.guild.id
        ] = message


def setup(bot):
    bot.add_cog(Text_To_Speech(bot))
