from uuid import uuid4

from bilibili_api.live import LiveRoom
from creart import it
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.behaviour import ListenerSchema
from loguru import logger

from src.config import Config
from src.database.database import Database
from src.database.models.live import Live
from src.events import DanmuReceivedEvent, LiveEndEvent, LiveStartEvent, RoomInfoChangedEvent
from src.global_vars import GlobalVars
from src.realtime.database import RealtimeDatabase
from src.utils import preprocess_danmu

saya = Saya.current()
channel = Channel.current()
db = it(Database)
config = it(Config).config
global_vars = it(GlobalVars)
realtime_db = it(RealtimeDatabase)


@channel.use(ListenerSchema(listening_events=[DanmuReceivedEvent]))
async def danmu_receiver(event: DanmuReceivedEvent):
    logger.debug(f"Received Danmu {event.command} from room {event.room_id}")
    for i in preprocess_danmu(event):
        await db.add_danmu(i)
        realtime_db.add_danmu(i)


@channel.use(ListenerSchema(listening_events=[LiveStartEvent]))
async def live_start_receiver(event: LiveStartEvent):
    logger.info(f"Room {event.room_id} Live Started!")
    room_info = await LiveRoom(event.room_id).get_room_info()
    live = Live(live_id=uuid4().hex, room_id=event.room_id, start_time=event.timestamp,
                end_time=0, title=room_info["room_info"]["title"])
    global_vars.live_status[event.room_id] = True
    if await db.if_same_live(live.room_id, live.start_time):
        live = await db.get_latest_live(event.room_id)
        global_vars.current_live.append(live)
        realtime_db.add_danmus_from_database(await db.get_danmu(live))
    else:
        global_vars.current_live.append(live)
    await db.add_live(live)


@channel.use(ListenerSchema(listening_events=[LiveEndEvent]))
async def live_end_receiver(event: LiveEndEvent):
    logger.info(f"Room {event.room_id} Live Ended!")
    live = await db.get_latest_live(event.room_id)
    live.end_time = event.timestamp
    await db.update_live(live)
    global_vars.current_live = [i for i in global_vars.current_live if i.live_id != live.live_id]
    global_vars.live_status[event.room_id] = False
    realtime_db.remove_danmus_of_live(live)


@channel.use(ListenerSchema(listening_events=[RoomInfoChangedEvent]))
async def room_info_changed_receiver(event: RoomInfoChangedEvent):
    logger.info(f"The title of room {event.room_id} changed to {event.title}")
    live = await db.get_latest_live(event.room_id)
    live.title = event.title
    await db.update_live(live)
