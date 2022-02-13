from logging import INFO, basicConfig, getLogger

import sys

from GBot.CRUD.guild import Guild
from sanic import Sanic
from sanic.response import text
sys.path.append(r"c:\users\kou\.virtualenvs\generalbot-zerobase-k-5rsmb3\lib\site-packages")
import nextcord
from nextcord.ext.commands import Bot
basicConfig(level=INFO)
LOG = getLogger(__name__)

team_id = [
    757106917947605034,
    705264675138568192,
    743455582517854239,
    910588052102086728,
    484655503675228171
    ]

class GeneralBotCore(Bot):
    def __init__(self, *, prefix, token, jishaku=True, sanic=False, _intents):
        super().__init__(command_prefix=None)
        self.token = token
        self.prefix = prefix
        self.jishaku = jishaku
        self._intents = _intents
        self.sanic = sanic
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

    async def keep_alive(self, request):
        return text("Bot is alive")

    async def is_owner(self, user: nextcord.User):
        if user.id in team_id:
            return True
        return await super().is_owner(user)

    def load_cogs(self):
        cog_files = [
            "Utils",
            "RoleKeeper",
            "screenshot",
            "music_player",
            "Calculation"
            ]
        for cog in cog_files:
            super().load_extension(f"GBot.cogs.{cog}")
            LOG.info(f"{cog}のロード完了。")
        LOG.info("全ファイルが正常に読み込まれました。")

    async def on_ready(self):
        LOG.info(f"Logger in {self.user}")

    async def get_prefix(self, message: nextcord.Message):
        guild = await Guild(message.guild.id).get()
        if guild:
            if guild.id == 878265923709075486:
                if self.user.id == 484655503675228171:
                    print(f"サーバー:{message.guild.name}")
                    print(f"接頭文字:{guild.prefix}")
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

    async def on_guild_join(self, guild: nextcord.Guild):
        db_guild = await Guild.create(guild.id)
        db_guild = await guild.get()
        print(f"サーバー:{guild.name}")
        print(f"接頭文字:{db_guild.prefix}")

    # 起動用の補助関数です
    async def setup_discordbot(self, app, loop):
        super().__init__(
            command_prefix=self.prefix,
            intents=self._intents,
            loop=loop
            )
        if self.jishaku:
            super().load_extension("jishaku")
        self.load_cogs()
        loop.create_task(self.start(self.token))

    async def setout_discordbot(self, app, loop):
        await self.close()

    def run(self, *args, **kwargs):
        if self.sanic:
            self.app.run(*args, **kwargs)
        else:
            self.loop.run_until_complete(self.start(self.token))
