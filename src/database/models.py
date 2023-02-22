from typing import Optional, Literal

from beanie import Document, UnionDoc
from pydantic import BaseModel, root_validator
from src.types import *
from loguru import logger


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


DB_TYPE_MATCHES = {"DanmuMsg": DanmuMsg,
                   "Guard": Guard,
                   "Gift": Gift,
                   "SuperChat": SuperChat,
                   "Entry": Entry,
                   "GuardEntry": GuardEntry,
                   "StartLive": StartLive,
                   "EndLive": EndLive}


class Danmu(Document):
    timestamp: int
    room_id: int
    uid: Optional[int]
    type: Literal["DanmuMsg", "Guard", "Gift", "SuperChat", "Entry", "GuardEntry", "StartLive", "EndLive"]
    medal: Optional[Medal]
    data: Optional[DanmuItem]

    class Settings:
        name = "danmu"


class Heartbeat(Document):
    room_id: int
    timestamp: int
    watching: int

    class Settings:
        name = "heartbeat"


class Live(Document):
    room_id: int
    start_time: int
    end_time: int

    class Settings:
        name = "live"
