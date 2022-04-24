from discord.ext import commands
from typing import Union

DEBUG = False

char_dct = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."}

pos = 0


class IllegalExpressionException(Exception):
    """括弧が閉じられていない場合に呼ばれます。

    Args:
        Exception (Exception): 括弧が閉じられていない
    """
    pass


def myeval(line: str) -> float:
    """渡された式を計算して答えを返す

    Args:
        line (str): 計算式

    Returns:
        float: lineの式の答え
    """
    global pos
    pos = 0
    return expr(line.replace(" ", ""))


def expr(line: str) -> float:
    """渡された式を減算、または加算で計算して答えを返す。もしも乗算除算があれば先に計算する。

    Args:
        line (str): 計算式

    Returns:
        float: lineの和または差
    """
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


def term(line: str) -> float:
    """渡された式を乗算、または除算で計算して答えを返す。

    Args:
        line (str): 計算式

    Returns:
        float: lineの乗算または除算の答え
    """
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


def factor(line: str) -> float:
    """括弧内の式を計算します。

    Args:
        line (str): 計算式

    Raises:
        IllegalExpressionException: 括弧がとじられていない場合に発生

    Returns:
        float: 括弧内の式の答え
    """
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


def number(line: str) -> Union[int, float]:
    """渡された式にある数字がInt型かFloat型かを判定して返す。

    Args:
        line (str): 計算式

    Returns:
        Union[int, float]: 数字が整数であればInt型、小数であればFloat型を返す
    """
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


class Calculation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="calc",
        aliases=["calculate"],
        help="""<formula>に計算式を入れると計算します。\n例：calc 1+2*3=7\n""")
    async def calc(self, ctx, formula):
        try:
            await ctx.send(myeval(formula))
        except IllegalExpressionException:
            await ctx.send("括弧が閉じられていないです。")


async def setup(bot):
    return await bot.add_cog(Calculation(bot))
