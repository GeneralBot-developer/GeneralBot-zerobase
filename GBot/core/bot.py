from logging import INFO, basicConfig, getLogger

import sys
sys.path.append(r"c:\users\kou\.virtualenvs\generalbot-zerobase-k-5rsmb3\lib\site-packages")
import nextcord
from nextcord.ext.commands import Bot

from GBot.models.guild import Guild
from sanic import Sanic
from sanic.response import text
import aiohttp
basicConfig(level=INFO)
LOG = getLogger(__name__)


class GeneralBotCore(Bot):
    def __init__(self, *, prefix, token, jishaku=True, sanic=False, intents):
        self.token = token
        self.sanic = sanic
        super().__init__(command_prefix=prefix, intents=intents)
        if jishaku:
            super().load_extension("jishaku")
        self.load_cogs()
        if sanic:
            self.app = Sanic(name="GeneralBot")
            self.app.register_listener(
                self.setup_discordbot,
                "main_process_start"
            )
            self.app.register_listener(
                self.setout_discordbot,
                "before_server_stop"
            )
            self.app.add_route(self.keep_alive, '/')
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'GeneralBot: kousakirai; aiohttp on Python 3.8.10;'
                    },
                skip_auto_headers=[
                    'User-Agent'
                    ],
                loop=self.loop
                )

    async def keep_alive(self, request):
        return text("Bot is alive")

    def load_cogs(self):
        cog_files = ["Utils", "RoleKeeper", "screenshot"]
        for cog in cog_files:
            self.load_extension(f"GBot.cogs.{cog}")
            LOG.info(f"{cog}のロード完了。")
        LOG.info("全ファイルが正常に読み込まれました。")

    async def on_ready(self):
        LOG.info(f"Logger in {self.user}")

    async def get_prefix(self, message: nextcord.Message):
        guild = await Guild(message.guild.id).get()
        if guild:
            if guild.id == 878265923709075486:
                print("サーバー:", guild.name)
                print("接頭文字:", guild.prefix)
                return "gc!"
            else:
                print("サーバー:", guild.name)
                print("接頭文字:", guild.prefix)
                return guild.prefix
        else:
            guild = await Guild.create(message.guild.id)
            guild = await guild.get()
            print("サーバー:", guild.name)
            print("接頭文字:", guild.prefix)

    async def on_guild_join(self, guild: nextcord.Guild):
        guild = await Guild.create(guild.id)
        guild = await guild.get()
        print("サーバー:", guild.name)
        print("接頭文字:", guild.prefix)

    # 起動用の補助関数です
    async def setup_discordbot(self, app, loop):
        loop.create_task(self.start(self.token))

    async def setout_discordbot(self, app, loop):
        await self.close()

    def run(self, *args, **kwargs):
        if self.sanic:
            self.app.run(*args, **kwargs)
        else:
            self.loop.run_until_complete(self.start(self.token))
