from typing import Optional, Literal

from beanie import Document
from pydantic import root_validator

from src.types import *


class Medal(BaseModel):
    room_id: int
    level: int
    name: str


class DanmuItem(BaseModel):
    ...


class DanmuMsg(DanmuItem):
    text: str


class Gift(DanmuItem):
    price: float


class Guard(DanmuItem):
    price: float


class SuperChat(DanmuItem):
    price: float
    text: str


class Entry(DanmuItem):
    ...


class GuardEntry(DanmuItem):
    ...


class StartLive(DanmuItem):
    ...


class EndLive(DanmuItem):
    ...


DB_TYPE_MATCHES = {DB_Types.DanmuMsg: DanmuMsg,
                   DB_Types.Guard: Guard,
                   DB_Types.Gift: Gift,
                   DB_Types.SuperChat: SuperChat,
                   DB_Types.Entry: Entry,
                   DB_Types.GuardEntry: GuardEntry,
                   DB_Types.StartLive: StartLive,
                   DB_Types.EndLive: EndLive}


class Danmu(Document):
    timestamp: int
    room_id: int
    uid: Optional[int]
    type: Literal["DanmuMsg", "Guard", "Gift", "SuperChat", "Entry", "GuardEntry", "StartLive", "EndLive"]
    medal: Medal | None
    data: Optional[DanmuItem]

    class Settings:
        name = "danmu"

    @root_validator
    def data_deserialization(cls, data: dict):
        cls.parse_obj(data)
        cls.data = DB_TYPE_MATCHES[data["type"]].parse_obj(data["data"])


class Heartbeat(Document):
    room_id: int
    timestamp: int
    watching: int

    class Settings:
        name = "heartbeat"


class Live(Document):
    room_id: int
    title: str
    start_time: int
    end_time: int

    class Settings:
        name = "live"
