import math

import jieba
import pandas as pd
from wordcloud import wordcloud

from typing import List, Optional, Literal
from functools import cache

from creart import it
from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from src.analytics.chart import Chart, ChartData
from src.database.database import Database
from src.database.models import Danmu, DB_Types, Live


# noinspection PyTypeChecker
class DanmuUtils:
    db = TinyDB(storage=MemoryStorage)
    interact_types = [DB_Types.DanmuMsg, DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat]
    valuable_types = [DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat]
    danmu_query = Query()

    def create(self, danmus: List[Danmu]):
        self.db.insert_multiple(i.dict() for i in danmus)

    def _generate_medal_query(self, medal_level_range: Optional[tuple] = None):
        if medal_level_range:
            medal_query = (self.danmu_query.medal != None) & (self.danmu_query.medal.level >= medal_level_range[0]) & (
                    self.danmu_query.medal.level < medal_level_range[1])
        else:
            medal_query = True
        return medal_query

    def get_audiences(self, medal_level_range: Optional[tuple] = None):
        if medal_level_range:
            return list(set([i["uid"] for i in self.db.search(self._generate_medal_query(medal_level_range))]))
        else:
            return list(set([i["uid"] for i in self.db.all()]))

    def get_interact_audiences(self):
        return list(set([i["uid"] for i in
                         self.db.search(self.danmu_query.type.test(lambda x: x in self.interact_types))]))

    def count_audience(self, medal_level_range: Optional[tuple] = None):
        return len(self.get_audiences(medal_level_range))

    def count_interact_audiences(self):
        return len(self.get_interact_audiences())

    def count_danmus(self, medal_level_range: Optional[tuple] = None):
        return self.db.count(
            (self.danmu_query.type == DB_Types.DanmuMsg) & self._generate_medal_query(medal_level_range))

    def count_interacts(self, medal_level_range: Optional[tuple] = None):
        return self.db.count(
            (self.danmu_query.type.test(lambda x: x["type"] in self.interact_types)) & self._generate_medal_query(
                medal_level_range))

    def sum_earning(self, gift_type: Literal[DB_Types.Gift, DB_Types.Guard, DB_Types.SuperChat, None] = None):
        if gift_type:
            valuable_danmus = self.db.search(self.danmu_query.type == gift_type)
        else:
            valuable_danmus = self.db.search(self.danmu_query.type.test(lambda x: x in self.valuable_types))
        return math.fsum(i["data"]["price"] for i in valuable_danmus)

    def get_danmu_msg(self):
        return self.db.search(self.danmu_query.type == DB_Types.DanmuMsg)

    def segment_danmu_text(self, words: list, ignore_words: list, stop_words: list):
        for i in words:
            jieba.suggest_freq(i, tune=True)
        result = []
        danmu_texts = [i["data"]["text"] for i in self.get_danmu_msg()]
        filtered_danmu_texts = list(filter(lambda a: a not in ignore_words, danmu_texts))
        for i in filtered_danmu_texts:
            result.extend(jieba.lcut(i))
        filtered_result = list(filter(lambda a: a not in stop_words, result))
        return filtered_result


class Analysis:
    du: DanmuUtils

    async def init(self, live: Live):
        danmus = await it(Database).get_danmu(live)
        self.du = DanmuUtils()
        self.du.create(danmus)

    def per_interact(self, interacted=False):
        if interacted:
            return self.du.count_interacts() / self.du.count_audience()
        else:
            return self.du.count_interacts() / self.du.count_interact_audiences()

    def per_danmus(self, interacted=False):
        if interacted:
            return self.du.count_danmus() / self.du.count_audience()
        else:
            return self.du.count_danmus() / self.du.count_interact_audiences()

    def generate_audience_compare(self):
        per_interact_times = self.per_interact()
        per_interact_times_of_interact = self.per_interact(True)
        per_danmu_times = self.per_danmus()
        per_danmu_times_of_interact = self.per_danmus(True)
        audience_compare = Chart() \
            .set_data(ChartData(name="人均互动条数", value=per_interact_times_of_interact, category="参与互动的观众"),
                      ChartData(name="人均互动条数", value=per_interact_times, category="所有观众"),
                      ChartData(name="人均弹幕条数", value=per_danmu_times_of_interact, category="参与互动的观众"),
                      ChartData(name="人均弹幕条数", value=per_danmu_times, category="所有观众")) \
            .set_title("参与互动/未参与互动观众对比") \
            .make_histogram()
        return audience_compare

    def generate_word_frequency(self):
        words = self.du.segment_danmu_text()
        series = pd.Series(words)
        frequency = series.value_counts()
        chart_data = [ChartData(name=str(name), value=value, category="") for name, value in
                      frequency.iloc[:15].iteritems()]
        word_frequency = Chart().set_data(*chart_data).set_title("词频统计").make_histogram(orient="h")
        return word_frequency

    def generate_wordcloud(self):
        words = self.du.segment_danmu_text()
        series = pd.Series(words)
        frequency = series.value_counts()
        frequency_data = {}
        for name, value in frequency.iloc[:300].iteritems():
            frequency_data.update({str(name): value})
        wordcloud.WordCloud().generate_from_frequencies(frequency_data)

    def generate_report(self):
        pass
