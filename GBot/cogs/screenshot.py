from nextcord.ext.commands import Cog, command, Context
from GBot.core import GeneralBotCore
from nextcord import File
from pyppeteer import launch


class ScreenShot(Cog):
    def __init__(self, bot: GeneralBotCore):
        self.bot = bot

    async def get_ss(self, url: str):
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        await page.goto(url)
        await page.setViewport({'width': 800, 'height': 1000})
        await page.screenshot(path='./GBot/data/screenshot.png')
        await browser.close()

    @command(help="スクリーンショットを取得します。")
    async def ss(self, ctx: Context, url):
        async with ctx.typing():
            await self.get_ss(url)
        await ctx.send(file=File("GBot/data/screenshot.png"))


def setup(bot):
    return bot.add_cog(ScreenShot(bot))
