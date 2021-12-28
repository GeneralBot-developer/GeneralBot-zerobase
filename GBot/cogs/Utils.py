from nextcord.ext.commands import Cog, command, is_owner, group
import os
import sys


class BotUtility(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def ping(self, ctx):
        async with ctx.typing():
            await ctx.reply(f"Pong! {round(self.bot.latency * 1000)}ms.")

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
