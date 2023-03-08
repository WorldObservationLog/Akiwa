import math

from typing import List, Optional, Literal
from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from src.database.models import Danmu, DB_Types


# noinspection PyTypeChecker
class DanmuUtils:
    db = TinyDB(storage=MemoryStorage)
    interact_types = [DB_Types.DanmuMsg, DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat]
    valuable_types = [DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat]
    danmu_query = Query()

    def create(self, danmus: List[Danmu]):
        self.db.insert_multiple(i.dict() for i in danmus)

    def get_audiences(self, medal_level_range: Optional[tuple] = None):
        if medal_level_range:
            return list(set([i["uid"] for i in self.db.search((self.danmu_query.medal is not None) &
                                                              (self.danmu_query.medal.level >= medal_level_range[0]) &
                                                              (self.danmu_query.medal.level < medal_level_range[1]))]))
        else:
            return list(set([i["uid"] for i in self.db.all()]))

    def get_interact_audiences(self):
        return list(set([i["uid"] for i in
                         self.db.search(self.danmu_query.type.test(lambda x: x in self.interact_types))]))

    def count_audience(self):
        return len(self.get_audiences())

    def count_interact_audiences(self):
        return len(self.get_interact_audiences())

    def count_danmus(self):
        return self.db.count(self.danmu_query.type == DB_Types.DanmuMsg)

    def count_interacts(self):
        return self.db.count(self.danmu_query.type.test(lambda x: x["type"] in self.interact_types))

    def sum_earning(self, gift_type: Literal[DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat, None] = None):
        if gift_type:
            valuable_danmus = self.db.search(self.danmu_query.type == gift_type)
        else:
            valuable_danmus = self.db.search(self.danmu_query.type.test(lambda x: x in self.valuable_types))
        return math.fsum(i["data"]["price"] for i in valuable_danmus)
