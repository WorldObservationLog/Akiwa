from io import BytesIO
from typing import List, Literal

import seaborn as sns
import pandas as pd
import sys

from pydantic import BaseModel
import matplotlib.pyplot as plt

sns.set_theme()

if sys.platform == "win32":
    sns.set(font="SimHei")
elif sys.platform == "linux":
    sns.set(font="Droid Sans Fallback")


class PieData(BaseModel):
    name: str
    value: float


class HistogramData(BaseModel):
    name: str
    value: float
    category: str

    def array(self):
        return [self.name, str(self.value), self.category]


class Pie:
    data: List[PieData]
    title: str

    def set_title(self, title):
        self.title = title
        return self

    def set_data(self, *data: PieData):
        self.data = list(data)
        return self

    def make_pie(self):
        pie, _, labels = plt.pie([i.value for i in self.data], labels=[i.name for i in self.data], autopct="", textprops={'fontsize': 8})
        plt.title(self.title)
        for i, j in zip(labels, [i.value for i in self.data]):
            i.set_text(str(j))
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.clf()
        return buf.read()


class Histogram:
    data: pd.DataFrame
    title: str
    x: str = "name"
    y: str = "value"
    hue: str = "category"

    def set_data(self, *data: HistogramData):
        self.data = pd.DataFrame([i.array() for i in data], columns=[self.x, self.y, self.hue])
        self.data[[self.y]] = self.data[[self.y]].apply(pd.to_numeric)
        return self

    def set_title(self, title):
        self.title = title
        return self

    def make_histogram(self, orient: Literal["v", "h"] = "v"):
        if orient == "v":
            barplot = sns.barplot(data=self.data, x=self.x, y=self.y, hue=self.hue, orient=orient)
        else:
            barplot = sns.barplot(data=self.data, x=self.y, y=self.x, hue=self.hue, orient=orient)
        barplot.set_title(self.title)
        barplot.set(xlabel=None)
        barplot.set(ylabel=None)
        barplot.legend_.set_title(None)
        for container in barplot.containers:
            barplot.bar_label(container, fontsize=8)
        buf = BytesIO()
        barplot.get_figure().savefig(buf, format="png")
        buf.seek(0)
        plt.clf()
        return buf.read()
