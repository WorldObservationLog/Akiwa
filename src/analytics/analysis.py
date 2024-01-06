import math
from typing import List

import pandas as pd
from creart import it
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from src.analytics.chart import Histogram, HistogramData, PieData, Pie, WordCloud, Line
from src.analytics.danmu_utils import DanmuUtils
from src.config import Config, ConfigModel
from src.database.models import DB_Types, Live, Danmu

jinja = Environment(loader=FileSystemLoader("templates"))


class Analysis:
    du: DanmuUtils
    live: Live
    config: ConfigModel

    def init(self, live: Live, danmus: List[Danmu]):
        danmus = danmus
        self.live = live
        self.config = it(Config).config
        self.du = DanmuUtils()
        self.du.create(danmus, live.room_id)


    def per_interact(self, interacted=False):
        if interacted:
            return self.du.count_interacts() / self.du.count_interact_audiences()
        else:
            return self.du.count_interacts() / self.du.count_audience()

    def per_danmus(self, interacted=False):
        if interacted:
            return self.du.count_danmus() / self.du.count_interact_audiences()
        else:
            return self.du.count_danmus() / self.du.count_audience()

    def convent_to_timing_data(self, start_time: int, data: list):
        for i in data:
            i[0] = round((i[0] - start_time) / 60)
        pd_data = pd.DataFrame(data, columns=["timestamp", "value"], dtype=pd.Float64Dtype)
        results = []
        for i in list(set(pd_data["timestamp"])):
            results.append([i, pd_data[pd_data["timestamp"] == i].sum()["value"]])
        results.sort(key=lambda x: x[0])
        return results

    async def generate_audience_compare(self):
        logger.info("Generating audience compare")
        per_interact_times = round(self.per_interact(), 2)
        per_interact_times_of_interact = round(self.per_interact(True), 2)
        per_danmu_times = round(self.per_danmus(), 2)
        per_danmu_times_of_interact = round(self.per_danmus(True), 2)
        audience_compare = Histogram() \
            .set_data(
            HistogramData(name="人均互动条数", value=per_interact_times_of_interact, category="参与互动的观众"),
            HistogramData(name="人均互动条数", value=per_interact_times, category="所有观众"),
            HistogramData(name="人均弹幕条数", value=per_danmu_times_of_interact, category="参与互动的观众"),
            HistogramData(name="人均弹幕条数", value=per_danmu_times, category="所有观众")) \
            .set_title("参与互动及未参与互动观众对比")
        audience_compare = await audience_compare.make()
        return audience_compare

    async def generate_medal_compare(self):
        logger.info("Generating medal compare")
        levels = {(0, 0): "非粉丝团", (1, 5): "1-5", (6, 10): "6-10", (11, 20): "11-20", (21, 40): "21-40"}
        results = []
        for i in levels.keys():
            audiences = self.du.count_audience(i)
            danmus = self.du.count_danmus(i)
            interacts = self.du.count_interacts(i)
            results.append(HistogramData(name=levels[i], value=audiences, category="观众数量"))
            results.append(HistogramData(name=levels[i], value=danmus, category="弹幕数量"))
            results.append(HistogramData(name=levels[i], value=interacts, category="互动数量"))
        medal_compare = Histogram().set_data(*results).set_title("观众及粉丝团数据")
        medal_compare = await medal_compare.make()
        return medal_compare

    async def generate_word_frequency(self):
        logger.info("Generating word frequency")
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        chart_data = [HistogramData(name=str(name), value=value, category="") for name, value in
                      frequency.iloc[:15].items()]
        word_frequency = Histogram().set_data(*chart_data).set_title("词频统计")
        word_frequency = await word_frequency.make(orient="h")
        return word_frequency

    async def generate_wordcloud(self):
        logger.info("Generating wordcloud")
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        frequency_data = []
        for name, value in frequency.iloc[:100].items():
            frequency_data.append((str(name), value))
        wordcloud = WordCloud().set_data(*frequency_data).set_title("弹幕词云")
        wordcloud = await wordcloud.make()
        return wordcloud

    async def generate_revenue_scale(self):
        logger.info("Generating revenue scale")
        revenues = {(0, 10): "≤10", (10, 100): "10-100", (100, 1e10): "≥100"}
        results = []
        for i in revenues.keys():
            revenue = self.du.sum_earning(None, i)
            results.append(PieData(name=revenues[i], value=revenue))
        revenue_scale = Pie().set_title("营收金额构成").set_data(*results)
        revenue_scale = await revenue_scale.make()
        return revenue_scale

    async def generate_revenue_type_scale(self):
        logger.info("Generating revenue type scale")
        revenue_types = {DB_Types.SuperChat: "超级留言", DB_Types.Guard: "舰长", DB_Types.Gift: "礼物"}
        results = []
        for i in revenue_types.keys():
            r_type = self.du.sum_earning(i)
            results.append(PieData(name=revenue_types[i], value=r_type))
        revenue_type_scale = Pie().set_title("营收类型构成").set_data(*results)
        revenue_type_scale = await revenue_type_scale.make()
        return revenue_type_scale

    async def generate_medal_scale(self):
        logger.info("Generating medal scale")
        interact_count = self.du.count_interacts()
        interact_medals = [i["medal"]["name"] if i["medal"] is not None and i["medal"]["name"] != "" else "无粉丝团" for
                           i in self.du.get_interact_danmus()]
        results = {"其他": 0.0}
        danmu_series = pd.Series(interact_medals)
        for i, j in danmu_series.value_counts().items():
            percent = j / interact_count
            if percent <= 0.05:
                results["其他"] = math.fsum([results["其他"], j])
            else:
                results.update({i: j})
        medal_scale_data = [PieData(name=i, value=j) for i, j in results.items()]
        medal_scale = Pie().set_title("粉丝团互动比例").set_data(*medal_scale_data)
        medal_scale = await medal_scale.make()
        return medal_scale

    async def generate_earning_timing(self):
        logger.info("Generating earning timing")
        earning_danmus = self.du.get_valuable_danmus()
        pre_timing_data = [[i["timestamp"], i["data"]["price"]] for i in earning_danmus]
        timing_data = self.convent_to_timing_data(self.live.start_time, pre_timing_data)
        chart_data = [HistogramData(name=i[0], value=i[1], category="") for i in timing_data]
        earning_timing = Line().set_title("时序营收图").set_data(*chart_data)
        earning_timing = await earning_timing.make()
        return earning_timing