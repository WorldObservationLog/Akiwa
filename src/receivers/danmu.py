from creart import it
from pydantic import BaseModel
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.behaviour import ListenerSchema
from src.config import Config
from src.database import Database


from src.events import DanmuReceivedEvent

saya = Saya.current()
channel = Channel.current()
db = it(Database)
config = it(Config).config


@channel.use(ListenerSchema(listening_events=[DanmuReceivedEvent]))
async def danmu_receiver(event: DanmuReceivedEvent):
    print(f"Received Danmu {event.command} from room {event.room_id}")
    await db.add_danmu(event)
