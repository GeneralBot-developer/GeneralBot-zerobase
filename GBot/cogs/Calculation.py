import nextcord
from nextcord.ext import commands


class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
