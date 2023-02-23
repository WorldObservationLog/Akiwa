import time

from loguru import logger

from src.database.models import DB_TYPE_MATCHES, Medal, Danmu
from src.events import DanmuReceivedEvent
from src.types import Commands, DB_Types

DB_TYPE_COMMAND_MAPPING = {Commands.INTERACT_WORD: DB_Types.Entry,
                           Commands.DANMU_MSG: DB_Types.DanmuMsg,
                           Commands.ENTRY_EFFECT: DB_Types.GuardEntry,
                           Commands.SEND_GIFT: DB_Types.Gift,
                           Commands.COMBO_SEND: DB_Types.Gift,
                           Commands.SUPER_CHAT_MESSAGE: DB_Types.SuperChat,
                           Commands.GUARD_BUY: DB_Types.Guard
                           }


def convert_danmu(danmu: DanmuReceivedEvent):
    danmu_item = DB_TYPE_MATCHES.get(DB_TYPE_COMMAND_MAPPING.get(danmu.command))
    if not danmu_item:
        logger.error(f"Unknown Danmu Command {danmu.command}")

    match danmu.command:
        case Commands.LIVE | Commands.PREPARING | Commands.GUARD_BUY | Commands.ENTRY_EFFECT:
            medal_info = None
        case Commands.INTERACT_WORD:
            medal_info = danmu.data.get("fans_medal")
            if not medal_info.get("anchor_roomid"):
                medal_info = None
        case _:
            medal_info = danmu.data.get("medal_info")

    if medal_info:
        medal = Medal(room_id=medal_info.get("anchor_roomid"),
                      level=medal_info.get("medal_level"),
                      name=medal_info.get("medal_name"))
    else:
        medal = None

    db_danmu = Danmu(timestamp=int(time.time()),
                     room_id=danmu.room_id,
                     type=DB_TYPE_COMMAND_MAPPING[danmu.command],
                     medal=medal)

    match danmu.command:
        case Commands.LIVE | Commands.PREPARING:
            db_danmu.uid = None
        case _:
            db_danmu.uid = danmu.data.get("uid")

    match danmu.command:
        case Commands.DANMU_MSG:
            data = danmu_item(text=danmu.data.get("msg"))
        case Commands.GUARD_BUY | Commands.SEND_GIFT:
            data = danmu_item(price=danmu.data.get("price") / 1000)
        case Commands.COMBO_SEND:
            data = danmu_item(price=danmu.data.get("combo_total_coin") / danmu.data.get("combo_num") / 1000)
        case Commands.INTERACT_WORD | Commands.ENTRY_EFFECT | Commands.LIVE | Commands.PREPARING:
            data = danmu_item()
        case _:
            data = danmu_item()

    db_danmu.data = data

    return db_danmu
