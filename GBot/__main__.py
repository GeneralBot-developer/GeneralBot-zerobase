import os
from dotenv import load_dotenv
from GBot.core import GeneralBotCore
import nextcord

load_dotenv()
bot = GeneralBotCore(
    prefix=None,
    token=os.environ["BOT_TOKEN"],
    jishaku=True,
    _intents=nextcord.Intents.all(),
    sanic=True
)
bot.owner_ids = [484655503675228171, 693025129806037003, 898929156048441386]
bot.run(host='0.0.0.0', port=8080)
