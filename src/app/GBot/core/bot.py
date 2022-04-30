from logging import INFO, basicConfig, getLogger
from typing import Dict, Set
from GBot.data.voice import VoiceState
import Levenshtein
import traceback

from GBot.CRUD.guild import Guild
from GBot.functions.help import HelpCommand

import discord
from discord.ext.commands import Bot
from discord.ext.commands.errors import MissingPermissions, CommandNotFound, NotOwner

basicConfig(level=INFO)
LOG = getLogger(__name__)

team_id = [
    757106917947605034, 705264675138568192, 743455582517854239,
    910588052102086728, 484655503675228171
]


class GeneralBotCore(Bot):

    def __init__(self, *, prefix, token, intents, jishaku=True):
        super().__init__(
            command_prefix=prefix,
            help_command=HelpCommand(),
            intents=intents
        )
        self.jishaku = jishaku
        self.voice = {}
        self.voice: Dict[int, Set[VoiceState]]
        self.token = token

    async def is_owner(self, user: discord.User):
        if user.id in team_id:
            return True
        return await super().is_owner(user)

    async def load_cogs(self):
        cog_files = [
            "Utils", "RoleKeeper", "screenshot", "music.__init__",
            "Calculation", "tts", "virtual_money", "crypto", "auth",
            "wolf.__init__", "trpg_dice", "vc_recoder.__init__"
        ]
        for cog in cog_files:
            await super().load_extension(
                f"GBot.cogs.{cog[:-3] if cog.endswith('.py') else cog}"
            )
            LOG.info(f"{cog}のロード完了。")
        if self.jishaku:
            await super().load_extension("jishaku")
        LOG.info("全ファイルが正常に読み込まれました。")

    async def on_ready(self):
        LOG.info(f"Logger in {self.user}")
        print(self.guilds)
        for guild in self.guilds:
            self.voice[guild.id] = VoiceState.NOT_PLAYED
        print(self.voice)
        await self.tree.sync(guild=discord.Object(id=878265923709075486))

    async def get_prefix(self, message: discord.Message):
        guild = await Guild(message.guild.id).get()
        if message.guild.id == 878265923709075486:
            if self.user.id == 950745689749602364:
                print(f"サーバー:{message.guild.name}")
                print("接頭文字:gc!")
                return "gc!"
        if guild:
            print(f"サーバー:{message.guild.name}")
            print(f"接頭文字:{guild.prefix}")
            return guild.prefix
        else:
            LOG.info("該当するサーバーがなかったので新たに作成します。")
            guild = await Guild.create(
                id=message.guild.id,
                auth=False
            )
            guild = await guild.get()
            print(f"サーバー:{message.guild.name}")
            print(f"接頭文字:{guild.prefix}")
            return guild.prefix

    @staticmethod
    async def prefix(self, message: discord.Message):
        guild = await Guild(message.guild.id).get()
        if guild:
            if guild.id == 878265923709075486:
                if self.user.id == 950745689749602364:
                    print(f"サーバー:{message.guild.name}")
                    print("接頭文字:gc!")
                    return "gc!"
                else:
                    print(f"サーバー:{message.guild.name}")
                    print(f"接頭文字:{guild.prefix}")
                    return guild.prefix
            else:
                print(f"サーバー:{message.guild.name}")
                print(f"接頭文字:{guild.prefix}")
                return guild.prefix
        else:
            LOG.info("該当するサーバーがなかったので新たに作成します。")
            guild = await Guild.create(message.guild.id)
            guild = await guild.get()
            print(f"サーバー:{message.guild.name}")
            print(f"接頭文字:{guild.prefix}")
            return guild.prefix

    async def on_guild_join(self, guild: discord.Guild):
        db_guild = await Guild.create(guild.id)
        db_guild = await db_guild.get()
        self.voice[guild.id] = VoiceState.NOT_PLAYED
        print(f"サーバー:{guild.name}")
        print(f"接頭文字:{db_guild.prefix}")

    async def on_command_error(self, ctx, error):
        embed = discord.Embed(color=0xff0000)
        if isinstance(error, MissingPermissions):
            embed.title = "ERROR: Missing Permissions"
            embed.description = "このコマンドを実行するための権限がありません。"
            return await ctx.reply(embed=embed, )
        elif isinstance(error, CommandNotFound):
            command_list = []
            cmds = self.commands
            for command in cmds:
                if Levenshtein.ratio(command.name, ctx.message.content) > 0.5:
                    command_list.append(command.name)
            else:
                pass
            if len(command_list) == 0:
                command_list.append("見つかりませんでした")
            embed.add_field(name="もしかして：",
                            value="\n".join(
                                [f"`{command}`" for command in command_list]))
            embed.title = "ERROR：NotCommandFound."
            embed.description = "コマンドが見つかりませんでした。"
            return await ctx.reply(embed=embed)
        elif isinstance(error, NotOwner):
            return await ctx.reply("このコマンドは管理者のみ実行できます。")
        else:
            embed.title = "ERROR: Unknown Error"
            embed.description = "```{0}```".format("".join(
                traceback.TracebackException.from_exception(error).format()))
            await ctx.reply(embed=embed)

    async def run(self):
        try:
            await self.start(self.token)
        except discord.LoginFailure:
            print("Discord Tokenが不正です")
        except KeyboardInterrupt:
            LOG.error("終了します")
            await self.close()
        else:
            traceback.print_exc()
