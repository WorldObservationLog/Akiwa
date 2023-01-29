from beanie import Document, UnionDoc
from pydantic import BaseModel, root_validator
from src.types import *
from loguru import logger

DANMU_MATCHES = {"DANMU_MSG": DANMU_MSG,
                 "INTERACT_WORD": INTERACT_WORD,
                 "ENTRY_EFFECT": ENTRY_EFFECT,
                 "SEND_GIFT": SEND_GIFT,
                 "COMBO_SEND": COMBO_SEND,
                 "SUPER_CHAT_MESSAGE": SUPER_CHAT_MESSAGE,
                 "GUARD_BUY": GUARD_BUY}


class DanmuItem(BaseModel):
    ...


class Danmu(Document):
    room_id: int
    timestamp: int
    command: str
    data: Any

    class Settings:
        name = "danmu"

    @root_validator()
    def validator(cls, values):
        if DANMU_MATCHES.get(values["command"]):
            values["data"] = DANMU_MATCHES.get(values["command"]).parse_obj(values["data"])
        else:
            logger.warning(f"Unknown Command! Total data: {values}")
            values["data"] = DanmuItem()
        return values

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

