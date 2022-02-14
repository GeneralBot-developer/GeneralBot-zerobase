import gTTS
from nextcord.ext import commands
import nextcord


class Text_To_Speech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.using = {}
        self.speaking = {}

    def create_voice_file(self, text):
        tts = gTTS(text=text, lang="ja")
        return nextcord.FFmpegPCMAudio(tts)

    @commands.group(name="tts", aliases=["text_to_speech"], help="テキストを読み上げる")
    async def tts(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @tts.command(name="join", aliases=["j"], help="Botをボイスチャンネルに参加させる")
    async def join(self, ctx):
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()

    @commands.Cog.listener("on_message")
    async def text_speeking(self, message):
        if self.using.get(message.guild.id) is None:
            return
        if not self.using[message.guild.id] == message.channel.id:
            return
        self.speaking[message.guild.id] = message.content


def setup(bot):
    bot.add_cog(Text_To_Speech(bot))
