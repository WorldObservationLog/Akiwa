import asyncio
import sys
import time

import socketio
import uvicorn
from creart import create, it, add_creator
from graia.broadcast import Broadcast
from graia.saya import Saya
from loguru import logger
from quart import Quart

from src.config import Config, ConfigCreator
from src.events import CollectorStartEvent
from src.global_vars import GlobalVarsCreator, GlobalVars
from src.realtime.database import RealtimeDatabaseCreator, RealtimeDatabase

saya = create(Saya)
add_creator(ConfigCreator)
create(Config)
loop = asyncio.get_event_loop()

logger.remove()
logger.add(sys.stderr, level=it(Config).config.log_level)

from src.database.database import Database, DatabaseCreator

add_creator(DatabaseCreator)
create(Database)
add_creator(RealtimeDatabaseCreator)
create(RealtimeDatabase)
add_creator(GlobalVarsCreator)
create(GlobalVars)

with saya.module_context():
    saya.require("src.schedule")
    saya.require("src.collectors.live")
    saya.require("src.collectors.danmu")
    saya.require("src.collectors.user")
    saya.require("src.receivers.danmu")
    saya.require("src.receivers.user")

from src.services.services import bp as service_bluepoint
from src.yomiuri.services import sio

app = Quart(__name__)
app.register_blueprint(service_bluepoint)
if it(Config).config.yomiuri.enable:
    sio_app = socketio.ASGIApp(sio, app)
    config = uvicorn.Config(sio_app, host=it(Config).config.service.host, port=it(Config).config.service.port)
else:
    config = uvicorn.Config(app, host=it(Config).config.service.host, port=it(Config).config.service.port)
server = uvicorn.Server(config)

if __name__ == "__main__":
    it(Broadcast).postEvent(CollectorStartEvent(timestamp=int(time.time())))
    loop.create_task(server.serve())
    loop.run_forever()
