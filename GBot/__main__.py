from GBot.core.bot import GeneralBotCore
import os

GeneralBotCore(prefix="!", token=os.environ["BOT_TOKEN"], jishaku=False).run()
