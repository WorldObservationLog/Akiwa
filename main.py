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
    saya.require("src.collectors.live")
    saya.require("src.collectors.danmu")
    saya.require("src.receivers.danmu")

if it(Config).config.enable_local_assets:
    from pathlib import Path
    if Path("pyecharts-assets").exists():
        import functools
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        from pyecharts.globals import CurrentConfig

        class quietServer(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        handler = functools.partial(quietServer, directory="pyecharts-assets")
        httpd = HTTPServer(("0.0.0.0", 8000), handler)
        it(Broadcast).loop.run_in_executor(None, httpd.serve_forever)
        CurrentConfig.ONLINE_HOST = "http://127.0.0.1:8000/assets/"
    else:
        logger.error("The pyecharts-assets directory does not exists!")

if __name__ == "__main__":
    it(Broadcast).postEvent(CollectorStartEvent(timestamp=int(time.time())))
    it(Broadcast).loop.run_forever()
