import os
import sys

from GBot.models.guild import Guild

from nextcord.ext.commands import (
    Cog, command, group,
    has_permissions, is_owner, Context
)
from nextcord.ext.commands.errors import (
    MissingPermissions,
    MissingRequiredArgument
)


class BotUtility(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def ping(self, ctx):
        async with ctx.typing():
            await ctx.reply(f"Pong! {round(self.bot.latency * 1000)}ms.")

    @command()
    @has_permissions(administrator=True)
    async def prefix(self, ctx: Context, *, prefix: str):
        if len(prefix) > 8:
            return await ctx.reply("prefixは8文字以内で設定してください。")
        guild = Guild(ctx.guild.id).get()
        Guild(ctx.guild.id).set(prefix=prefix)
        await ctx.reply(f"{guild.prefix}から{prefix}に変更しました。")

    @prefix.error
    async def on_prefix_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            return await ctx.send('管理者のみが実行可能です')
        if isinstance(error, MissingRequiredArgument):
            return await ctx.send('引数は新しいPrefixを8文字以内で渡してください')
        raise error

    @is_owner()
    @group()
    async def moding(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @moding.command()
    @is_owner()
    async def reboot(self, ctx):
        await ctx.reply("rebooting...")
        python = sys.executable
        os.execl(
            python,
            python,
            *sys.argv
        )


def setup(bot):
    bot.add_cog(BotUtility(bot))
