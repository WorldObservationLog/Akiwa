from beanie import init_beanie
from creart import it, AbstractCreator, CreateTargetInfo, exists_module
from graia.broadcast import Broadcast
from motor.motor_asyncio import AsyncIOMotorClient
from bilibili_api.live import LiveRoom

from src.config import Config
from src.events import DanmuReceivedEvent, HeartbeatReceivedEvent
from src.utils import convert_danmu
from .models import Danmu, Heartbeat, Live

config = it(Config).config
bcc = it(Broadcast)


class Database:
    _client = AsyncIOMotorClient(config.conn_str)

    def __init__(self):
        bcc.loop.run_until_complete(init_beanie(database=self._client[config.database_name],
                                                document_models=[Danmu, Heartbeat, Live]))

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

    async def add_heartbeat(self, heartbeat: HeartbeatReceivedEvent):
        await Heartbeat.parse_obj(heartbeat.dict()).insert()

    async def get_heartbeat(self, live: Live):
        return await Heartbeat.find_many(Heartbeat.room_id == live.room_id,
                                         Heartbeat.timestamp >= live.start_time,
                                         Heartbeat.timestamp <= live.end_time).to_list()

    async def if_same_live(self, room_id: int, timestamp: int):
        room_info = await LiveRoom(room_id).get_room_info()
        latest_live = await self.get_latest_live(room_id)
        if latest_live:
            if latest_live.title == room_info["room_info"]["title"] and timestamp - latest_live.start_time < 900:
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
