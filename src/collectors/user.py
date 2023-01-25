from graia.scheduler.timers import every_custom_minutes
from graia.scheduler.saya import SchedulerSchema
from creart import it
from graia.saya import Saya, Channel
from bilibili_api.user import User

from src.config import Config

saya = Saya.current()
channel = Channel.current()
config = it(Config).config

@channel.use(SchedulerSchema(timer=every_custom_minutes(5)))
async def get_user_info():
    User.

