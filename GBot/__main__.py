from GBot.core import GeneralBotCore
import os

bot = GeneralBotCore(prefix="!", token=os.environ["BOT_TOKEN"], jishaku=True)
bot.owner_ids = [484655503675228171, 693025129806037003, 898929156048441386]
bot.run()
