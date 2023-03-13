import io
import sys

import pandas as pd
from creart import it
from matplotlib.font_manager import fontManager
from wordcloud import wordcloud

from src.analytics.chart import Histogram, HistogramData, PieData, Pie
from src.analytics.danmu_utils import DanmuUtils
from src.config import Config
from src.database.database import Database
from src.database.models import DB_Types, Live


class Analysis:
    du: DanmuUtils

    async def init(self, live: Live):
        danmus = await it(Database).get_danmu(live)
        self.config = it(Config).config
        self.du = DanmuUtils()
        self.du.create(danmus, live.room_id)

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
        audience_compare = Histogram() \
            .set_data(HistogramData(name="人均互动条数", value=per_interact_times_of_interact, category="参与互动的观众"),
                      HistogramData(name="人均互动条数", value=per_interact_times, category="所有观众"),
                      HistogramData(name="人均弹幕条数", value=per_danmu_times_of_interact, category="参与互动的观众"),
                      HistogramData(name="人均弹幕条数", value=per_danmu_times, category="所有观众")) \
            .set_title("参与互动及未参与互动观众对比") \
            .make_histogram()
        return audience_compare

    def generate_medal_compare(self):
        levels = {(0, 0): "非粉丝团", (1, 5): "1-5", (6, 10): "6-10", (11, 20): "11-20", (21, 40): "21-40"}
        results = []
        for i in levels.keys():
            audiences = self.du.count_audience(i)
            danmus = self.du.count_danmus(i)
            interacts = self.du.count_interacts(i)
            results.append(HistogramData(name=levels[i], value=audiences, category="观众数量"))
            results.append(HistogramData(name=levels[i], value=danmus, category="弹幕数量"))
            results.append(HistogramData(name=levels[i], value=interacts, category="互动数量"))
        medal_compare = Histogram().set_data(*results).set_title("观众及粉丝团数据").make_histogram()
        return medal_compare

    def generate_word_frequency(self):
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        chart_data = [HistogramData(name=str(name), value=value, category="") for name, value in
                      frequency.iloc[:15].iteritems()]
        word_frequency = Histogram().set_data(*chart_data).set_title("词频统计").make_histogram(orient="h")
        return word_frequency

    def generate_wordcloud(self):
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        frequency_data = {}
        for name, value in frequency.iloc[:300].iteritems():
            frequency_data.update({str(name): value})
        if sys.platform == "win32":
            font_name = "SimHei"
        elif sys.platform == "linux":
            font_name = "Droid Sans Fallback"
        else:
            font_name = "Arial"
        font = fontManager.findfont(font_name)
        wc = wordcloud.WordCloud(font_path=font).generate_from_frequencies(frequency_data)
        img = io.BytesIO()
        wc.to_image().save(img)
        return img.getvalue()

    def generate_revenue_scale(self):
        revenues = {(0, 10): "≤10", (10, 100): "10-100", (100, 1e10): "≥100"}
        results = []
        for i in revenues.keys():
            revenue = self.du.sum_earning(None, i)
            results.append(PieData(name=revenues[i], value=revenue))
        revenue_scale = Pie().set_title("营收金额构成").set_data(*results).make_pie()
        return revenue_scale

    def generate_revenue_type_scale(self):
        revenue_types = {DB_Types.SuperChat: "超级留言", DB_Types.Guard: "舰长", DB_Types.Gift: "礼物"}
        results = []
        for i in revenue_types.keys():
            r_type = self.du.sum_earning(i)
            results.append(PieData(name=revenue_types[i], value=r_type))
        revenue_type_scale = Pie().set_title("营收类型构成").set_data(*results).make_pie()
        return revenue_type_scale

    def generate_report(self):
        pass
