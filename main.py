import sys
import time

from creart import create, it, add_creator
from graia.broadcast import Broadcast
from graia.saya import Saya
from loguru import logger

from src.config import Config, ConfigCreator
from src.events import CollectorStartEvent

logger.remove()
logger.add(sys.stderr, level="INFO")

add_creator(ConfigCreator)
create(Config)
saya = create(Saya)

from src.database.database import Database, DatabaseCreator

add_creator(DatabaseCreator)
create(Database)

with saya.module_context():
    saya.require("src.collectors.danmu")
    saya.require("src.receivers.danmu")

if __name__ == "__main__":
    it(Broadcast).postEvent(CollectorStartEvent(timestamp=int(time.time())))
    it(Broadcast).loop.run_forever()
