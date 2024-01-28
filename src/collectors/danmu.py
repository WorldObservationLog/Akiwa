import asyncio
import json
import time

from loguru import logger
from bilibili_api.live import LiveDanmaku
from creart import it
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.behaviour import ListenerSchema

from src.collectors import bcc
from src.config import Config
from src.events import DanmuReceivedEvent, LiveStartEvent, LiveEndEvent, TimesUpEvent, CollectorStartEvent, \
    RoomInfoChangedEvent
from src.global_vars import GlobalVars
from src.types import DANMU_MSG
from src.yomiuri.services import start_listening, stop_listening

saya = Saya.current()
channel = Channel.current()
config = it(Config).config
global_vars = it(GlobalVars)
current_danmu_client = {}


async def handle_danmu(raw_danmu: dict):
    danmu_type = raw_danmu["name"]
    if len(raw_danmu["data"]) > 1:
        breakpoint()
    if danmu_type == "TIMEOUT":
        return
    room_id = raw_danmu["data"][0]["room_display_id"]
    danmu = raw_danmu["data"][0]["data"]
    timestamp = int(time.time())
    if danmu_type == "DANMU_MSG":
        bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                         data=DANMU_MSG.from_danmu(danmu["info"]).model_dump(),
                                         timestamp=timestamp))
    elif danmu_type == "ROOM_CHANGE":
        bcc.postEvent(RoomInfoChangedEvent(room_id=room_id, title=danmu["title"], timestamp=timestamp))
    else:
        if danmu_type in config.commands:
            bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                             data=danmu["data"], timestamp=timestamp))


@channel.use(ListenerSchema(listening_events=[LiveStartEvent]))
async def danmu_receiver(event: LiveStartEvent):
    global current_danmu_client
    loop = asyncio.get_running_loop()
    if config.yomiuri.enable:
        await start_listening(room_id=event.room_id, danmu_callback=handle_danmu)
    else:
        if current_danmu_client.values() or (current_danmu_client == [None] * len(current_danmu_client)):
            logger.warning("Akiwa is listening multi live rooms! It may cause danmu lost!")
        await refresh_credential()
        client = LiveDanmaku(event.room_id, credential=global_vars.credential)
        client.add_event_listener("__ALL__", handle_danmu)
        current_danmu_client[event.room_id] = client
        loop.create_task(client.connect())
        logger.debug(f"Danmu receiver of {event.room_id} started!")


@channel.use(ListenerSchema(listening_events=[LiveEndEvent]))
async def stop_receive_danmu(event: LiveEndEvent):
    global current_danmu_client
    if config.yomiuri.enable:
        await stop_listening(event.room_id)
    else:
        if current_danmu_client:
            await current_danmu_client[event.room_id].disconnect()
            current_danmu_client[event.room_id] = None
            logger.debug(f"Danmu receiver of {event.room_id} stopped!")


@channel.use(ListenerSchema(listening_events=[TimesUpEvent, CollectorStartEvent]))
async def refresh_credential():
    if await global_vars.credential.check_refresh():
        logger.warning("Bilibili credential is invalid!")
        # bilibili-api-python 及其 dev 分支均无法刷新cookie，怀疑算法已修改
        # await global_vars.credential.refresh()
        # logger.debug("Bilibili credential refreshed")
        # with open("credential.json", "w") as f:
        #    json.dump({"sessdata": global_vars.credential.sessdata, "bili_jct": global_vars.credential.bili_jct,
        #               "buvid3": global_vars.credential.buvid3, "deaduserid": global_vars.credential.dedeuserid,
        #               "ac_time_value": global_vars.credential.ac_time_value}, f)
