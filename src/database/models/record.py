from typing import Optional

from beanie import Document
from pydantic import SerializeAsAny, BaseModel


class RecordItem(BaseModel):
    ...


class Record(Document):
    uid: int
    timestamp: int
    type: str
    data: Optional[SerializeAsAny[RecordItem]] = None

    class Settings:
        name = "record"


class Follower(RecordItem):
    num: int


class Guard(RecordItem):
    num: int


class RecordType:
    Follower = "Follower"
    Guard = "Guard"
