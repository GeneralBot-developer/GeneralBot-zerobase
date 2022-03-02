from nextcord.ext import commands
from GBot.CRUD.bbs import BBS
from GBot.core.bot import team_id


class Bulletin_Board_System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="bbs", aliases=["b"], help="掲示板コマンド")
    async def bbs(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @bbs.command(name="create", aliases=["c"], help="掲示板を作ります。")
    async def bbs_create(self, ctx: commands.Context, title: str, content: str):
        channel = [].append(ctx.channel.id)
        created_bbs = await BBS.create(
            title=title,
            content=content,
            author=ctx.author.id,
            create_at=ctx.message.created_at,
            using_channels=channel
        )
        await ctx.reply(f"{created_bbs.title}を作成しました。")

    @bbs.command(name="delete", aliases=["d"], help="掲示板を削除します。")
    async def bbs_delete(self, ctx: commands.Context, title: str):
        bbs = await BBS.get(str)
        if not bbs:
            return await ctx.reply("掲示板が存在しません。")
        if bbs.author != ctx.author.id or ctx.author.id not in team_id or ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("掲示板を削除する権限がありません。")
        await BBS(title).delete()
        await ctx.reply("掲示板を削除しました。")

    @bbs.command(name="edit", aliases=["e"], help="掲示板を編集します。")
    async def bbs_edit(self, ctx: commands.Context, title: str, content: str):
        bbs = await BBS.get(str)
        if not bbs:
            return await ctx.reply("掲示板が存在しません。")
        if bbs.author != ctx.author.id or ctx.author.id not in team_id or ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("掲示板を編集する権限がありません。")
        await BBS(title).set(content=content)
        await ctx.reply("掲示板を編集しました。")

    @bbs.command(name="join", aliases=["j"], help="掲示板に参加します。")
    async def bbs_join(self, ctx: commands.Context, title: str):
        bbs = await BBS.get(str)
        if not bbs:
            return await ctx.reply("掲示板が存在しません。")
        if ctx.author.id in bbs.using_channels:
            return await ctx.reply("すでに参加しています。")
        await BBS(title).set(using_channels=ctx.author.id)
        await ctx.reply("参加しました。")

    @bbs.command(name="leave", aliases=["l"], help="掲示板から退出します。")
    async def bbs_leave(self, ctx: commands.Context, title: str):
        bbs = await BBS.get(str)
        if not bbs:
            return await ctx.reply("掲示板が存在しません。")
        if ctx.author.id not in bbs.using_channels:
            return await ctx.reply("参加していません。")
        await BBS(title).set(using_channels=ctx.author.id)
        await ctx.reply("退出しました。")

    @bbs.command(name="list", aliases=["l"], help="掲示板一覧を表示します。")
    async def bbs_list(self, ctx: commands.Context):
        bbs = await BBS.get_all()
        if not bbs:
            return await ctx.reply("掲示板が存在しません。")
        await ctx.reply(f"掲示板一覧\n{bbs}")

    @commands.Cog.listener("on_message")
    async def private_message_send(self, message):
        if message.author.bot:
            return
        bbs = await BBS.get_all()
        if not bbs:
            return
        for b in bbs:
            if message.channel.id in b.using_channels:
                await message.channel.send(f"{message.content}")


def setup(bot):
    bot.add_cog(Bulletin_Board_System(bot))
