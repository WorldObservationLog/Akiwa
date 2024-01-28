from typing import Optional

from pydantic import SerializeAsAny, BaseModel

from src.analysis.chart import PieData, HistogramData


class Data(BaseModel):
    ...


class Error(BaseModel):
    type: str
    message: str


class Response(BaseModel):
    data: Optional[SerializeAsAny[Data] | list[SerializeAsAny[Data]] | list[SerializeAsAny[PieData | HistogramData | tuple]]]
    error: Optional[Error] = None


class Live(Data):
    live_id: str
    room_id: int
    title: str
    start_time: int
    end_time: int


class Revenue(Data):
    amount: float


class DataWithTimestamp(Data):
    timestamp: int
    value: int
