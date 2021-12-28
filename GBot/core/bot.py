from nextcord.ext.commands import Bot
from logging import getLogger, basicConfig, INFO
import nextcord
import traceback

class GeneralBotCore(Bot):
    def __init__(self, token):
        self.token = token
        super().__init__(command_prefix=None)
        self.LOG = getLogger(__name__)
        basicConfig(level=INFO)

    async def on_ready(self):
        self.LOG.INFO(f"Logger in {self.name}")

    # 起動用の補助関数です
    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.token))
        except nextcord.LoginFailure:
            print("Discord Tokenが不正です")
        except KeyboardInterrupt:
            print("終了します")
            self.loop.run_until_complete(self.logout())
        except:
            traceback.print_exc()
