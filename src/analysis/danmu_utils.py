import math
import time
from functools import wraps
from typing import List, Optional, Literal, Tuple

import jieba
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

from src.database.models.danmu import DanmuType, Danmu


class DanmuUtils:
    db = TinyDB(storage=MemoryStorage)
    interact_types = [DanmuType.DanmuMsg, DanmuType.Gift, DanmuType.Guard, DanmuType.SuperChat, DanmuType.Follow]
    valuable_types = [DanmuType.Gift, DanmuType.Guard, DanmuType.SuperChat]
    danmu_query = Query()
    room_id: int

    def create(self, danmus: List[Danmu], room_id: int):
        self.db.insert_multiple(i.model_dump() for i in danmus)
        self.room_id = room_id

    def create_from_database(self, database: TinyDB, room_id: int):
        self.db = database
        self.room_id = room_id

    def _generate_medal_query(self, medal_level_range: Optional[tuple] = None):
        if medal_level_range:
            if medal_level_range == (0, 0):
                medal_query = (self.danmu_query.medal == None) | (self.danmu_query.medal.room_id != self.room_id)
            else:
                medal_query = (self.danmu_query.medal != None) & (self.danmu_query.medal.room_id == self.room_id) & (
                        self.danmu_query.medal.level >= medal_level_range[0]) & (
                                      self.danmu_query.medal.level <= medal_level_range[1])
        else:
            medal_query = self.danmu_query.medal.room_id != self.room_id
        return medal_query

    def get_audiences(self, medal_level_range: Optional[tuple] = None):
        if medal_level_range:
            return list(set([i["uid"] for i in self.db.search(self._generate_medal_query(medal_level_range))]))
        else:
            return list(set([i["uid"] for i in self.db.all()]))

    def get_valuable_danmus(self):
        return self.db.search(self.danmu_query.type.one_of(self.valuable_types))

    def get_interact_audiences(self):
        return list(set([i["uid"] for i in
                         self.db.search(self.danmu_query.type.one_of(self.interact_types))]))

    def count_audience(self, medal_level_range: Optional[tuple] = None):
        return len(self.get_audiences(medal_level_range))

    def count_interact_audiences(self):
        return len(self.get_interact_audiences())

    def count_danmus(self, medal_level_range: Optional[tuple] = None):
        return self.db.count(
            (self.danmu_query.type == DanmuType.DanmuMsg) & self._generate_medal_query(medal_level_range))

    def count_interacts(self, medal_level_range: Optional[tuple] = None):
        return self.db.count(
            (self.danmu_query.type.one_of(self.interact_types)) & self._generate_medal_query(
                medal_level_range))

    def sum_earning(self, gift_type: Literal[DanmuType.Gift, DanmuType.Guard, DanmuType.SuperChat, None] = None,
                    gift_price: Tuple[int, int] = None):
        gift_type_query = self.danmu_query.type.one_of(
            self.valuable_types) if not gift_type else self.danmu_query.type == gift_type
        gift_price_query = self.danmu_query.room_id.exists() if not gift_price else (self.danmu_query.data.price >=
                                                                                     gift_price[0]) & (
                                                                                            self.danmu_query.data.price <=
                                                                                            gift_price[1])
        valuable_danmus = self.db.search(gift_price_query & gift_type_query)
        return math.fsum(i["data"]["price"] for i in valuable_danmus)

    def get_danmu_msg(self):
        return self.db.search(self.danmu_query.type == DanmuType.DanmuMsg)

    def get_interact_danmus(self):
        return self.db.search(self.danmu_query.type.one_of(self.interact_types))

    def get_danmus_by_type(self, danmu_type: DanmuType):
        return self.db.search(self.danmu_query.type == danmu_type)

    def get_medals(self):
        return list(set([i["medal"]["name"] for i in self.db.search(self.danmu_query.medal != None) if
                         i["medal"]["name"] != ""]))

    def count_medal_interacts(self, medal_name):
        return self.db.count((self.danmu_query.medal != None) & (self.danmu_query.medal.name == medal_name))

    def segment_danmu_text(self, words: list, ignore_words: list, stop_words: list):
        for i in words:
            jieba.suggest_freq(i, tune=True)
        result = []
        danmu_texts = [i["data"]["text"].upper() for i in self.get_danmu_msg()]
        filtered_danmu_texts = list(
            filter(lambda a: a not in ignore_words or (a.startswith("[") and a.endswith("]")), danmu_texts))
        for i in filtered_danmu_texts:
            result.extend(jieba.lcut(i))
        filtered_result = list(filter(lambda a: a not in stop_words, result))
        return filtered_result

    def get_watched_counts(self):
        return self.get_danmus_by_type(DanmuType.WatchedCount)

    def get_paid_count(self):
        return self.get_danmus_by_type(DanmuType.PaidCount)

    def get_online_count(self):
        return self.get_danmus_by_type(DanmuType.OnlineCount)

    def get_popular_rank(self):
        return self.get_danmus_by_type(DanmuType.PopularRank)

    def get_user_watch_time(self, uid: int, start_time: int, end_time: int):
        user_danmus = self.db.search(self.danmu_query.uid == uid)
        user_danmus.sort(key=lambda x: x["timestamp"])
        live_time = end_time - start_time
        action = user_danmus[0]["type"]
        # 若用户首条弹幕为入场，则将此弹幕视为用户开始观看直播的时间
        if action == DanmuType.Entry:
            action_time = user_danmus[0]["timestamp"]
        # 若用户首条弹幕为互动，则视用户在直播开始前就已入场，将直播开始时间视为用户开始观看直播的时间
        else:
            action_time = start_time
        watch_time = 0
        for i in user_danmus[1:]:
            danmu_type = i["type"]
            match danmu_type:
                case DanmuType.Entry:
                    # 若用户上条弹幕为入场，本条弹幕为入场，则为上次记录300s观看时间（B站两次入场消息触发最低间隔600s)
                    if action == DanmuType.Entry:
                        watch_time += 300
                    # 若用户上条弹幕为入场，本条弹幕为互动，则全额记录
                    else:
                        watch_time += i["timestamp"] - action_time
                case danmu_type if danmu_type in self.interact_types:
                    # 若用户上条弹幕为互动，本条弹幕为互动/入场，则全额记录（入场估测为刷新直播间）
                    watch_time += i["timestamp"] - action_time
            action_time = i["timestamp"]
        # 若用户最后一条弹幕为入场，则视其继续观看了300s
        if action == DanmuType.Entry:
            add_time = 300
        # 若用户最后一条弹幕为互动，则视其继续观看了1/10的直播时长
        else:
            add_time = live_time / 10
        # 若最后一条弹幕估算出的最后时间大于结束时间，则视为观看到直播结束
        if action_time + add_time > end_time:
            watch_time += end_time - action_time
        else:
            watch_time += add_time
        return watch_time

    def get_watch_time(self, start_time, end_time):
        danmus = self.db.search(self.danmu_query.uid != None)
        danmus.sort(key=lambda x: x["timestamp"])
        live_time = end_time - start_time
        user_watch_times = {}
        watch_time_info = {"action": "", "action_time": 0, "watch_time": 0}
        for i in danmus:
            uid = i["uid"]
            danmu_type = i["type"]
            if not user_watch_times.get(uid):
                user_watch_times.update({uid: watch_time_info.copy()})
                if danmu_type == DanmuType.Entry:
                    user_watch_times[uid]["action_time"] = i["timestamp"]
                else:
                    user_watch_times[uid]["action_time"] = start_time
            user = user_watch_times[uid]
            match danmu_type:
                case DanmuType.Entry:
                    # 若用户上条弹幕为入场，本条弹幕为入场，则为上次记录300s观看时间（B站两次入场消息触发最低间隔600s)
                    if user["action"] == DanmuType.Entry:
                        user["watch_time"] += 300
                    # 若用户上条弹幕为入场，本条弹幕为互动，则全额记录
                    else:
                        user["watch_time"] += (i["timestamp"] - user["action_time"])
                case danmu_type if danmu_type in self.interact_types:
                    # 若用户上条弹幕为互动，本条弹幕为互动/入场，则全额记录（入场估测为刷新直播间）
                    user["watch_time"] += (i["timestamp"] - user["action_time"])
            user["action_time"] = i["timestamp"]
            user["action"] = i["type"]
        for _, user in user_watch_times.items():
            # 若用户最后一条弹幕为入场，则视其继续观看了300s
            if user["action"] == DanmuType.Entry:
                add_time = 300
                # 若用户最后一条弹幕为互动，则视其继续观看了1/10的直播时长
            else:
                add_time = live_time / 10
                # 若最后一条弹幕估算出的最后时间大于结束时间，则视为观看到直播结束
            if user["action_time"] + add_time > end_time:
                user["watch_time"] += end_time - user["action_time"]
            else:
                user["watch_time"] += add_time
        return user_watch_times
