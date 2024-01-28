from typing import Optional

from pydantic import BaseModel, SerializeAsAny


class Data(BaseModel):
    ...


class Register(Data):
    id: str
    token: str


class Available(Data):
    status: bool
    room_id: Optional[int] = None


class Danmu(Data):
    room_id: int
    data: dict


class Result(Data):
    result: bool
    message: Optional[str] = None


class StartListening(Data):
    room_id: int


class StopListening(Data):
    room_id: int


class DataPack(BaseModel):
    action: str
    data: Optional[dict | SerializeAsAny[Data]] = None


class Actions:
    Register = "REGISTER"
    Available = "AVAILABLE"
    StartListening = "STARTLISTENING"
    StopListening = "STOPLISTENING"
    Danmu = "DANMU"
    Result = "RESULT"
