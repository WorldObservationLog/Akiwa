from creart import it, AbstractCreator, CreateTargetInfo, exists_module
from motor import motor_asyncio as motor

from src.events import DanmuReceivedEvent, HeartbeatReceivedEvent
from src.types import *
from .config import Config

DANMU_MATCHES = {"DANMU_MSG": DANMU_MSG,
                 "INTERACT_WORD": INTERACT_WORD,
                 "ENTRY_EFFECT": ENTRY_EFFECT,
                 "SEND_GIFT": SEND_GIFT,
                 "COMBO_SEND": COMBO_SEND,
                 "SUPER_CHAT_MESSAGE": SUPER_CHAT_MESSAGE,
                 "GUARD_BUY": GUARD_BUY}


class Database:
    _client = motor.AsyncIOMotorClient(it(Config).config.conn_str)
    _db = _client["eoe"]

    async def add_danmu(self, danmu: DanmuReceivedEvent):
        await self._db.danmu.insert_one(danmu.dict())

    async def get_danmu(self, live: Live) -> List[Danmu]:
        result = []
        danmus = await self._db.danmu.find({"$and": [
            {"$and": [{"timestamp": {"$gte": live.start_time}}, {"timestamp": {"$lte": live.end_time}}]},
            {"room_id": {"$eq": live.room_id}}]}).to_list()
        for danmu in danmus:
            if danmu["command"] in DANMU_MATCHES.keys():
                result.append(Danmu(room_id=danmu["room_id"],
                                    timestamp=danmu["timestamp"],
                                    command=danmu["command"],
                                    data=DANMU_MATCHES.get(danmu["command"]).parse_obj(danmu["data"])))
        return result

    async def add_live(self, live: Live):
        await self._db.live.insert_one(live.dict())

    async def get_latest_live(self, room_id: int):
        return await self._db.live.find({"room_id": {"$eq": room_id}}).sort("timestamp", -1).to_list(1)[0]

    async def add_heartbeat(self, heartbeat: HeartbeatReceivedEvent):
        await self._db.heartbeat.insert_one(heartbeat.dict())


class DatabaseCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.database", "Database"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.database")

    @staticmethod
    def create(create_type: type[Database]) -> Database:
        return create_type()
