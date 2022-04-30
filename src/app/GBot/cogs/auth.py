from discord.ext import commands
from GBot.CRUD.guild import Guild
import string
import secrets
from captcha.image import ImageCaptcha
import discord
from discord import ui


def get_random_password_string(length: int) -> str:
    pass_chars = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(pass_chars) for _ in range(length))
    return password


class AuthView(ui.View):
    def __init__(self, *items):
        for item in items:
            self.add_item(item)


class PassModal(
    ui.Modal,
    title="ランダムパスワード認証"
):
    def __init__(self):
        self.true_pass = get_random_password_string(8)
        self.return_pass = ui.TextInput(
            label=f"ワンタイムパスワード：{self.true_pass}",
            required=True,
            max_length=8
        )

    async def on_submit(self, inter: discord.Interaction):
        if self.true_pass == self.return_pass:
            role_id = Guild(inter.guild.id).get().auth_role
            role = discord.utils.get(inter.guild.roles, id=role_id)
            inter.client.get_guild(
                inter.guild.id
            ).get_member(
                inter.author.id
            ).add_roles(
                role
            )
            inter.response.send("Access Granted!")
        else:
            await inter.response.send(
                "パスワードが違います。"
            )


class UserAuth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    return await bot.add_cog(UserAuth(bot))
