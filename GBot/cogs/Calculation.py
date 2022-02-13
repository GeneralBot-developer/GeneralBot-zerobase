from nextcord.ext import commands

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


class Calculation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="calc", aliases=["calculate"])
    async def calc(self, ctx, formula):
        try:
            await ctx.send(myeval(formula))
        except IllegalExpressionException:
            await ctx.send("Illegal expression")


def setup(bot):
    bot.add_cog(Calculation(bot))
