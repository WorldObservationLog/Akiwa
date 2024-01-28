import asyncio
from typing import Callable
from urllib.parse import parse_qs

import socketio
from creart import it
from loguru import logger

from src.config import Config
from src.global_vars import GlobalVars
from src.yomiuri.models import StartListening, Actions, StopListening

sio = socketio.AsyncServer(async_mode='asgi')
config = it(Config)
global_vars = it(GlobalVars)
clients = set()
available_clients = set()
room_id_client = {}
callback: Callable


async def start_listening(room_id: int, danmu_callback):
    global callback
    while True:
        if available_clients:
            break
        logger.warning("No available Yomiuri client connected! Wait for 5 seconds")
        await asyncio.sleep(5)
    callback = danmu_callback
    client_sid = available_clients.pop()
    await sio.emit(Actions.StartListening, StartListening(room_id=room_id).model_dump(), room=client_sid)
    room_id_client[room_id] = client_sid


async def stop_listening(room_id: int):
    await sio.emit(Actions.StopListening,
                   data=StopListening(room_id=room_id).model_dump(), room=room_id_client[room_id])


@sio.event()
async def connect(sid, environ, auth):
    token = parse_qs(environ["QUERY_STRING"])["token"][0]
    if token == config.config.yomiuri.token:
        clients.add(sid)
        logger.info(f"Yomiuri client {sid} connected")
    else:
        raise ConnectionRefusedError("Invalid Token!")


@sio.event()
async def disconnect(sid):
    logger.info(f"Yomiuri client {sid} disconnected")
    clients.remove(sid)
    if sid in available_clients:
        available_clients.remove(sid)
    if sid in room_id_client.values():
        client_room_id = {v: k for k, v in room_id_client.items()}
        global_vars.listening_status[client_room_id[sid]] = False
        if global_vars.live_status[client_room_id[sid]]:
            await start_listening(client_room_id[sid], callback)


@sio.on(Actions.Danmu)
async def danmu(sid, data):
    await callback(data)


@sio.on(Actions.Available)
async def available(sid, data):
    if data["status"]:
        available_clients.add(sid)
    else:
        if global_vars.live_status[data["room_id"]]:
            room_id_client[data["room_id"]] = sid
        else:
            await sio.emit(Actions.StopListening, StopListening(room_id=data["room_id"]).model_dump())
