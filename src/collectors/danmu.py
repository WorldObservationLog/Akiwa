import asyncio
import time

from loguru import logger
from bilibili_api.live import LiveDanmaku
from creart import it
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.behaviour import ListenerSchema

from src.collectors import bcc
from src.config import Config
from src.events import DanmuReceivedEvent, LiveStartEvent, LiveEndEvent
from src.types import DANMU_MSG

saya = Saya.current()
channel = Channel.current()
config = it(Config).config
current_danmu_client = None


@channel.use(ListenerSchema(listening_events=[LiveStartEvent]))
async def danmu_receiver(event: LiveStartEvent):
    global current_danmu_client
    loop = asyncio.get_running_loop()
    room_id = event.room_id

    async def receive_danmu(raw_danmu: dict):
        danmu_type = raw_danmu["name"]
        danmu = raw_danmu["data"][0]["data"]
        timestamp = int(time.time())
        if danmu_type in ["DANMU_MSG", "DANMU_MSG:4:0:2:2:2:0"]:
            bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                             data=DANMU_MSG.from_danmu(danmu["info"]).dict(),
                                             timestamp=timestamp))
        else:
            if danmu_type in config.commands:
                bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                                 data=danmu["data"], timestamp=timestamp))

    client = LiveDanmaku(event.room_id, credential=config.account.to_credential())
    client.add_event_listener("__ALL__", receive_danmu)
    current_danmu_client = client
    loop.create_task(client.connect())
    logger.debug(f"Danmu receiver of {event.room_id} started!")


@channel.use(ListenerSchema(listening_events=[LiveEndEvent]))
async def stop_receive_danmu(event: LiveEndEvent):
    if current_danmu_client:
        await current_danmu_client.disconnect()
        logger.debug(f"Danmu receiver of {event.room_id} stopped!")