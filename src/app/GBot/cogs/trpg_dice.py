from discord.ext import commands
import random


class Dice_Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="dice", aliases=["d"])
    async def dice(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("引数が不足しています。\n サブコマンドなどをお間違えではありませんか？")

    @dice.command(name="roll", aliases=["r"])
    async def dice_roll(self, ctx: commands.Context, *args):
        """
        ダイスを振る
        """
        print(*args)
        if len(args) == 2:
            pass
        else:
            args = "\n".join(args).split("D")
        result: int = 0
        for _ in range(int(args[0])):
            result += random.randint(1, int(args[1]))
        formura = f"{args[0]}D{args[1]}"
        await ctx.send(f"{formura} = {result}")


def setup(bot):
    return bot.add_cog(Dice_Roll(bot))
