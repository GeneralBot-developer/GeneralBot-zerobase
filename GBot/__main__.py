import os
from dotenv import load_dotenv
from GBot.core import GeneralBotCore
import discord
import sentry_sdk
import asyncio

load_dotenv()
sentry_sdk.init(os.environ["SENTRY_DSN"], traces_sample_rate=1.0)

bot = GeneralBotCore(
    prefix=None,
    token=os.environ["BOT_TOKEN"],
    intents=discord.Intents.all(),
    jishaku=True,
)


async def main():
    async with bot:
        await bot.load_cogs()
        await bot.run()

asyncio.run(main())
