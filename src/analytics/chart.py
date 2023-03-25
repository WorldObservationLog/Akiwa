import tempfile
from typing import List, Literal, Tuple
from pathlib import Path
import uuid

from pyecharts.globals import SymbolType
from pyecharts.render import make_snapshot
from pyecharts.charts import Pie as ecPie
from pyecharts.charts import WordCloud as ecWordCloud
from pyecharts.charts import Bar
from pyecharts import options as opts
from pydantic import BaseModel

import .snapshot

class Chart:
    def set_title(self, title: str):
        return NotImplemented

    def set_data(self, *data):
        return NotImplemented

    def make(self):
        return NotImplemented

    def render(self, chart_obj):
        temp_dir = tempfile.TemporaryDirectory()
        temp_html = str((Path(temp_dir.name) / Path(str(uuid.uuid4()) + ".html")).absolute())
        chart = chart_obj.render(temp_html)
        temp_img = str((Path(temp_dir.name) / Path(str(uuid.uuid4()) + ".png")).absolute())
        make_snapshot(snapshot, chart, temp_img, pixel_ratio=1)
        img = open(temp_img, "rb").read()
        temp_dir.cleanup()
        return img


class PieData(BaseModel):
    name: str
    value: float

    def list(self):
        return [self.name, self.value]


class HistogramData(BaseModel):
    name: str
    value: float
    category: str

    def array(self):
        return [self.name, str(self.value), self.category]


class Pie(Chart):
    data: List[PieData]
    title: str

    def set_title(self, title):
        self.title = title
        return self

    def set_data(self, *data: PieData):
        self.data = list(data)
        return self

    def make(self):
        pie = ecPie(init_opts=opts.InitOpts(bg_color="#FFFFFF")) \
            .add("", [i.list() for i in self.data]) \
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title)) \
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        return self.render(pie)


class Histogram(Chart):
    data: List[HistogramData]
    title: str
    x: str = "name"
    y: str = "value"
    hue: str = "category"

    def set_data(self, *data: HistogramData):
        self.data = list(data)
        return self

    def set_title(self, title):
        self.title = title
        return self

    def make(self, orient: Literal["v", "h"] = "v"):
        histogram_data = {}
        for j in list(set([i.category for i in self.data])):
            values = [i for i in self.data if i.category == j]
            histogram_data.update({j: values})
        xaxis_data = list(set([i.name for i in self.data]))
        xaxis_data.sort(key=[i.name for i in self.data].index)
        histogram = Bar(init_opts=opts.InitOpts(bg_color="#FFFFFF")) \
            .add_xaxis(xaxis_data) \
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title))
        for i, j in histogram_data.items():
            histogram = histogram.add_yaxis(i, [opts.BarItem(name=k.name, value=k.value) for k in j])
        # for j in list(set([i.category for i in self.data])):
        #    values = [i.value for i in self.data if i.category == j]
        #    histogram = histogram.add_yaxis(j, values)
        if orient == "h":
            histogram = histogram.reversal_axis().set_series_opts(label_opts=opts.LabelOpts(position="right"))
        return self.render(histogram)


class WordCloud(Chart):
    data: List[Tuple[str, int]]
    title: str

    def set_data(self, *data):
        self.data = list(data)
        return self

    def set_title(self, title: str):
        self.title = title
        return self

    def make(self):
        wordcloud = ecWordCloud(init_opts=opts.InitOpts(bg_color="#FFFFFF")) \
            .add("", data_pair=self.data, word_size_range=[6, 66]) \
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title))
        return self.render(wordcloud)
