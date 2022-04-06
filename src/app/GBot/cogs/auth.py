from discord.ext import commands
from GBot.CRUD.auth import Auth
from GBot.CRUD.guild import Guild
import string
import secrets
from captcha.image import ImageCaptcha
import discord


class user_auth(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def get_random_password_string(self, length):
        pass_chars = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(pass_chars) for x in range(length))
        return password

    def create_passimage(self, text):
        image = ImageCaptcha()
        return image.generate(text)

    @commands.group(name="auth", aliases=["auths"], help="画像認証の設定を行います")
    async def auth(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @auth.command(name="setting", aliases=["set"], help="画像認証を有効化、または無効化します")
    async def auth_on(self, ctx, on_off: bool, auth_role: int = None):
        guild = await Guild(ctx.guild.id).get()
        if guild.auth == on_off:
            if on_off:
                return await ctx.reply("既に有効化されています。")
            else:
                return await ctx.reply("既に無効化されています。")
        if not on_off:
            return await Guild(ctx.guild.id).set(auth=on_off)
        if auth_role is None:
            return await ctx.reply("ロールIDを指定してください。")
        await Guild(ctx.guild.id).set(
            auth=on_off,
            auth_ch=ctx.channel.id,
            auth_role=auth_role)
        await ctx.send(f"認証を{'有効化' if on_off else '無効化'}しました。")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = await Guild(member.guild.id).get()
        channel = self.bot.get_channel(guild.auth_ch)
        if not guild.auth:
            return
        else:
            passcord = self.get_random_password_string(4)
            await Auth.create(user_id=member.id, passcord=passcord)
            file = discord.File(self.create_passimage(passcord),
                                filename="captcha.png")
            await channel.send(
                content=f"<@{member.id}> パスコード認証をしてください。",
                file=file
            )

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        guild = await Guild(member.guild.id).get()
        if not guild.auth:
            return
        else:
            await Auth(user_id=member.id).delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = await Guild(message.guild.id).get()
        auth = await Auth(message.author.id).get()
        if not guild.auth:
            return
        elif not auth:
            return
        elif message.author.bot:
            return
        elif message.channel.id != guild.auth_ch:
            return
        else:
            pass
        if message.content == auth.passcord:
            await message.channel.send(
                f"<@{message.author.id}> パスコード認証に成功しました。")
            await Auth(message.author.id).delete()
            role = self.bot.get_role(guild.auth_role)
            await message.author.add_roles(role)
        else:
            await message.channel.send(
                f"<@{message.author.id}> パスコード認証に失敗しました。")

    @auth.command(
        name="change",
        aliases=["changepass"],
        help="ロールIDとチャンネルIDを変更します。"
    )
    async def guild_setting_change(self, ctx, column, value):
        guild = await Guild(ctx.guild.id).get()
        if not guild.auth:
            return
        else:
            pass
        if ctx.author.id != guild.owner_id:
            return await ctx.reply("このコマンドはオーナーのみ使用できます。")
        if column == "auth_role":
            role = self.bot.get_role(value)
            if role is None:
                return await ctx.reply("ロールIDが間違っています。")
            await Guild(ctx.guild.id).set(column=column, value=value)
            return await ctx.reply("変更しました。")
        elif column == "auth_ch":
            channel = self.bot.get_channel(value)
            if channel is None:
                return await ctx.reply("チャンネルIDが間違っています。")
            await Guild(ctx.guild.id).set(column=column, value=value)
            return await ctx.reply("変更しました。")
        else:
            return await ctx.reply("変更する項目を指定してください。")


async def setup(bot):
    return await bot.add_cog(user_auth(bot))
