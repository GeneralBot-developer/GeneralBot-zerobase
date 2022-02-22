from nextcord.ext import commands
from GBot.CRUD.auth import Auth
from GBot.CRUD.guild import Guild
import string
import secrets
from captcha.image import ImageCaptcha
import nextcord


class user_auth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_random_password_string(length):
        pass_chars = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(pass_chars) for x in range(length))
        return password

    def create_passimage(self):
        image = ImageCaptcha()
        return image.generate(self.get_random_password_string())

    @commands.group(name="auth", aliases=["auths"])
    async def auth(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @auth.command(name="setting", aliases=["set"])
    async def auth_on(self, ctx, on_off: bool):
        guild = await Guild(ctx.guild.id).get()
        if guild.auth == False:
            await ctx.reply("既に無効化されています。")
        elif guild.auth == True:
            await ctx.reply("既に有効化されています。")
        else:
            pass
        await guild.set(auth=on_off)
        await ctx.send(f"認証を{'有効化' if on_off else '無効化'}しました。")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = await Guild(member.guild.id).get()
        channel = self.bot.get_channel(guild.auth_ch)
        if guild.auth is None:
            return
        else:
            Auth.create(member.id)
            file = nextcord.File(self.create_passimage(), filename="captcha.png")
            await channel.send(content=f"<@{member.id}> パスコード認証をしてください。", file=file)

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = await Guild(message.guild.id).get()
        if guild.auth is None:
            return
        elif not guild.auth:
            return
        else:
            pass
        if message.author.bot:
            return
        elif message.channel.id != guild.auth_ch:
            return
        else:
            pass
        if message.content == await Auth(message.author.id).get().passcord:
            await message.channel.send(f"<@{message.author.id}> パスコード認証に成功しました。")
            await Auth(message.author.id).delete()
        else:
            await message.channel.send(f"<@{message.author.id}> パスコード認証に失敗しました。")


def setup(bot):
    bot.add_cog(user_auth(bot))
