import time

from loguru import logger

from src.database.models.danmu import DanmuType, DANMU_TYPE_MATCHES, Medal, Danmu
from src.events import DanmuReceivedEvent
from src.types import Commands


def convert_danmu(danmu: DanmuReceivedEvent):
    danmu_item = DANMU_TYPE_MATCHES.get(get_db_type_by_danmu(danmu))
    if not danmu_item:
        logger.error(f"Unknown Danmu Command {danmu.command}")

    match danmu.command:
        case Commands.INTERACT_WORD:
            medal_info = danmu.data.get("fans_medal")
            if not medal_info.get("anchor_roomid"):
                medal_info = None
        case Commands.DANMU_MSG:
            medal_info = {"anchor_roomid": danmu.data.get("medal_room_id"),
                          "medal_level": danmu.data.get("medal_level"),
                          "medal_name": danmu.data.get("medal_name")}
            if not medal_info.get("anchor_roomid"):
                medal_info = None
        case Commands.SEND_GIFT | Commands.COMBO_SEND | Commands.SUPER_CHAT_MESSAGE:
            medal_info = danmu.data.get("medal_info")
        case _:
            medal_info = None

    if medal_info:
        medal = Medal(room_id=medal_info.get("anchor_roomid"),
                      level=medal_info.get("medal_level"),
                      name=medal_info.get("medal_name"))
    else:
        medal = None

    db_danmu = Danmu(timestamp=int(time.time()),
                     room_id=danmu.room_id,
                     type=get_db_type_by_danmu(danmu),
                     medal=medal)

    match danmu.command:
        case Commands.LIVE | Commands.PREPARING | Commands.LIKE_INFO_V3_UPDATE | Commands.POPULAR_RANK_CHANGED | Commands.WATCHED_CHANGE | Commands.ONLINE_RANK_COUNT:
            db_danmu.uid = None
        case _:
            db_danmu.uid = danmu.data.get("uid")

    match danmu.command:
        case Commands.DANMU_MSG:
            data = danmu_item(text=danmu.data.get("msg"))
        case Commands.SEND_GIFT:
            # 单位是金瓜子
            if danmu.data.get("coin_type") == "gold":
                data = danmu_item(price=danmu.data.get("price") / 1000)
            else:
                data = danmu_item(price=0.0)
        case Commands.POPULARITY_RED_POCKET_NEW:
            # 单位是电池，每个红包主播抽成20%
            data = danmu_item(price=danmu.data.get("price") / 10 / 5)
        case Commands.GUARD_BUY:
            # 单位是金瓜子
            data = danmu_item(price=danmu.data.get("price") / 1000)
        case Commands.COMBO_SEND:
            # 单位是金瓜子
            data = danmu_item(price=danmu.data.get("combo_total_coin") / 1000)
        case Commands.SUPER_CHAT_MESSAGE:
            # 单位是人民币
            data = danmu_item(price=danmu.data.get("price"), text=danmu.data.get("message"))
        case Commands.POPULAR_RANK_CHANGED:
            data = danmu_item(rank=danmu.data.get("rank"))
        case Commands.LIKE_INFO_V3_UPDATE:
            data = danmu_item(count=danmu.data.get("click_count"))
        case Commands.WATCHED_CHANGE:
            data = danmu_item(count=danmu.data.get("num"))
        case Commands.ONLINE_RANK_COUNT:
            if not danmu.data.get("count"):
                breakpoint()
            data = danmu_item(count=danmu.data.get("count"))
        case Commands.ONLINE_COUNT:
            data = danmu_item(count=danmu.data.get("online_count"))
        case Commands.INTERACT_WORD | Commands.ENTRY_EFFECT | Commands.LIVE | Commands.PREPARING:
            data = danmu_item()
        case _:
            data = danmu_item()

    db_danmu.data = data

    return db_danmu


_DB_TYPE_COMMAND_MAPPING = {Commands.INTERACT_WORD: DanmuType.Entry,
                            Commands.DANMU_MSG: DanmuType.DanmuMsg,
                            Commands.ENTRY_EFFECT: DanmuType.GuardEntry,
                            Commands.SEND_GIFT: DanmuType.Gift,
                            Commands.COMBO_SEND: DanmuType.Gift,
                            Commands.POPULARITY_RED_POCKET_NEW: DanmuType.Gift,
                            Commands.SUPER_CHAT_MESSAGE: DanmuType.SuperChat,
                            Commands.GUARD_BUY: DanmuType.Guard,
                            Commands.USER_TOAST_MSG: DanmuType.Guard,
                            Commands.LIVE: DanmuType.StartLive,
                            Commands.PREPARING: DanmuType.EndLive,
                            Commands.WATCHED_CHANGE: DanmuType.WatchedCount,
                            Commands.ONLINE_RANK_COUNT: DanmuType.PaidCount,
                            Commands.ONLINE_COUNT: DanmuType.OnlineCount,
                            Commands.POPULAR_RANK_CHANGED: DanmuType.PopularRank,
                            Commands.LIKE_INFO_V3_UPDATE: DanmuType.LikeCount
                            }


def get_db_type_by_danmu(danmu: DanmuReceivedEvent):
    match danmu.command:
        case Commands.INTERACT_WORD:
            if danmu.data.get("msg_type") == 1:
                return DanmuType.Entry
            else:
                return DanmuType.Follow
        case _:
            return _DB_TYPE_COMMAND_MAPPING[danmu.command]


def preprocess_danmu(danmu: DanmuReceivedEvent):
    match danmu.command:
        case Commands.ONLINE_RANK_COUNT:
            if danmu.data.get("online_count"):
                new_danmu = danmu.model_copy(deep=True)
                del new_danmu.data["count"]
                new_danmu.command = Commands.ONLINE_COUNT
                del danmu.data["online_count"]
                return [danmu, new_danmu]
            else:
                return [danmu]
        case _:
            return [danmu]
