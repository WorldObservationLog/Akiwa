from typing import Union

from loguru import logger
from pydantic import BaseModel


class DanmuItem(BaseModel):
    ...


class Danmu(BaseModel):
    room_id: int
    timestamp: int
    command: str
    data: dict


class DANMU_MSG(DanmuItem):
    mode: int
    font_size: int
    color: int
    timestamp: int
    rnd: int
    uid_crc32: str
    msg_type: int
    bubble: int
    dm_type: int
    emoticon_options: Union[dict, str]
    voice_config: Union[dict, str]
    mode_info: dict
    msg: str
    uid: int
    uname: str
    admin: int
    vip: int
    svip: int
    urank: int
    mobile_verify: int
    uname_color: str
    medal_level: int
    medal_name: str
    runame: str
    medal_room_id: int
    mcolor: int
    special_medal: str
    user_level: int
    ulevel_color: int
    ulevel_rank: str | int
    old_title: str
    title: str
    privilege_type: int

    @classmethod
    def from_danmu(cls, danmu):
        if len(danmu[3]) != 0:
            medal_level = danmu[3][0]
            medal_name = danmu[3][1]
            runame = danmu[3][2]
            room_id = danmu[3][3]
            mcolor = danmu[3][4]
            special_medal = danmu[3][5]
        else:
            medal_level = 0
            medal_name = ''
            runame = ''
            room_id = 0
            mcolor = 0
            special_medal = ''
        try:
            return cls(
                mode=danmu[0][1],
                font_size=danmu[0][2],
                color=danmu[0][3],
                timestamp=danmu[0][4],
                rnd=danmu[0][5],
                uid_crc32=danmu[0][7],
                msg_type=danmu[0][9],
                bubble=danmu[0][10],
                dm_type=danmu[0][12],
                emoticon_options=danmu[0][13],
                voice_config=danmu[0][14],
                mode_info=danmu[0][15],

                msg=danmu[1],

                uid=danmu[2][0],
                uname=danmu[2][1],
                admin=danmu[2][2],
                vip=danmu[2][3],
                svip=danmu[2][4],
                urank=danmu[2][5],
                mobile_verify=danmu[2][6],
                uname_color=danmu[2][7],

                medal_level=medal_level,
                medal_name=medal_name,
                runame=runame,
                medal_room_id=room_id,
                mcolor=mcolor,
                special_medal=special_medal,

                user_level=danmu[4][0],
                ulevel_color=danmu[4][2],
                ulevel_rank=danmu[4][3],

                old_title=danmu[5][0],
                title=danmu[5][1],

                privilege_type=danmu[7],
            )
        except:
            logger.debug(danmu)
            breakpoint()


class Commands:
    INTERACT_WORD = "INTERACT_WORD"
    DANMU_MSG = "DANMU_MSG"
    ENTRY_EFFECT = "ENTRY_EFFECT"
    SEND_GIFT = "SEND_GIFT"
    COMBO_SEND = "COMBO_SEND"
    SUPER_CHAT_MESSAGE = "SUPER_CHAT_MESSAGE"
    GUARD_BUY = "GUARD_BUY"
    LIVE = "LIVE"
    PREPARING = "PREPARING"
    WATCHED_CHANGE = "WATCHED_CHANGE"
    ONLINE_RANK_COUNT = "ONLINE_RANK_COUNT"
    POPULAR_RANK_CHANGED = "POPULAR_RANK_CHANGED"
    LIKE_INFO_V3_UPDATE = "LIKE_INFO_V3_UPDATE"
    ONLINE_COUNT = "ONLINE_COUNT"
    POPULARITY_RED_POCKET_NEW = "POPULARITY_RED_POCKET_NEW"
    USER_TOAST_MSG = "USER_TOAST_MSG"
