import nextcord
from nextcord.ext.commands import Cog, command, Context
import asyncio


class automoderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def ban(self, ctx: Context, user):
        await ctx.guild.ban(user)
        await ctx.send(f"{user.mention}をBANしました")

    @command()
    async def kick(self, ctx: Context, user):
        await ctx.guild.kick(user)
        await ctx.send(f"{user.mention}をkickしました")

    @command()
    async def tempban(self, ctx: Context, user, time):
        await ctx.guild.ban(user, delete_message_days=0)
        await asyncio.sleep(int(time))
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention}を{time}秒後に自動でBANを解除しました")

    @Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return
        if message.content == "":
            return
        if message.author.id == self.bot.user.id:
            return
        if message.guild.id == self.bot.guild_id:
            if message.content == "":
                return
            async for msg in message.channel.history(limit=4):
                if msg.content == message.content:
                    await message.guild.ban(message.author)
                    await message.channel.send(
                        f"{message.author.mention}をBANしました"
                        )
                    break


def setup(bot):
    bot.add_cog(automoderation(bot))
