import os
import sys

from GBot.CRUD.guild import Guild

from nextcord.ext.commands import (
    Cog, command, group,
    has_permissions, is_owner, Context
)
from nextcord.ext.commands.errors import (
    MissingPermissions,
    MissingRequiredArgument
)
from GBot.core import GeneralBotCore


class BotUtility(Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot

    @command()
    async def ping(self, ctx):
        async with ctx.typing():
            await ctx.reply(f"Pong! {round(self.bot.latency * 1000)}ms.")

    @command(ignore_extra=False)
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
    @group(aliases=["mod", "dev", "develop"])
    async def moderation(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @is_owner()
    @moderation.command()
    async def restart(self, ctx):
        await ctx.send("Restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)


def setup(bot):
    bot.add_cog(BotUtility(bot))
