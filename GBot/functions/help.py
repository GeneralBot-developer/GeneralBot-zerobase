from nextcord.ext import commands
import nextcord
import Levenshtein


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                "hidden": True
            }
        )

    async def send_bot_help(self, mapping):
        embed = nextcord.Embed(title="コマンド一覧", description=" ", color=0x00ff00)
        for cog in mapping:
            if isinstance(cog, commands.Cog):
                embed.add_field(
                    name=cog.qualified_name,
                    value="\n".join(
                        [
                            f"```{command.name} - {command.short_doc}```"
                            for command in cog.get_commands()
                            ]
                    ),
                    inline=False
                )
            elif cog is None:
                pass
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = nextcord.Embed(
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
        embed = nextcord.Embed(
            title=f"`{self.get_command_signature(command)}`の使い方",
            description=f"{command.help}",
            color=0x00ff00
            )
        await self.get_destination().send(embed=embed)

    def get_commands(self):
        return self.context.bot.commands

    async def command_not_found(self, string):
        embed = nextcord.Embed(
            title="コマンドが見つかりませんでした。",
            description=f"{string}",
            color=0xff0000
            )
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
            value="\n".join([f"`{command}`" for command in command_list])
            )
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = nextcord.Embed(
            title=f"{group.qualified_name}のサブコマンド",
            description=" ",
            color=0x00ff00
            )
        for command in group.commands:
            embed.add_field(
                name=command.name,
                value=command.short_doc
            )
        await self.get_destination().send(embed=embed)
