import math
from typing import List

import pandas as pd
from creart import it
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from src.database.models.danmu import DanmuType, Danmu
from src.analysis.chart import PieData, Pie, HistogramData, Line, Histogram, WordCloud
from src.analysis.danmu_utils import DanmuUtils
from src.config import Config, ConfigModel
from src.database.models.live import Live

jinja = Environment(loader=FileSystemLoader("templates"))


class LiveAnalysis:
    du: DanmuUtils
    live: Live
    config: ConfigModel

    def init(self, live: Live, danmus: List[Danmu]):
        self.live = live
        self.config = it(Config).config
        self.du = DanmuUtils()
        self.du.create(danmus, live.room_id)

    def _remove_no_value_gift(self, gifts):
        return [i for i in gifts if i["data"]["price"] != 0]

    def fill_zero_item(self, danmus: list):
        exist_times = [int(i.name) for i in danmus]
        for i in range(0, exist_times[-1] + 5):
            if i not in exist_times:
                danmus.append(HistogramData(name=str(i), value=0, category=""))
        danmus.sort(key=lambda x: int(x.name))
        return danmus

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

    def per_watch_time(self, interacted=False):
        if interacted:
            users = self.du.get_interact_audiences()
        else:
            users = self.du.get_audiences()
        user_watch_times = self.du.get_watch_time(self.live.start_time, self.live.end_time)
        watch_times = [j["watch_time"] for i, j in user_watch_times.items() if i in users]
        ave_watch_time = math.fsum(watch_times) / 3600 / len(users)
        return ave_watch_time

    def get_same_x_data(self, a: list[list], b: list[list]):
        a_x_set = set([i[0] for i in a])
        b_x_set = set([i[0] for i in b])
        same_x = a_x_set & b_x_set
        a_data = [i for i in a if i[0] in same_x]
        b_data = [i for i in b if i[0] in same_x]
        return a_data, b_data

    def convent_to_timing_data(self, start_time: int, data: list):
        for i in data:
            i[0] = round((i[0] - start_time) / 60)
        pd_data = pd.DataFrame(data, columns=["timestamp", "value"], dtype=pd.Float64Dtype)
        results = []
        for i in list(set(pd_data["timestamp"])):
            results.append([i, pd_data[pd_data["timestamp"] == i].sum()["value"]])
        results.sort(key=lambda x: x[0])
        return results

    def convent_to_averange_timing_data(self, start_time: int, data: list):
        for i in data:
            i[0] = round((i[0] - start_time) / 60)
        pd_data = pd.DataFrame(data, columns=["timestamp", "value"], dtype=pd.Float64Dtype)
        results = []
        for i in list(set(pd_data["timestamp"])):
            results.append([i, pd_data[pd_data["timestamp"] == i].mean()["value"]])
        results.sort(key=lambda x: x[0])
        return results

    async def generate_audience_compare(self, data=False):
        logger.info("Generating audience compare")
        per_interact_times = round(self.per_interact(), 2)
        per_interact_times_of_interact = round(self.per_interact(True), 2)
        per_danmu_times = round(self.per_danmus(), 2)
        per_danmu_times_of_interact = round(self.per_danmus(True), 2)
        per_watch_times = round(self.per_watch_time(), 2)
        per_watch_times_of_interact = round(self.per_watch_time(True), 2)
        chart_data = [HistogramData(name="人均互动条数", value=per_interact_times_of_interact, category="参与互动的观众"),
                HistogramData(name="人均互动条数", value=per_interact_times, category="所有观众"),
                HistogramData(name="人均弹幕条数", value=per_danmu_times_of_interact, category="参与互动的观众"),
                HistogramData(name="人均弹幕条数", value=per_danmu_times, category="所有观众"),
                HistogramData(name="人均观看时长", value=per_watch_times, category="所有观众"),
                HistogramData(name="人均观看时长", value=per_watch_times_of_interact, category="参与互动的观众")]
        if data:
            return chart_data
        audience_compare = Histogram().set_data(*chart_data).set_title("参与互动及未参与互动观众对比")
        audience_compare = await audience_compare.make()
        return audience_compare

    async def generate_medal_compare(self, data=False):
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
        if data:
            return results
        medal_compare = Histogram().set_data(*results).set_title("观众及粉丝团数据")
        medal_compare = await medal_compare.make()
        return medal_compare

    async def generate_word_frequency(self, data=False):
        logger.info("Generating word frequency")
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        chart_data = [HistogramData(name=str(name), value=value, category="") for name, value in
                      frequency.iloc[:15].items()]
        if data:
            return chart_data
        word_frequency = Histogram().set_data(*chart_data).set_title("词频统计")
        word_frequency = await word_frequency.make(orient="h")
        return word_frequency

    async def generate_wordcloud(self, data=False):
        logger.info("Generating wordcloud")
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        frequency_data = []
        for name, value in frequency.iloc[:100].items():
            frequency_data.append((str(name), value))
        if data:
            return frequency_data
        wordcloud = WordCloud().set_data(*frequency_data).set_title("弹幕词云")
        wordcloud = await wordcloud.make()
        return wordcloud

    async def generate_revenue_scale(self, data=False):
        logger.info("Generating revenue scale")
        revenues = {(0, 100): "≤100", (101, 999): "100-1000", (1000, 1e10): "≥1000"}
        results = []
        for i in revenues.keys():
            revenue = self.du.sum_earning(None, i)
            results.append(PieData(name=revenues[i], value=revenue))
        if data:
            return results
        revenue_scale = Pie().set_title("营收金额构成").set_data(*results)
        revenue_scale = await revenue_scale.make()
        return revenue_scale

    async def generate_revenue_type_scale(self, data=False):
        logger.info("Generating revenue type scale")
        revenue_types = {DanmuType.SuperChat: "超级留言", DanmuType.Guard: "舰长", DanmuType.Gift: "礼物"}
        results = []
        for i in revenue_types.keys():
            r_type = self.du.sum_earning(i)
            results.append(PieData(name=revenue_types[i], value=r_type))
        if data:
            return results
        revenue_type_scale = Pie().set_title("营收类型构成（以金额记）").set_data(*results)
        revenue_type_scale = await revenue_type_scale.make()
        return revenue_type_scale

    async def generate_revenue_type_scale_by_times(self, data=False):
        logger.info("Generating revenue type scale by times")
        revenue_types = {DanmuType.SuperChat: "超级留言", DanmuType.Guard: "舰长", DanmuType.Gift: "礼物"}
        results = []
        for i in revenue_types.keys():
            r_type = len(self._remove_no_value_gift(self.du.get_danmus_by_type(i)))
            results.append(PieData(name=revenue_types[i], value=r_type))
        if data:
            return results
        revenue_type_scale = Pie().set_title("营收类型构成（以数量记）").set_data(*results)
        revenue_type_scale = await revenue_type_scale.make()
        return revenue_type_scale

    async def generate_medal_scale(self, data=False):
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
        if data:
            return medal_scale_data
        medal_scale = Pie().set_title("粉丝团互动比例").set_data(*medal_scale_data)
        medal_scale = await medal_scale.make()
        return medal_scale

    async def generate_earning_timing(self, data=False):
        logger.info("Generating earning timing")
        earning_danmus = self.du.get_valuable_danmus()
        pre_timing_data = [[i["timestamp"], i["data"]["price"]] for i in earning_danmus]
        timing_data = self.convent_to_timing_data(self.live.start_time, pre_timing_data)
        chart_data = [HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data]
        if data:
            return chart_data
        earning_timing = Line().set_title("时序营收图").set_data(*chart_data)
        earning_timing = await earning_timing.make()
        return earning_timing

    async def generate_danmu_timing(self, data=False):
        logger.info("Generating danmu timing")
        danmus = self.du.get_danmu_msg()
        pre_timing_data = [[i["timestamp"], 1] for i in danmus]
        timing_data = self.convent_to_timing_data(self.live.start_time, pre_timing_data)
        chart_data = [HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data]
        if data:
            return chart_data
        danmu_timing = Line().set_title("时序弹幕图").set_data(*chart_data)
        danmu_timing = await danmu_timing.make()
        return danmu_timing

    async def generate_guard_timing(self, data=False):
        logger.info("Generating guard timing")
        guard_danmus = self.du.get_danmus_by_type(DanmuType.Guard)
        pre_timing_data = [[i["timestamp"], 1] for i in guard_danmus]
        timing_data = self.convent_to_timing_data(self.live.start_time, pre_timing_data)
        chart_data = self.fill_zero_item([HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data])
        if data:
            return chart_data
        guard_timing = Line().set_title("时序舰团图").set_data(*chart_data)
        guard_timing = await guard_timing.make()
        return guard_timing

    async def generate_superchat_timing(self, data=False):
        logger.info("Generating superchat timing")
        superchat_danmus = self.du.get_danmus_by_type(DanmuType.SuperChat)
        pre_timing_data = [[i["timestamp"], 1] for i in superchat_danmus]
        timing_data = self.convent_to_timing_data(self.live.start_time, pre_timing_data)
        chart_data = self.fill_zero_item([HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data])
        if data:
            return chart_data
        superchat_timing = Line().set_title("时序SC图").set_data(*chart_data)
        superchat_timing = await superchat_timing.make()
        return superchat_timing

    async def generate_paid_and_online_timing(self, data=False):
        logger.info("Generating paid and online count timing")
        paid_danmus = self.du.get_paid_count()
        online_danmus = self.du.get_online_count()
        paid_pre_timing_data = [[i["timestamp"], i["data"]["count"]] for i in paid_danmus]
        online_pre_timing_data = [[i["timestamp"], i["data"]["count"]] for i in online_danmus]
        paid_timing_data = self.convent_to_averange_timing_data(self.live.start_time, paid_pre_timing_data)
        online_timing_data = self.convent_to_averange_timing_data(self.live.start_time, online_pre_timing_data)
        paid_timing_data, online_timing_data = self.get_same_x_data(paid_timing_data, online_timing_data)
        chart_data = ([HistogramData(name=str(i[0]), value=i[1], category="高能用户") for i in paid_timing_data]
                      + [HistogramData(name=str(i[0]), value=i[1], category="同接") for i in online_timing_data])
        if data:
            return chart_data
        paid_and_online_timing = Line().set_title("高能用户与同接时序图").set_data(*chart_data)
        paid_and_online_timing = await paid_and_online_timing.make()
        return paid_and_online_timing

    async def generate_popular_rank_timing(self, data=False):
        logger.info("Generating popular rank timing")
        rank_danmus = self.du.get_danmus_by_type(DanmuType.PopularRank)
        pre_timing_data = [[i["timestamp"], i["data"]["rank"]] for i in rank_danmus]
        timing_data = self.convent_to_averange_timing_data(self.live.start_time, pre_timing_data)
        chart_data = [HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data]
        if data:
            return chart_data
        rank_timing = Line().set_title("高能榜时序图").set_data(*chart_data)
        rank_timing = await rank_timing.make(reverse_y=True)
        return rank_timing

    async def generate_like_timing(self, data=False):
        logger.info("Generating like timing")
        like_danmus = self.du.get_danmus_by_type(DanmuType.LikeCount)
        pre_timing_data = [[i["timestamp"], i["data"]["count"]] for i in like_danmus]
        timing_data = self.convent_to_averange_timing_data(self.live.start_time, pre_timing_data)
        chart_data = [HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data]
        if data:
            return chart_data
        like_timing = Line().set_title("点赞时序图").set_data(*chart_data)
        like_timing = await like_timing.make()
        return like_timing

    async def generate_watched_timing(self, data=False):
        logger.info("Generating watched timing")
        watched_danmus = self.du.get_danmus_by_type(DanmuType.WatchedCount)
        pre_timing_data = [[i["timestamp"], i["data"]["count"]] for i in watched_danmus]
        timing_data = self.convent_to_averange_timing_data(self.live.start_time, pre_timing_data)
        chart_data = [HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data]
        if data:
            return chart_data
        watched_timing = Line().set_title("看过时序图").set_data(*chart_data)
        watched_timing = await watched_timing.make()
        return watched_timing

    async def generate_followers_increment_timing(self, data=False):
        logger.info("Generating followers increment timing")
        follow_danmus = self.du.get_danmus_by_type(DanmuType.Follow)
        pre_timing_data = [[i["timestamp"], 1] for i in follow_danmus]
        timing_data = self.convent_to_averange_timing_data(self.live.start_time, pre_timing_data)
        chart_data = self.fill_zero_item([HistogramData(name=str(i[0]), value=i[1], category="") for i in timing_data])
        if data:
            return chart_data
        follow_timing = Line().set_title("粉丝增量时序图").set_data(*chart_data)
        follow_timing = await follow_timing.make()
        return follow_timing
