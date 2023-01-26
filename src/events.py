from graia.broadcast import BaseDispatcher, Dispatchable, DispatcherInterface
from pydantic import BaseModel
import time


class Event(Dispatchable, BaseModel):
    timestamp: int

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface):
            pass


class DanmuReceivedEvent(Event):
    room_id: int
    command: str
    data: dict


class HeartbeatReceivedEvent(Event):
    room_id: int
    watching: int


class CollectorStartEvent(Event):
    ...

class LiveStartEvent(Event):
    room_id: int

class LiveEndEvent(Event):
    room_id: int

