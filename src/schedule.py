import asyncio
import time

from creart import it
from graia.broadcast import Broadcast
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler import GraiaScheduler

from src.config import Config
from src.events import TimesUpEvent, CollectorStartEvent

loop = asyncio.get_event_loop()
bcc = it(Broadcast)
scheduler = GraiaScheduler(loop, bcc)
config = it(Config)
saya = Saya.current()
channel = Channel.current()


# graia-scheduler does not work and I don't know why
@channel.use(ListenerSchema(listening_events=[CollectorStartEvent]))
async def post_times_up_event():
    while True:
        bcc.postEvent(TimesUpEvent(timestamp=int(time.time())))
        await asyncio.sleep(config.config.schedule_interval)
