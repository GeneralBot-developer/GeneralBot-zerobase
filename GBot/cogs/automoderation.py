import discord
from discord.ext.commands import Cog, command, Context, has_guild_permissions, group
import asyncio
from GBot.CRUD.guild import Guild


class moderation(Cog):

    def __init__(self, bot):
        self.bot = bot

    @has_guild_permissions(kick_members=True)
    @command(name="kick", aliases=["k"], help="指定したユーザーをキックします")
    async def kick(self, ctx, user: discord.User, *, reason: str = None):
        await user.kick(reason=reason)
        await ctx.send(f"{user.name} をキックしました。")

    @has_guild_permissions(ban_members=True)
    @command(name="ban", aliases=["b"], help="指定したユーザーをバンします")
    async def ban(self, ctx, user: discord.User, *, reason: str = None):
        await user.ban(reason=reason)
        await ctx.send(f"{user.name} をバンしました。")

    @has_guild_permissions(ban_members=True)
    @command(name="unban", aliases=["ub"], help="指定したユーザーのバンを解除します")
    async def unban(self, ctx, user: discord.User, *, reason: str = None):
        await user.unban(reason=reason)
        await ctx.send(f"{user.name} を解除しました。")

    @has_guild_permissions(manage_messages=True)
    @command(name="purge", aliases=["p"], help="指定した数のメッセージを削除します")
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} 件のメッセージを削除しました。")

    @has_guild_permissions(administrator=True)
    @group(name="automoderation", aliases=["am"], help="自動モデレーションの設定を行います")
    async def automoderation(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @automoderation.command(name="setting",
                            aliases=["set"],
                            help="自動モデレーションを有効化、または無効化します")
    async def automoderation_setting(self, ctx, enable: bool):
        guild = await Guild(ctx.guild.id).get()
        if guild.automoderation == enable:
            if enable:
                await ctx.reply("既に有効化されています。")
            else:
                await ctx.reply("既に無効化されています。")
        await ctx.send(f"自動モデレーションを{'有効' if enable else '無効'}にしました。")

    @automoderation.command(name="ignore_channel",
                            aliases=["ignore"],
                            help="自動モデレーションを除外するチャンネルを設定します")
    async def automoderation_ignore_channel(self, ctx, channel: int):
        guild = await Guild(ctx.guild.id).get()
        if channel in guild.automoderation_ignore_channels:
            await ctx.reply("既に除外されています。")
        await ctx.send(f"{channel} を除外しました。")

    @automoderation.command(name="ignore_role",
                            aliases=["ignore"],
                            help="自動モデレーションを除外するロールを設定します")
    async def automoderation_ignore_role(self, ctx, role: int):
        guild = await Guild(ctx.guild.id).get()
        if role in guild.automoderation_ignore_roles:
            await ctx.reply("既に除外されています。")
        await ctx.send(f"{role} を除外しました。")

    @automoderation.command(name="ignore_user",
                            aliases=["ignore"],
                            help="自動モデレーションを除外するユーザーを設定します")
    async def automoderation_ignore_user(self, ctx, user: int):
        guild = await Guild(ctx.guild.id).get()
        if user in guild.automoderation_ignore_users:
            await ctx.reply("既に除外されています。")
        await ctx.send(f"{user} を除外しました。")

    @Cog.listener("on_message")
    async def delete_duplicate_message(self, message):
        if message.author.bot:
            return
        guild = await Guild(message.guild.id).get()
        if guild.automoderation:
            if message.channel.id in guild.automoderation_ignore_channels:
                return
            if message.author.id in guild.automoderation_ignore_users:
                return
            if message.author.id in guild.automoderation_ignore_roles:
                return
            async for msg in message.channel.history(
                    limit=guild.message_delete_limit):
                if msg.content == message.content:
                    await msg.delete()
                    await message.delete()


def setup(bot):
    bot.add_cog(moderation(bot))
