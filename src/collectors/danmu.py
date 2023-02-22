import asyncio
import struct
import time

from creart import it
from danmu import DanmuClient
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.behaviour import ListenerSchema

from src.collectors import bcc
from src.config import Config
from src.events import CollectorStartEvent, DanmuReceivedEvent, HeartbeatReceivedEvent, LiveStartEvent, LiveEndEvent
from src.types import DANMU_MSG

saya = Saya.current()
channel = Channel.current()
config = it(Config).config


@channel.use(ListenerSchema(listening_events=[CollectorStartEvent]))
async def danmu_receiver(event: CollectorStartEvent):
    loop = asyncio.get_running_loop()

    async def receive_danmu(room_id: int, danmu: dict):
        timestamp = int(time.time())
        if danmu["cmd"] in ["DANMU_MSG", "DANMU_MSG:4:0:2:2:2:0"]:
            bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                             data=DANMU_MSG.from_danmu(danmu["info"]).dict(),
                                             timestamp=timestamp))
        else:
            if danmu["cmd"] in config.commands and not danmu["cmd"] in ["PREPARING", "LIVE"]:
                bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                                 data=danmu["data"], timestamp=timestamp))
            elif danmu["cmd"] in ["PREPARING", "LIVE"]:
                bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                                 data={}, timestamp=timestamp))
                if danmu["cmd"] == "PREPARING":
                    bcc.postEvent(LiveEndEvent(room_id=room_id, timestamp=timestamp))
                else:
                    bcc.postEvent(LiveStartEvent(room_id=room_id, timestamp=timestamp))

    async def receive_heartbeat(room_id, rawDanmu):
        timestamp = int(time.time())
        bcc.postEvent(HeartbeatReceivedEvent(room_id=room_id,
                                             watching=struct.unpack("!I", rawDanmu.body)[0],
                                             timestamp=timestamp))

    for i in it(Config).config.listening.room:
        dmc = DanmuClient(i)
        dmc.on_danmu(receive_danmu)
        dmc.on_heartbeat(receive_heartbeat)
        dmc.run(loop)
