from discord.ext import commands
from discord import app_commands
from GBot.CRUD.guild import Guild
from GBot.core import GeneralBotCore
import string
import secrets
import discord
from discord import ui
from typing import List, Dict


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
            label=f"ランダムパスワード：{self.true_pass}",
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
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.process_dict: Dict[discord.Guild, List[discord.Member]] = {}

    group = app_commands.Group(name="auth", description="認証系コマンド")

    @group.command(name="setup", description="実行したチャンネルに認証用の設定を行う")
    async def setup(self, inter: discord.Interaction):
        if Guild(inter.guild.id).get().auth_channel_id is None or True:
            Guild(inter.guild.id).set(
                auth_channel_id=inter.channel.id
            )

        if Guild(inter.guild.id).get().auth_role is None:
            await inter.response.send_message(
                "認証用のロールが設定されていません。"
            )
            return
        await inter.response.send_message(
            "認証用の設定を行いました。"
        )

    # role引数が正しいかどうかを確認し、正しければGuild.auth_roleを設定する
    @group.command(name="role", description="認証用のロールを設定する")
    async def role(self, inter: discord.Interaction, role: discord.Role):
        check = self.bot.get_guild(inter.guild.id).get_role(role.id)
        if check is None:
            await inter.response.send(
                "指定されたロールは存在しません。"
            )
            return
        if role.id == Guild(inter.guild.id).get().auth_role:
            await inter.response.send_message(
                "認証用のロールは設定済みです。"
            )
            return
        Guild(inter.guild.id).set(
            auth_role=role.id
        )
        await inter.response.send_message(
            "認証用のロールを設定しました。"
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if Guild(member.guild.id).get().auth_channel_id is None:
            return
        channel = member.guild.get_channel(
            Guild(member.guild.id).get().auth_channel_id
        )
        if channel is None:
            return
        self.process_dict[member.guild].append(member)
        await channel.send(
            f"{member.mention} さん、認証を行ってください。",
            view=AuthView(PassModal)
        )

    # 認証し忘れ、または認証に失敗した場合に再認証できるようにするスラッシュコマンド
    @group.command(name="reauth", description="認証に失敗した場合に再認証する")
    async def reauth(self, inter: discord.Interaction):
        pass


async def setup(bot) -> None:
    return await bot.add_cog(UserAuth(bot))
