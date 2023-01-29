import time

from graia.scheduler.timers import every_custom_minutes
from graia.scheduler.saya import SchedulerSchema
from creart import it
from graia.saya import Broadcast, Saya, Channel
from bilibili_api.user import User

from src.config import Config
from src.events import GetFollowersEvent

saya = Saya.current()
channel = Channel.current()
bcc = it(Broadcast)
config = it(Config).config

@channel.use(SchedulerSchema(timer=every_custom_minutes(5)))
async def get_user_info():
    for uid in config.listening.user:
        info = await User(uid).get_relation_info()
        bcc.postEvent(GetFollowersEvent(timestamp=int(time.time()),
                                        uid=uid,
                                        followers=info["follower"]))

