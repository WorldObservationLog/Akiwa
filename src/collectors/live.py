import asyncio
import time

import httpx
from loguru import logger
from creart import it
from graia.saya import Saya, Channel
from bilibili_api.live import LiveRoom
from graia.saya.builtins.broadcast import ListenerSchema

from src.collectors import bcc
from src.config import Config
from src.events import LiveStartEvent, CollectorStartEvent, LiveEndEvent
from src.global_vars import GlobalVars

saya = Saya.current()
channel = Channel.current()
config = it(Config).config
global_vars = it(GlobalVars)


@channel.use(ListenerSchema(listening_events=[CollectorStartEvent]))
async def check_live_status():
    for room_id in config.listening.room:
        global_vars.listening_status.update({room_id: False})
    while True:
        for room_id in config.listening.room:
            try:
                info = await LiveRoom(room_id).get_room_info()
            except httpx.HTTPError:
                logger.warning(f"Failed to get live room info of {room_id}")
                continue
            if info["room_info"]["live_status"] == 1:
                logger.debug(f"{room_id} is streaming now.")
                if not global_vars.listening_status[room_id]:
                    global_vars.listening_status[room_id] = True
                    bcc.postEvent(LiveStartEvent(room_id=room_id, timestamp=int(time.time())))
            else:
                logger.debug(f"{room_id} is not streaming now.")
                if global_vars.listening_status[room_id]:
                    global_vars.listening_status[room_id] = False
                    bcc.postEvent(LiveEndEvent(room_id=room_id, timestamp=int(time.time())))
        await asyncio.sleep(config.listening.check_interval)
