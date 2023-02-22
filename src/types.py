from typing import Any, List, Union

from pydantic import BaseModel


class Live(BaseModel):
    room_id: int
    start_time: int
    end_time: int


class DanmuItem(BaseModel):
    ...


class Danmu(BaseModel):
    room_id: int
    timestamp: int
    command: str
    data: DanmuItem


class Contribution(BaseModel):
    grade: int


class FansMedal(BaseModel):
    anchor_roomid: int
    guard_level: int
    icon_id: int
    is_lighted: int
    medal_color: int
    medal_color_border: int
    medal_color_end: int
    medal_color_start: int
    medal_level: int
    medal_name: str
    score: int
    special: str
    target_id: int


class INTERACT_WORD(DanmuItem):
    contribution: Contribution
    core_user_type: int
    dmscore: int
    fans_medal: FansMedal
    identities: List[int]
    is_spread: int
    msg_type: int
    privilege_type: int
    roomid: int
    score: int
    spread_desc: str
    spread_info: str
    tail_icon: int
    timestamp: int
    trigger_time: int
    uid: int
    uname: str
    uname_color: str


class MedalInfo(BaseModel):
    anchor_roomid: int
    anchor_uname: str
    guard_level: int
    icon_id: int
    is_lighted: int
    medal_color: int | str
    medal_color_border: int
    medal_color_end: int
    medal_color_start: int
    medal_level: int
    medal_name: str
    special: str
    target_id: int


class ReceiveUserInfo(BaseModel):
    uid: int
    uname: str


class SEND_GIFT(DanmuItem):
    action: str
    batch_combo_id: str
    batch_combo_send: Any
    beatId: str
    biz_source: str
    blind_gift: Any
    broadcast_id: int
    coin_type: str
    combo_resources_id: int
    combo_send: Any
    combo_stay_time: int
    combo_total_coin: int
    crit_prob: int
    demarcation: int
    discount_price: int
    dmscore: int
    draw: int
    effect: int
    effect_block: int
    face: str
    face_effect_id: int
    face_effect_type: int
    float_sc_resource_id: int
    giftId: int
    giftName: str
    giftType: int
    gold: int
    guard_level: int
    is_first: bool
    is_join_receiver: bool
    is_naming: bool
    is_special_batch: int
    magnification: int
    medal_info: MedalInfo
    name_color: str
    num: int
    original_gift_name: str
    price: int
    rcost: int
    receive_user_info: ReceiveUserInfo
    remain: int
    rnd: str
    send_master: Any
    silver: int
    super: int
    super_batch_gift_num: int
    super_gift_num: int
    svga_block: int
    switch: bool
    tag_image: str
    tid: str
    timestamp: int
    top_list: Any
    total_coin: int
    uid: int
    uname: str


class COMBO_SEND(DanmuItem):
    action: str
    batch_combo_id: str
    batch_combo_num: int
    combo_id: str
    combo_num: int
    combo_total_coin: int
    dmscore: int
    gift_id: int
    gift_name: str
    gift_num: int
    is_join_receiver: bool
    is_naming: bool
    is_show: int
    medal_info: MedalInfo
    name_color: str
    r_uname: str
    receive_user_info: ReceiveUserInfo
    ruid: int
    send_master: Any
    total_num: int
    uid: int
    uname: str


class ENTRY_EFFECT(DanmuItem):
    id: int
    uid: int
    target_id: int
    mock_effect: int
    face: str
    privilege_type: int
    copy_writing: str
    copy_color: str
    highlight_color: str
    priority: int
    basemap_url: str
    show_avatar: int
    effective_time: int
    web_basemap_url: str
    web_effective_time: int
    web_effect_close: int
    web_close_time: int
    business: int
    copy_writing_v2: str
    icon_list: List
    max_delay_time: int
    trigger_time: int
    identities: int
    effect_silent_time: int
    effective_time_new: int
    web_dynamic_url_webp: str
    web_dynamic_url_apng: str
    mobile_dynamic_url_webp: str


class Gift(BaseModel):
    gift_id: int
    gift_name: str
    num: int


class UserInfo(BaseModel):
    face: str
    face_frame: str
    guard_level: int
    is_main_vip: int
    is_svip: int
    is_vip: int
    level_color: str
    manager: int
    name_color: str
    title: str
    uname: str
    user_level: int


class SUPER_CHAT_MESSAGE(DanmuItem):
    background_bottom_color: str
    background_color: str
    background_color_end: str
    background_color_start: str
    background_icon: str
    background_image: str
    background_price_color: str
    color_point: float
    dmscore: int
    end_time: int
    gift: Gift
    id: int
    is_ranked: int
    is_send_audit: int
    medal_info: MedalInfo
    message: str
    message_font_color: str
    message_trans: str
    price: int
    rate: int
    start_time: int
    time: int
    token: str
    trans_mark: int
    ts: int
    uid: int
    user_info: UserInfo


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
    ulevel_rank: str
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


class GUARD_BUY(DanmuItem):
    uid: int
    username: str
    guard_level: int
    num: int
    price: int
    gift_id: int
    gift_name: str
    start_time: int
    end_time: int
