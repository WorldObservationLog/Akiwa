import asyncio

from beanie import init_beanie
from bilibili_api.live import LiveRoom
from creart import it, AbstractCreator, CreateTargetInfo, exists_module
from graia.broadcast import Broadcast
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import Config
from src.database.models import Danmu, Live
from src.events import DanmuReceivedEvent
from src.utils import convert_danmu

config = it(Config).config
bcc = it(Broadcast)
loop = asyncio.get_event_loop()


class Database:
    _client = AsyncIOMotorClient(config.conn_str)

    def __init__(self):
        loop.run_until_complete(init_beanie(database=self._client[config.database_name],
                                            document_models=[Danmu, Live]))

    async def add_danmu(self, danmu: DanmuReceivedEvent):
        await convert_danmu(danmu).insert()

    async def get_danmu(self, live: Live):
        return await Danmu.find_many(
            Danmu.room_id == live.room_id,
            Danmu.timestamp >= live.start_time,
            Danmu.timestamp <= live.end_time).to_list()

    async def add_live(self, live: Live):
        if not await self.if_same_live(live.room_id, live.start_time):
            await live.insert()

    async def get_latest_live(self, room_id: int):
        return await Live.find_many(Live.room_id == room_id).sort(-Live.start_time).first_or_none()

    async def update_live(self, live: Live):
        await live.replace()

    async def if_same_live(self, room_id: int, timestamp: int):
        room_info = await LiveRoom(room_id).get_room_info()
        latest_live = await self.get_latest_live(room_id)
        if latest_live:
            if latest_live.title == room_info["room_info"]["title"] and timestamp - latest_live.start_time < 43200:
                return True
        return False


class DatabaseCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.database.database", "Database"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.database.database")

    @staticmethod
    def create(create_type: type[Database]) -> Database:
        return create_type()
