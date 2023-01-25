import asyncio
import struct
from graia.saya.builtins.broadcast.behaviour import ListenerSchema

from pydantic import BaseModel
from typing import Union
from danmu import DanmuClient
from creart import it
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled

from src.collectors import bcc
from src.events import CollectorStartEvent, DanmuReceivedEvent, HeartbeatReceivedEvent, LiveStartEvent, LiveEndEvent
from src.config import Config
from src.types import DANMU_MSG

saya = Saya.current()
channel = Channel.current()
config = it(Config).config



@channel.use(ListenerSchema(listening_events=[CollectorStartEvent]))
async def danmu_receiver(event: CollectorStartEvent):
    loop = asyncio.get_running_loop()

    async def receive_danmu(room_id: int, danmu: dict):
        if danmu["cmd"] in ["DANMU_MSG", "DANMU_MSG:4:0:2:2:2:0"]:
            bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                             data=DANMU_MSG.from_danmu(danmu["info"]).dict()))
        else:
            if danmu["cmd"] in config.commands and not danmu["cmd"] in ["PREPARING", "LIVE"]:
                bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"], data=danmu["data"]))
            elif danmu["cmd"] in ["PREPARING", "LIVE"]:
                bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"], data={}))
                if danmu["cmd"] == "PREPARING":
                    bcc.postEvent(LiveEndEvent(room_id=room_id))
                else:
                    bcc.postEvent(LiveStartEvent(room_id=room_id))

    async def receive_heartbeat(room_id, rawDanmu):
        bcc.postEvent(HeartbeatReceivedEvent(room_id=room_id, watching=struct.unpack("!I", rawDanmu.body)[0]))

    for i in it(Config).config.listening.room:
        dmc = DanmuClient(i)
        dmc.on_danmu(receive_danmu)
        dmc.on_heartbeat(receive_heartbeat)
        dmc.run(loop)
