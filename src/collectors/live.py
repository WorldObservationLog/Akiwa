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

saya = Saya.current()
channel = Channel.current()
config = it(Config).config
live_status = {}


@channel.use(ListenerSchema(listening_events=[CollectorStartEvent]))
async def check_live_status():
    for room_id in config.listening.room:
        live_status.update({room_id: False})
    while True:
        for room_id in config.listening.room:
            try:
                info = await LiveRoom(room_id).get_room_info()
            except httpx.HTTPError:
                logger.warning(f"Failed to get live room info of {room_id}")
                continue
            if info["room_info"]["live_status"] == 1:
                logger.debug(f"{room_id} is streaming now.")
                if not live_status[room_id]:
                    live_status[room_id] = True
                    bcc.postEvent(LiveStartEvent(room_id=room_id, timestamp=int(time.time())))
            else:
                logger.debug(f"{room_id} is not streaming now.")
                if live_status[room_id]:
                    live_status[room_id] = False
                    bcc.postEvent(LiveEndEvent(room_id=room_id, timestamp=int(time.time())))
        await asyncio.sleep(config.listening.check_interval)
