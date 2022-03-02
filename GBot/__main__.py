import os
from dotenv import load_dotenv
from GBot.core import GeneralBotCore
import nextcord
import sentry_sdk


load_dotenv()
sentry_sdk.init(
    os.environ["SENTRY_DSN"],
    traces_sample_rate=1.0
)

bot = GeneralBotCore(
    prefix=None,
    token=os.environ["BOT_TOKEN"],
    onami=True,
    _intents=nextcord.Intents.all()
)

bot.run()
