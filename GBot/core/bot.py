from nextcord.ext.commands import Bot
from logging import getLogger, basicConfig, INFO


class GeneralBotCore(Bot):
    def __init__(self, token):
        self.token = token
        super().__init__(command_prefix=None)
        self.LOG = getLogger(__name__)
        basicConfig(level=INFO)

    async def on_ready(self):
        self.LOG.INFO(f"Logger in {self.name}")

    def run(self):
        self.start(self.token)
