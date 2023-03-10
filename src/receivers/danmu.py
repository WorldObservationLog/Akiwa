from bilibili_api.live import LiveRoom
from creart import it
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.behaviour import ListenerSchema
from loguru import logger

from src.config import Config
from src.database.database import Database
from src.events import DanmuReceivedEvent, HeartbeatReceivedEvent, LiveEndEvent, LiveStartEvent
from src.database.models import Live

saya = Saya.current()
channel = Channel.current()
db = it(Database)
config = it(Config).config


@channel.use(ListenerSchema(listening_events=[DanmuReceivedEvent]))
async def danmu_receiver(event: DanmuReceivedEvent):
    logger.info(f"Received Danmu {event.command} from room {event.room_id}")
    await db.add_danmu(event)


@channel.use(ListenerSchema(listening_events=[HeartbeatReceivedEvent]))
async def heartbeat_receiver(event: HeartbeatReceivedEvent):
    logger.info(f"Received Heartbeat from room {event.room_id}, watching: {event.watching}")
    if event.watching > 1:
        await db.add_heartbeat(event)


@channel.use(ListenerSchema(listening_events=[LiveStartEvent]))
async def live_start_receiver(event: LiveStartEvent):
    logger.info(f"Room {event.room_id} Live Started!")
    room_info = await LiveRoom(event.room_id).get_room_info()
    await db.add_live(Live(room_id=event.room_id,
                           start_time=event.timestamp,
                           end_time=0,
                           title=room_info["room_info"]["title"]))


@channel.use(ListenerSchema(listening_events=[LiveEndEvent]))
async def live_end_receiver(event: LiveEndEvent):
    logger.info(f"Room {event.room_id} Live Ended!")
    live = await db.get_latest_live(event.room_id)
    live.end_time = event.timestamp
    await db.update_live(live)
