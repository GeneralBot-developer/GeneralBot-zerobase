from nextcord.ext.commands import Cog, command


class BotUtility(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def ping(self, ctx):
        async with ctx.typing():
            await ctx.reply(f"Pong! {round(self.bot.latency * 1000)}ms.")

    def setup(bot):
        bot.add_cog(BotUtility(bot))
