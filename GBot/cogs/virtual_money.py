from nextcord.ext import commands
from GBot.CRUD.virtual import VirtualMoney


class VMoney(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="virtual", aliases=["v"])
    async def virtualmoney(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @virtualmoney.command(name="add", aliases=["a"])
    async def virtualmoney_add(self, ctx, user, amount):
        vmoney = VirtualMoney(ctx.author.id).get()
        if not vmoney:
            await ctx.reply("仮想通貨が作成されていません。")
            return
        vmoney.members[user.id] += amount
        await vmoney.set(members=vmoney.members)

    @virtualmoney.command(name="create", aliases=["c"])
    async def create(self, ctx, unit):
        if await VirtualMoney(ctx.author.id).get():
            return await ctx.reply("既に仮想通貨が存在します。")
        q = await VirtualMoney.create(id=ctx.guild.id, unit=unit)
        members = await q.get().members
        print(members)
        for member in ctx.guild.members:
            members[member.id] = 0
        print(members)
        await q.set(members)
        await ctx.reply(f"1000{unit}作成しました。")


def setup(bot):
    return bot.add_cog(VMoney(bot))
