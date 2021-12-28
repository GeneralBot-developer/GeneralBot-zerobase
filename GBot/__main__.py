from GBot.core import GeneralBotCore
import os

GeneralBotCore(prefix="!", token=os.environ["BOT_TOKEN"], jishaku=True).run()
