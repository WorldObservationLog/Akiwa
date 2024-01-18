import sys
import time
import asyncio

from creart import create, it, add_creator
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour
from loguru import logger

from src.config import Config, ConfigCreator
from src.events import CollectorStartEvent
from src.realtime.database import RealtimeDatabaseCreator, RealtimeDatabase
from src.global_vars import GlobalVarsCreator, GlobalVars

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
    saya.require("src.services.services")

if __name__ == "__main__":
    it(Broadcast).postEvent(CollectorStartEvent(timestamp=int(time.time())))
    loop.run_forever()
