import cryptocode
from discord.ext import commands


class Crypt_string(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="encode", aliases=["enc", "encrypt"])
    async def crypt_str(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @crypt_str.command(name="encrypt", aliases=["enc"])
    async def encrypt(self, ctx, text, password):
        await ctx.send(f"```{cryptocode.encrypt(text, password)}```")

    @crypt_str.command(name="decrypt", aliases=["dec"])
    async def decrypt(self, ctx, text, password):
        await ctx.send(f"```{cryptocode.decrypt(text, password)}```")


def setup(bot):
    bot.add_cog(Crypt_string(bot))
