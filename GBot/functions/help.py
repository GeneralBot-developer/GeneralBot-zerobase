from discord.ext import commands
from discord.ext.commands import Command, Cog
import discord
import Levenshtein
from typing import List, Optional, Dict


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"hidden": True})

    async def send_bot_help(self, mapping: Dict[Optional[Cog], List[Command]]):
        embed = discord.Embed(
            title="GBotのコマンド一覧",
            description=" ",
            color=0x00ff00
        )
        for cog, command in mapping.items():
            if cog is None:
                continue
            if len(command) == 0:
                continue
            for command in command:
                embed.add_field(
                    name=cog.qualified_name,
                    value="\n".join(
                        [
                            f"```{command.name}```-```{command.short_doc}```" if command.short_doc else "None" for command in cog.get_commands()
                        ]
                    ),
                    inline=False
                )
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"{cog.qualified_name}のコマンド一覧",
            description=" ",
            color=0x00ff00
        )

        for command in cog.get_commands():
            embed.add_field(
                name=command.name,
                value=f"{command.help}",
            )
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"`{self.get_command_signature(command)}`の使い方",
            description=f"{command.help}",
            color=0x00ff00)
        await self.get_destination().send(embed=embed)

    def get_commands(self):
        return self.context.bot.commands

    async def command_not_found(self, string):
        embed = discord.Embed(
            title="コマンドが見つかりませんでした。",
            description=f"{string}",
            color=0xff0000)
        command_list = []
        cmds = self.get_commands()
        for command in cmds:
            if Levenshtein.ratio(command.name, string) > 0.5:
                command_list.append(command.name)
            else:
                pass
        if len(command_list) == 0:
            command_list.append("見つかりませんでした")
        embed.add_field(
            name="もしかして：",
            value="\n".join(
                [f"`{command}`" for command in command_list]
            )
        )
        return embed

    async def send_error_message(self, error):
        await self.get_destination().send(embed=error)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=f"{group.qualified_name}のサブコマンド",
            description=" ",
            color=0x00ff00
        )
        for command in group.commands:
            embed.add_field(
                name=command.name,
                value=[
                    command.short_doc
                    if not command.short_doc else "None"
                ]
            )
        await self.get_destination().send(embed=embed)
