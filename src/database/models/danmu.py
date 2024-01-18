from typing import Optional

from beanie import Document
from pydantic import SerializeAsAny, model_validator, BaseModel


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


class LikeCount(DanmuItem):
    count: int


class WatchedCount(DanmuItem):
    count: int


class PaidCount(DanmuItem):
    count: int


class OnlineCount(DanmuItem):
    count: int


class PopularRank(DanmuItem):
    rank: int


class Follow(DanmuItem):
    ...


class Danmu(Document):
    timestamp: int
    room_id: int
    uid: Optional[int] = None
    type: str
    medal: Optional[Medal] = None
    data: Optional[SerializeAsAny[DanmuItem]] = None

    class Settings:
        name = "danmu"

    @model_validator(mode="before")
    @classmethod
    def data_deserialization(cls, data: dict):
        if data.get("data"):
            if type(data.get("data")) is dict:
                data["data"] = DANMU_TYPE_MATCHES[data["type"]].model_validate(data["data"])
        return data


class DanmuType:
    Guard = "Guard"
    Gift = "Gift"
    SuperChat = "SuperChat"
    Entry = "Entry"
    GuardEntry = "GuardEntry"
    DanmuMsg = "DanmuMsg"
    StartLive = "StartLive"
    EndLive = "EndLive"
    LikeCount = "LikeCount"
    WatchedCount = "WatchedCount"
    PaidCount = "PaidCount"
    OnlineCount = "OnlineCount"
    PopularRank = "PopularRank"
    Follow = "Follow"


DANMU_TYPE_MATCHES = {DanmuType.DanmuMsg: DanmuMsg,
                      DanmuType.Guard: Guard,
                      DanmuType.Gift: Gift,
                      DanmuType.SuperChat: SuperChat,
                      DanmuType.Entry: Entry,
                      DanmuType.GuardEntry: GuardEntry,
                      DanmuType.StartLive: StartLive,
                      DanmuType.EndLive: EndLive,
                      DanmuType.LikeCount: LikeCount,
                      DanmuType.WatchedCount: WatchedCount,
                      DanmuType.PaidCount: PaidCount,
                      DanmuType.OnlineCount: OnlineCount,
                      DanmuType.PopularRank: PopularRank,
                      DanmuType.Follow: Follow}
