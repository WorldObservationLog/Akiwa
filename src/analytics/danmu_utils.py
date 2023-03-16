import math
from typing import List, Optional, Literal, Tuple

import jieba
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

from src.database.models import Danmu
from src.types import DB_Types


class DanmuUtils:
    db = TinyDB(storage=MemoryStorage)
    interact_types = [DB_Types.DanmuMsg, DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat]
    valuable_types = [DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat]
    danmu_query = Query()
    room_id: int

    def create(self, danmus: List[Danmu], room_id: int):
        self.db.insert_multiple(i.dict() for i in danmus)
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

    def get_interact_audiences(self):
        return list(set([i["uid"] for i in
                         self.db.search(self.danmu_query.type.one_of(self.interact_types))]))

    def count_audience(self, medal_level_range: Optional[tuple] = None):
        return len(self.get_audiences(medal_level_range))

    def count_interact_audiences(self):
        return len(self.get_interact_audiences())

    def count_danmus(self, medal_level_range: Optional[tuple] = None):
        return self.db.count(
            (self.danmu_query.type == DB_Types.DanmuMsg) & self._generate_medal_query(medal_level_range))

    def count_interacts(self, medal_level_range: Optional[tuple] = None):
        return self.db.count(
            (self.danmu_query.type.one_of(self.interact_types)) & self._generate_medal_query(
                medal_level_range))

    def sum_earning(self, gift_type: Literal[DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat, None] = None,
                    gift_price: Tuple[int, int] = None):
        gift_type_query = self.danmu_query.type.one_of(self.valuable_types) if not gift_type else self.danmu_query.type == gift_type
        gift_price_query = self.danmu_query.room_id.exists() if not gift_price else (self.danmu_query.data.price >= gift_price[0]) & (
                    self.danmu_query.data.price <= gift_price[1])
        valuable_danmus = self.db.search(gift_price_query & gift_type_query)
        return math.fsum(i["data"]["price"] for i in valuable_danmus)

    def get_danmu_msg(self):
        return self.db.search(self.danmu_query.type == DB_Types.DanmuMsg)

    def segment_danmu_text(self, words: list, ignore_words: list, stop_words: list):
        for i in words:
            jieba.suggest_freq(i, tune=True)
        result = []
        danmu_texts = [i["data"]["text"].upper() for i in self.get_danmu_msg()]
        filtered_danmu_texts = list(filter(lambda a: a not in ignore_words or (a.startswith("[") and a.endswith("]")), danmu_texts))
        for i in filtered_danmu_texts:
            result.extend(jieba.lcut(i))
        filtered_result = list(filter(lambda a: a not in stop_words, result))
        return filtered_result
