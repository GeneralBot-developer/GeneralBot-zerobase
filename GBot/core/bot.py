import traceback
from logging import INFO, basicConfig, getLogger

import sys
sys.path.append(r"c:\users\kou\.virtualenvs\generalbot-zerobase-k-5rsmb3\lib\site-packages")
import nextcord
from nextcord.ext.commands import Bot

from GBot.models.guild import Guild

basicConfig(level=INFO)
LOG = getLogger(__name__)


class GeneralBotCore(Bot):
    def __init__(self, *, prefix, token, jishaku=True):
        intents = nextcord.Intents.default()
        intents.members = True
        self.token = token
        super().__init__(command_prefix=prefix)
        if jishaku:
            super().load_extension("jishaku")
        self.load_cogs()

    def load_cogs(self):
        cog_files = ["Utils"]
        for cog in cog_files:
            self.load_extension(f"GBot.cogs.{cog}")
            LOG.info(f"{cog}のロード完了。")
        LOG.info("全ファイルが正常に読み込まれました。")

    async def on_ready(self):
        LOG.info(f"Logger in {self.user}")

    async def get_prefix(self, message: nextcord.Message):
        guild = await Guild(message.guild.id).get()
        if guild:
            print("サーバー:", message.guild.name)
            print("接頭文字:", guild.prefix)
            return guild.prefix
        else:
            guild = await Guild.create(message.guild.id)
            guild = await guild.get()
            print("サーバー:", message.guild.name)
            print("接頭文字:", guild.prefix)
            return guild.prefix

    async def on_guild_join(self, guild: nextcord.Guild):
        guild = await Guild.create(guild.id)
        guild = await guild.get()
        print("サーバー:", guild.name)
        print("接頭文字:", guild.prefix)

    # 起動用の補助関数です
    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.token))
        except nextcord.LoginFailure:
            print("Discord Tokenが不正です")
        except KeyboardInterrupt:
            print("終了します")
            self.loop.run_until_complete(self.close())
        except Exception:
            traceback.print_exc()
