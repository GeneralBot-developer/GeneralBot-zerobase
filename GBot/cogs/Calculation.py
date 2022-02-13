from nextcord.ext import commands

from lark import Lark
from lark import Transformer
import aiofile
from functools import reduce

DEBUG = False

char_dct = {
    "1", "2", "3", "4", "5",
    "6", "7", "8", "9", "0",
    "."
}

pos = 0


class IllegalExpressionException(Exception):
    pass


def myeval(line):
    global pos
    pos = 0
    return expr(line.replace(" ", ""))


def expr(line):
    global pos
    v = term(line)
    while pos < len(line) and (line[pos] == "+" or line[pos] == "-"):
        op = line[pos]
        pos += 1
        if op == "+":
            v = v + term(line)
        elif op == "-":
            v = v - term(line)
    return v


def term(line):
    global pos
    v = factor(line)
    while pos < len(line) and (line[pos] == "*" or line[pos] == "/"):
        op = line[pos]
        pos += 1
        if op == "*":
            v = v * factor(line)
        elif op == "/":
            v = v / factor(line)
    return v


def factor(line):
    global pos
    v = None
    if line[pos] == "(":
        pos += 1
        v = expr(line)
        if pos == len(line) or line[pos] != ")":
            raise IllegalExpressionException()
        pos += 1
    else:
        v = number(line)
    return v


def number(line):
    global pos
    tmp = ""
    is_float = False
    while pos < len(line) and line[pos] in char_dct:
        if line[pos] == ".":
            is_float = True
        tmp += line[pos]
        pos += 1
    if is_float:
        return float(tmp)
    else:
        return int(tmp)


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

    @commands.command(name="calc", aliases=["calcuration"])
    async def calcuration(self, ctx, *, formula: str):
        result = myeval(formula)
        await ctx.send(f"{formula} = {result}")


def setup(bot):
    bot.add_cog(Four_Arithmetic_Operations(bot))
