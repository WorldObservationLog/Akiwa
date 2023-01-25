from motor import motor_asyncio as motor
from creart import it, AbstractCreator, CreateTargetInfo, exists_module

from src.events import DanmuReceivedEvent
from src.types import Live
from .config import Config


class Database:
    _client = motor.AsyncIOMotorClient(it(Config).config.conn_str)
    _db = _client["eoe"]

    async def add_danmu(self, danmu: DanmuReceivedEvent):
        await self._db.danmu.insert_one(danmu.dict())

    async def get_danmu(self, command: str, room_id: int):
        pass

    async def add_live(self, live: Live):
        await self._db.live.insert_one(live.dict())
    
    async def get_latest_live(self, room_id: int):
        return await self._db.live.find({"room_id": {"$eq": room_id}}).sort("timestamp", -1).to_list(1)[0]





class DatabaseCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.database", "Database"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.database")

    @staticmethod
    def create(create_type: type[Database]) -> Database:
        return create_type()
