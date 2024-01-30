import asyncio
import time
from urllib.parse import parse_qs

import socketio
from creart import it
from graia.broadcast import Broadcast
from loguru import logger

from src.config import Config
from src.events import DanmuReceivedEvent, RoomInfoChangedEvent
from src.global_vars import GlobalVars
from src.types import DANMU_MSG
from src.yomiuri.models import StartListening, Actions, StopListening

sio = socketio.AsyncServer(async_mode='asgi')
config = it(Config)
bcc = it(Broadcast)
global_vars = it(GlobalVars)
clients = set()
available_clients = set()
room_id_client = {}


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
        if danmu_type in config.config.commands:
            bcc.postEvent(DanmuReceivedEvent(room_id=room_id, command=danmu["cmd"],
                                             data=danmu["data"], timestamp=timestamp))


async def start_listening(room_id: int):
    while True:
        if available_clients:
            break
        if not global_vars.live_status.get(room_id):
            logger.error("Live ended without available Yomiuri client!")
            return
        logger.warning("No available Yomiuri client connected! Wait for 5 seconds")
        await asyncio.sleep(5)
    client_sid = available_clients.pop()
    await sio.emit(Actions.StartListening, StartListening(room_id=room_id).model_dump(), room=client_sid)
    room_id_client[room_id] = client_sid


async def stop_listening(room_id: int):
    await sio.emit(Actions.StopListening,
                   data=StopListening(room_id=room_id).model_dump(), room=room_id_client[room_id])


@sio.event()
async def connect(sid, environ):
    token = parse_qs(environ["QUERY_STRING"])["token"][0]
    if token == config.config.yomiuri.token:
        clients.add(sid)
        logger.info(f"Yomiuri client {sid} connected")
    else:
        raise ConnectionRefusedError("Invalid Token!")


@sio.event()
async def disconnect(sid):
    logger.info(f"Yomiuri client {sid} disconnected")
    if sid in clients:
        clients.remove(sid)
    if sid in available_clients:
        available_clients.remove(sid)
    if sid in room_id_client.values():
        client_room_id = {v: k for k, v in room_id_client.items()}
        global_vars.listening_status[client_room_id[sid]] = False
        if global_vars.live_status[client_room_id[sid]]:
            await start_listening(client_room_id[sid])


@sio.on(Actions.Danmu)
async def danmu(sid, data):
    await handle_danmu(data)


@sio.on(Actions.Available)
async def available(sid, data):
    if data["status"]:
        available_clients.add(sid)
    else:
        if global_vars.live_status[data["room_id"]]:
            room_id_client[data["room_id"]] = sid
        else:
            await sio.emit(Actions.StopListening, StopListening(room_id=data["room_id"]).model_dump())
