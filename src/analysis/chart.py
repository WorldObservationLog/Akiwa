from io import BytesIO
from typing import List, Literal, Tuple

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud as WordCloudModule

from matplotlib.font_manager import fontManager, FontProperties
from pydantic import BaseModel
from creart import it

from src.config import Config
from src.utils import get_font_path

sns.set_style(it(Config).config.render.seaborn_style)
font_path = get_font_path(it(Config).config.render.font)
fontManager.addfont(font_path)
prop = FontProperties(fname=font_path)
sns.set(font=prop.get_name())


class Chart:
    def set_title(self, title: str):
        return NotImplemented

    def set_data(self, *data):
        return NotImplemented

    async def make(self):
        return NotImplemented

    async def render(self, chart_obj):
        with BytesIO() as f:
            chart_obj.savefig(f, format="png")
            plt.close(chart_obj)
            return f.getvalue()


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

    async def make(self):
        data = [i.value for i in self.data]
        labels = [i.name for i in self.data]
        pie = plt.figure()
        _, autotexts = plt.pie(data, labels=labels)
        for i, j in enumerate(autotexts):
            j.set_text(labels[i])
        plt.title(self.title)
        return await self.render(pie)


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

    async def make(self, orient: Literal["v", "h"] = "v"):
        categories = set()
        for i in self.data:
            categories.add(i.category)
        data = {self.hue: list(categories)}
        for i in self.data:
            data.update({i.name: []})
        for i in categories:
            for j in self.data:
                if j.category == i:
                    data[j.name].append(j.value)
        df = pd.DataFrame.from_dict(data)
        dfm = df.melt(id_vars=self.hue)
        histogram = plt.figure()
        if orient == "v":
            ax = sns.barplot(data=dfm, x='variable', y='value', hue=self.hue)
        else:
            ax = sns.barplot(data=dfm, x='value', y='variable', hue=self.hue, orient="h")
        ax.set(xlabel='', ylabel='')
        plt.title(self.title)
        return await self.render(histogram)


class WordCloud(Chart):
    data: List[Tuple[str, int]]
    title: str

    def set_data(self, *data):
        self.data = list(data)
        return self

    def set_title(self, title: str):
        self.title = title
        return self

    async def make(self):
        wc = WordCloudModule(font_path=it(Config).config.render.font_path, background_color="white")
        data = {}
        for i in self.data:
            data.update({i[0]: float(i[1])})
        wc.generate_from_frequencies(data)
        plt.title(self.title)
        return await self.render(wc)

    async def render(self, chart_obj: WordCloudModule):
        with BytesIO() as f:
            chart_obj.to_image().save(f, format="PNG")
            return f.getvalue()


class Line(Chart):
    data: List[HistogramData]
    title: str
    hue = "names"

    def set_data(self, *data):
        self.data = list(data)
        return self

    def set_title(self, title: str):
        self.title = title
        return self

    async def make(self, reverse_y: bool = False):
        data = {self.hue: list(set([i.name for i in self.data]))}
        data[self.hue].sort(key=lambda x: int(x))
        categories = set()
        for i in self.data:
            categories.add(i.category)
        for i in categories:
            data.update({i: []})
        for i in self.data:
            data[i.category].append(i.value)
        df = pd.DataFrame.from_dict(data)
        dfm = df.melt(id_vars="names")
        line = plt.figure(figsize=(15, 8))
        ax = sns.lineplot(dfm, x="names", y="value", hue="variable")
        ax.set(xlabel='', ylabel='')
        plt.title(self.title)
        plt.xticks(df['names'][::5])
        if reverse_y:
            ax.invert_yaxis()
        return await self.render(line)
