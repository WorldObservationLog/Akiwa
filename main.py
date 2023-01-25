import asyncio

from creart import create, it, add_creator
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast.behaviour import BroadcastBehaviour
from graia.scheduler import GraiaScheduler

from src.config import Config, ConfigCreator
from src.events import CollectorStartEvent

add_creator(ConfigCreator)
create(Config)

from src.database import Database, DatabaseCreator

add_creator(DatabaseCreator)
create(Database)

saya = create(Saya)

with saya.module_context():
    saya.require("src.collectors.danmu")
    saya.require("src.receivers.danmu")

if __name__ == "__main__":
    it(Broadcast).postEvent(CollectorStartEvent())
    it(Broadcast).loop.run_forever()
