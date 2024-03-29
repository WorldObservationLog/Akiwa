from beanie import Document
from creart import AbstractCreator, CreateTargetInfo, exists_module
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

from src.database.models.live import Live
from src.events import DanmuReceivedEvent
from src.utils import convert_danmu


class RealtimeDatabase:
    db = TinyDB(storage=MemoryStorage)

    def add_danmu(self, danmu: DanmuReceivedEvent):
        self.db.insert(convert_danmu(danmu).model_dump())

    def add_danmus_from_database(self, danmus: list[Document]):
        self.db.insert_multiple([i.model_dump() for i in danmus])

    def clear(self):
        self.db.truncate()

    def remove_danmus_of_live(self, live: Live):
        self.db.remove(Query().live_id == live.live_id)


class RealtimeDatabaseCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.realtime.database", "RealtimeDatabase"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.realtime.database")

    @staticmethod
    def create(create_type: type[RealtimeDatabase]) -> RealtimeDatabase:
        return create_type()
