from creart import it
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

from src.config import Config
from src.database.database import Database
from src.database.models.record import Record, Follower, RecordType, Guard
from src.events import GetFollowersEvent, GetGuardsEvent

saya = Saya.current()
channel = Channel.current()
db = it(Database)
config = it(Config).config


@channel.use(ListenerSchema(listening_events=[GetFollowersEvent]))
async def add_follower_record(event: GetFollowersEvent):
    logger.debug(f"Recorded the follower number of uid {event.uid}")
    await db.add_record(Record(uid=event.uid, timestamp=event.timestamp,
                               type=RecordType.Follower, data=Follower(num=event.followers)))


@channel.use(ListenerSchema(listening_events=[GetGuardsEvent]))
async def add_guard_record(event: GetGuardsEvent):
    logger.debug(f"Recorded the guard number of uid {event.uid}")
    await db.add_record(Record(uid=event.uid, timestamp=event.timestamp,
                               type=RecordType.Guard, data=Guard(num=event.guards)))