from nextcord.ext.commands import Cog, group, Context
from GBot.core import GeneralBotCore
import json
import aiofile
import nextcord
import asyncio


class RoleKeep(Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot
        self.json_path = "GBot/data/role_keep.json"

    @Cog.listener()
    async def on_member_leave(self, member: nextcord.Member):
        remove_role = member.guild.get_role(member.guild.id)
        roles = []
        for role in member.roles:
            print(role)
            if role == remove_role:
                pass
            roles.append(role.id)
        convert_roles = json.dumps(roles)
        async with aiofile.async_open(self.json_path, mode="r") as f:
            content = await f.read()
        content = json.loads(content)
        content[member.guild.id] = {
            member.id: convert_roles
        }
        async with aiofile.async_open(self.json_path, mode="w") as f:
            await f.write(json.dumps(content, indent=4))

    @Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        async with aiofile.async_open(self.json_path, mode="r") as f:
            content = await f.read()
        content = json.loads(content)
        member_check = member.id in content.get(member.guild.id)
        if member_check is None:
            return
        member_role = content[member.guild.id][member.id]
        for role_id in member_role:
            role = member.guild.get_role(role_id)
            await member.add_roles(role)
            asyncio.sleep(1)

    @group(aliases=["rk, role"])
    async def role_keeper(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @role_keeper.command()
    async def save(self, ctx: Context):
        remove_role = ctx.guild.get_role(ctx.guild.id)
        roles = []
        for role in ctx.author.roles:
            print(role)
            if role == remove_role:
                pass
            roles.append(role.id)
        convert_roles = json.dumps(roles)
        async with aiofile.async_open(self.json_path, mode="r") as f:
            content = await f.read()
        content = json.loads(content)
        content[ctx.guild.id] = {
            ctx.author.id: convert_roles
        }
        async with aiofile.async_open(self.json_path, mode="w") as f:
            await f.write(json.dumps(content, indent=4))
        await ctx.reply("Ok")


def setup(bot: GeneralBotCore):
    bot.add_cog(RoleKeep(bot))
