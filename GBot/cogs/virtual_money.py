from discord.ext import commands
from GBot.CRUD.virtual import VirtualMoney
from discord.ext.commands import Context
import discord
from sqlalchemy.orm.attributes import flag_modified
from GBot.models.model import VirtualMoney as VM


class VMoney(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="virtual", aliases=["v"], help="サーバー独自の通貨を作ります。")
    async def virtualmoney(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @virtualmoney.command(name="add", aliases=["a"], help="特定のユーザーに通貨を追加します。")
    async def virtualmoney_add(self, ctx, member: discord.Member, amount: int):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            await ctx.reply("仮想通貨が作成されていません。")
            return
        vmoney.members[str(member.id)] += amount
        q = VM.select().where(ctx.guild.id == VM.c.id)
        flag_modified(q, "members")
        await VirtualMoney(ctx.guild.id).set(members=vmoney.members)

    @virtualmoney.command(name="create", aliases=["c"], help="仮想通貨を作成します。")
    async def create(self, ctx: Context, unit):
        if await VirtualMoney(ctx.guild.id).get():
            return await ctx.reply("既に仮想通貨が存在します。")
        new_members = {}
        for member in ctx.guild.members:
            new_members[int(member.id)] = 0
        await VirtualMoney.create(id=ctx.guild.id,
                                  unit=unit,
                                  members=new_members)
        await ctx.reply(f"1000{unit}作成しました。")

    @virtualmoney.command(name="get", aliases=["g"], help="所持金額を取得します。")
    async def get(self, ctx, user: discord.Member = None):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if user is None:
            amount = vmoney.members[str(ctx.author.id)]
            await ctx.reply("あなたの所持額は" + str(amount) + vmoney.unit + "です。")
        else:
            amount = vmoney.members[str(user.id)]
            await ctx.reply(f"{user.name}の所持額は{amount}{vmoney.unit}です。")

    @virtualmoney.command(name="delete", aliases=["d"], help="仮想通貨を削除します。")
    async def delete(self, ctx):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        await VirtualMoney(ctx.guild.id).delete()
        await ctx.reply("仮想通貨を削除しました。")

    @virtualmoney.command(name="list", aliases=["l"], help="仮想通貨を一覧表示します。")
    async def list(self, ctx):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        embed = discord.Embed(
            title=f"{vmoney.unit}一覧",
            description=" ",
        )
        print(vmoney.members)
        for member in ctx.guild.members:
            embed.add_field(
                name="{}".format(member.name),
                value="{}".format(vmoney.members[str(member.id)]),
            )
        await ctx.reply(embed=embed)

    @virtualmoney.command(name="hand_over",
                          aliases=["ho"],
                          help="仮想通貨を他のユーザーに渡します。")
    async def hand_over(self, ctx, user, amount):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        vmoney.members[str(user.id)] += amount
        vmoney.members[str(ctx.author.id)] -= amount
        await VirtualMoney(ctx.guild.id).set(members=vmoney.members)
        embed = discord.Embed(
            title="通貨の受け渡し",
            description=
            f"{ctx.author.name}さんから{user.name}さんに{amount}{vmoney.unit}を受け渡しました。",
        )
        await ctx.reply(embed=embed)

    @virtualmoney.command(name="store_create",
                          aliases=["sc"],
                          help="物品を販売できます")
    async def store_create(self, ctx, name, params: discord.Role, amount):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        vmoney.stores[name] = {params.name: amount}
        await VirtualMoney(ctx.guild.id).set(stores=vmoney.stores)
        await ctx.reply(f"{name}の店を作成しました。")

    @virtualmoney.command(name="store_list", aliases=["sl"], help="物品を一覧表示します")
    async def store_list(self, ctx):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        embed = discord.Embed(
            title="店一覧",
            description=" ",
        )
        for name in vmoney.stores:
            embed.add_field(
                name="{}".format(name),
                value="{}".format(vmoney.stores[name]),
            )
        await ctx.reply(embed=embed)

    @virtualmoney.command(name="store_delete", aliases=["sd"], help="物品を削除します")
    async def store_delete(self, ctx, name):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        del vmoney.stores[name]
        await VirtualMoney(ctx.guild.id).set(stores=vmoney.stores)
        await ctx.reply(f"{name}の店を削除しました。")

    @virtualmoney.command(name="buy", aliases=["b"], help="物品を購入します")
    async def buy(self, ctx, name, amount):
        vmoney = await VirtualMoney(ctx.guild.id).get()
        if not vmoney:
            return await ctx.reply("仮想通貨が作成されていません。")
        if name not in vmoney.stores:
            return await ctx.reply("店が存在しません。")
        if amount > vmoney.members[ctx.author.id]:
            return await ctx.reply("所持金が不足しています。")
        vmoney.members[str(ctx.author.id)] -= amount
        vmoney.stores[name][ctx.author.name] += amount
        await VirtualMoney(ctx.guild.id).set(members=vmoney.members,
                                             stores=vmoney.stores)
        embed = discord.Embed(
            title="購入",
            description=
            f"{ctx.author.name}さんが{name}の店に{amount}{vmoney.unit}を購入しました。",
        )
        await ctx.reply(embed=embed)


def setup(bot):
    return bot.add_cog(VMoney(bot))
