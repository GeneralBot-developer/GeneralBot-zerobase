import os
import sys

from GBot.CRUD.guild import Guild
import discord
from discord import app_commands, Object, Interaction, ui

from discord.ext.commands import (
    Cog, command, group,
    has_permissions, is_owner, Context
)
from discord.ext.commands.errors import (
    MissingPermissions,
    MissingRequiredArgument)
from GBot.core import GeneralBotCore


class BotUtility(Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot

    @command(help="ping値を取得します。")
    async def ping(self, ctx):
        async with ctx.typing():
            await ctx.reply(f"Pong! {round(self.bot.latency * 1000)}ms.")

    @command(ignore_extra=False, help="prefixを変更します。")
    @has_permissions(administrator=True)
    async def prefix(self, ctx: Context, *, prefix: str):
        if len(prefix) > 8:
            return await ctx.send("Prefixは8文字以内である必要があります")
        guild = await Guild(ctx.guild.id).get()
        await Guild(ctx.guild.id).set(prefix=prefix)
        await ctx.send(f"Prefixを{guild.prefix}から{prefix}に変更しました")

    @prefix.error
    async def on_prefix_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            return await ctx.send('管理者のみが実行可能です')
        if isinstance(error, MissingRequiredArgument):
            return await ctx.send('引数は新しいPrefixを8文字以内で渡してください')
        raise error

    @is_owner()
    @group(aliases=["mod", "dev", "develop"], help="開発者コマンド")
    async def moderation(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @is_owner()
    @moderation.command(help="botを再起動します。")
    async def restart(self, ctx):
        await ctx.send("Restarting...")
        python = sys.executable
        os.execl(python, python, *sys.argv)


class PrefixModal(ui.Modal, title="Prefixを変更"):
    prefix = ui.TextInput(label="新しいPrefix名", default="g!", max_length=8, required=True)

    async def on_submit(self, inter: discord.Interaction):
        if str(inter.guild.owner.id) == str(inter.user.id):
            guild = await Guild(inter.guild.id).get()
            await Guild(inter.guild.id).set(prefix=str(self.prefix))
            await inter.response.send_message(f"Prefixを{guild.prefix}から{self.prefix}に変更しました")
        else:
            await inter.response.send_message("管理者のみが実行可能です")


class Test_Button(discord.ui.Button):
    def __init__(self, bot: GeneralBotCore):
        super().__init__(label="Ping!")
        self.bot = bot

    async def callback(self, inter: discord.Interaction):
        await inter.response.edit_message(content=f"Pong! {round(self.bot.latency * 1000)}ms.", view=None)


class Test_View(discord.ui.View):
    def __init__(self, item):
        super().__init__()
        self.add_item(item)


class Slash_Command_BotUtils(Cog, app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="utils", description="Botに関する設定")
        self.bot = bot

    @app_commands.command(name="prefix", description="prefixを変更します")
    async def slash_change_prefix(self, inter: Interaction):
        modal = PrefixModal()
        await inter.response.send_modal(modal)

    @app_commands.command(name="ping", description="ping値を取得します")
    async def slash_ping(self, inter: Interaction):
        await inter.response.send_message(view=Test_View(Test_Button(self.bot)))


async def setup(bot: GeneralBotCore):
    await bot.add_cog(BotUtility(bot))
    await bot.add_cog(Slash_Command_BotUtils(bot))
    bot.tree.add_command(
        Slash_Command_BotUtils(bot),
        guild=Object(id=878265923709075486)
    )
