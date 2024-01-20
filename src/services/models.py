from typing import Optional

from pydantic import SerializeAsAny
from pydantic.dataclasses import dataclass

from src.analysis.chart import PieData, HistogramData


@dataclass
class Data:
    ...


@dataclass
class Error:
    type: str
    message: str


@dataclass
class Response:
    data: Optional[SerializeAsAny[Data] | list[SerializeAsAny[Data]] | list[SerializeAsAny[PieData | HistogramData]]]
    error: Optional[Error] = None


@dataclass
class Live(Data):
    live_id: str
    room_id: int
    title: str
    start_time: int
    end_time: int


@dataclass
class Revenue(Data):
    amount: float


@dataclass
class DataWithTimestamp(Data):
    timestamp: int
    value: int
