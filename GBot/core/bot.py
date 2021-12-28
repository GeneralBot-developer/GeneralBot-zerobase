from nextcord.ext.commands import Bot
from logging import getLogger, basicConfig, INFO
import nextcord
import traceback

basicConfig(level=INFO)
LOG = getLogger(__name__)


class GeneralBotCore(Bot):
    def __init__(self, *, prefix, token, jishaku=True):
        self.token = token
        super().__init__(command_prefix=prefix)
        if jishaku:
            super().load_extension("jishaku")

    async def on_ready(self):
        LOG.info(f"Logger in {self.user}")

    # 起動用の補助関数です
    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.token))
        except nextcord.LoginFailure:
            print("Discord Tokenが不正です")
        except KeyboardInterrupt:
            print("終了します")
            self.loop.run_until_complete(self.logout())
        except Exception:
            traceback.print_exc()
