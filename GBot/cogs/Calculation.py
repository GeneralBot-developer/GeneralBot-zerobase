import nextcord
from nextcord.ext import commands

import sys
from lark import Lark
from lark import Transformer
from functools import reduce


class CalcTransformer(Transformer):
    def expr(self, tree):
        return reduce(lambda x, y: x + y, tree)

    def term(self, tree):
        return reduce(lambda x, y: x * y, tree)

    def factor(self, tree):
        return tree[0]

    def number(self, tree):
        return int(tree[0])


class Four_Arithmetic_Operations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def calc_num(self, formula: str):
        with open("./data/calcuration.lark", encoding="utf-8") as grammar:
            parser = Lark(grammar.read(), start="expr")
            tree = parser.parse(formula)
            result = CalcTransformer().transform(tree)
            return result

    @commands.command(name="calc", aliases=["calcuration"])
    async def calcuration(self, ctx, *, formula: str):
        result = await self.calc_num(formula)
        await ctx.send(f"{formula} = {result}")


def setup(bot):
    bot.add_cog(Four_Arithmetic_Operations(bot))
