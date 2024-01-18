import time

import httpx
from bilibili_api.user import User
from bilibili_api import HEADERS
from creart import it
from graia.broadcast import Broadcast
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema

from src.config import Config
from src.events import GetFollowersEvent, TimesUpEvent, LiveStartEvent, LiveEndEvent, Event, GetGuardsEvent

saya = Saya.current()
channel = Channel.current()
bcc = it(Broadcast)
config = it(Config).config
client = httpx.AsyncClient(headers=HEADERS)


async def _request_guard_api(room_id: int, uid: int):
    ENDPOINT = "https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList"
    resp = (await client.get(ENDPOINT, params={"roomid": room_id, "ruid": uid, "page_num": 1, "page": 1})).json()
    if resp["code"] == 0:
        return resp
    else:
        return None


@channel.use(ListenerSchema(listening_events=[TimesUpEvent, LiveStartEvent, LiveEndEvent]))
async def get_user_info(event: Event):
    for uid in config.listening.user:
        info = await User(uid).get_relation_info()
        bcc.postEvent(GetFollowersEvent(timestamp=event.timestamp,
                                        uid=uid,
                                        followers=info["follower"]))


@channel.use(ListenerSchema(listening_events=[TimesUpEvent, LiveStartEvent, LiveEndEvent]))
async def get_guard_num(event: Event):
    for uid in config.listening.user:
        room_info = await User(uid).get_live_info()
        if room_info["live_room"]:
            room_id = room_info["live_room"]["roomid"]
            guard_info = await _request_guard_api(room_id, uid)
            if guard_info:
                bcc.postEvent(GetGuardsEvent(timestamp=event.timestamp,
                                             uid=uid,
                                             guards=guard_info["data"]["info"]["num"]))
