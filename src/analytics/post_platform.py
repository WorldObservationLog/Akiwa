from asyncio import AbstractEventLoop


class PostPlatform:
    async def post_report(self, target: str, report_url: str):
        raise NotImplemented


class Telegram(PostPlatform):
    def __init__(self, **kwargs):
        from telegram import Bot
        self.bot = Bot(token=kwargs["bot_token"])

    async def post_report(self, target: str, report_url: str):
        await self.bot.send_message(target, report_url)


POST_PLATFORM_MATCHES = {"telegram": Telegram}
