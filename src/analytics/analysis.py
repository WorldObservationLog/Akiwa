import io
import sys
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

import pandas as pd
from creart import it
from matplotlib.font_manager import fontManager
from wordcloud import wordcloud
from jinja2 import Environment, FileSystemLoader

from src.analytics.chart import Histogram, HistogramData, PieData, Pie
from src.analytics.danmu_utils import DanmuUtils
from src.analytics.platforms import PLATFORM_MATCHES, Platform
from src.config import Config, ConfigModel
from src.database.models import DB_Types, Live, Danmu


jinja = Environment(loader=FileSystemLoader("templates"))


class Report:
    data: dict = {}
    live_title: str
    date: str

    def set_data(self, **kwargs):
        self.data.update(kwargs)
        return self

    def set_title(self, title: str):
        self.live_title = title
        return self

    def upload_images(self, platform: Platform):
        for i, j in self.data.copy().items():
            self.data[i] = platform.upload_image(img=j)

    def post_report(self, platform: str):
        self.date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%m-%d")
        platform_obj = PLATFORM_MATCHES[platform]()
        self.upload_images(platform_obj)
        template = jinja.get_template(name=it(Config).config.platform.find_platform_config(platform).template)
        report = template.render(report=self, platform=platform_obj)
        platform_obj.send_report(report, title=f"【{self.live_title}】{ self.date }直播数据统计报告")


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

    def generate_audience_compare(self):
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
                      frequency.iloc[:15].items()]
        word_frequency = Histogram().set_data(*chart_data).set_title("词频统计").make_histogram(orient="h")
        return word_frequency

    def generate_wordcloud(self):
        words = self.du.segment_danmu_text(self.config.jieba.words,
                                           self.config.jieba.ignore_words,
                                           self.config.jieba.stop_words)
        series = pd.Series(words)
        frequency = series.value_counts()
        frequency_data = {}
        for name, value in frequency.iloc[:300].items():
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
        wc.to_image().save(img, format="png")
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

    def post_report(self):
        audience_compare = self.generate_audience_compare()
        medal_compare = self.generate_medal_compare()
        word_frequency = self.generate_word_frequency()
        word_cloud = self.generate_wordcloud()
        revenue_scale = self.generate_revenue_scale()
        revenue_type_scale = self.generate_revenue_type_scale()
        report = Report().set_data(audience_compare=audience_compare,
                                   medal_compare=medal_compare,
                                   word_frequency=word_frequency,
                                   word_cloud=word_cloud,
                                   revenue_scale=revenue_scale,
                                   revenue_type_scale=revenue_type_scale) \
            .set_title(self.live.title)
        for i in self.config.platform.name:
            report.post_report(i)
