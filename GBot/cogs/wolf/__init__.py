from discord.ext.commands import Cog
from sqlalchemy import desc
from GBot.core import GeneralBotCore
from discord import app_commands, Object, Interaction, ui, Embed, Color
from .Game import SessionManager
from .WolfDatas import Day_Cycles
from typing import List


class WerewolfGame(Cog, app_commands.Group):
    def __init__(self, bot: GeneralBotCore):
        super().__init__(name="werewolf", description="人狼ゲームを管理するコマンドです")
        self.bot = bot

    async def show_vote(self, inter: Interaction):
        wolfgame = SessionManager(inter.guild_id).vote_result()
        user = self.bot.get_user(wolfgame)
        embed = Embed(title="処刑投票の結果", description=f"{user.name}", color=Color.green())
        await inter.response.send_message(embed=embed)

    @app_commands.command(name="create", description="セッションを作成します")
    async def create(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if session:
            return await inter.response.send_message("すでにセッションが作成されています")
        else:
            print(inter.guild)
            SessionManager.game_create(inter.guild_id)
            await inter.response.send_message("セッションを作成しました")

    @app_commands.command(name="join", description="セッションに参加します")
    async def join(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません")
            return
        if inter.user.id in session.get_player_list():
            await inter.response.send_message("すでに参加しています")
        SessionManager(inter.guild_id).join(inter.user.id)
        await inter.response.send_message("参加しました")

    @app_commands.command(name="leave", description="セッションから退出します")
    async def leave(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません")
            return
        if inter.user.id not in session.get_player_list():
            await inter.response.send_message("参加していません")
        SessionManager(inter.guild_id).leave(inter.user.id)
        await inter.response.send_message("退出しました")

    @app_commands.command(name="close", description="セッションを閉じます")
    async def close(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません")
            return
        SessionManager(inter.guild_id).close()
        await inter.response.send_message("セッションを閉じました")

    @app_commands.command(name="start", description="セッションを開始します")
    async def start(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません")
            return
        SessionManager(inter.guild_id).start()
        await inter.response.send_message("セッションを開始しました")

    @app_commands.command(name="end", description="セッションを終了します")
    async def end(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません")
            return
        SessionManager(inter.guild_id).end()
        await inter.response.send_message("セッションを終了しました")

    @app_commands.command(name="list", description="セッションに参加しているユーザーを表示します")
    async def list(self, inter: Interaction):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません")
            return
        members = session.members
        if not members:
            await inter.response.send_message("参加しているユーザーはいません")
            return
        embed = Embed(title="参加しているユーザー")
        for member in members:
            embed.add_field(name=member.name, value=member.id)
        await inter.response.send_message(embed=embed)

    @app_commands.command(name="vote", description="投票します")
    async def vote(self, inter: Interaction, target: int):
        session = SessionManager(inter.guild_id).get()
        if not session:
            await inter.response.send_message("セッションが作成されていません", ephemeral=True)
            return
        if target.id not in session.members:
            await inter.response.send_message("投票対象が参加していません", ephemeral=True)
            return
        user = inter.guild.get_member(target.id)
        if user is None:
            await inter.response.send_message("正しいユーザーを指定してください", ephemeral=True)
        SessionManager(inter.guild_id).vote(inter.author.id, target.id)
        await inter.response.send_message("投票しました")
        if SessionManager(inter.guild_id).is_vote_all():
            await inter.response.send_message("投票が終了しました。結果を開示します。")
            await self.show_vote(inter)


async def setup(bot: GeneralBotCore):
    await bot.add_cog(WerewolfGame(bot))
    bot.tree.add_command(
        WerewolfGame(bot),
        guild=Object(id=878265923709075486)
    )


def teardown(bot: GeneralBotCore):
    bot.tree.remove_command("werewwolf", guild=Object(id=878265923709075486))
    bot.tree.remove_command(
        WerewolfGame(bot),
        guild=Object(id=878265923709075486)
    )
    bot.remove_cog(WerewolfGame(bot))
