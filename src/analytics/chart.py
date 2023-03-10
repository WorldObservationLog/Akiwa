from io import BytesIO
from typing import List, Tuple, Literal

import seaborn as sns
import pandas as pd
import sys

from pydantic import BaseModel

sns.set_theme()

if sys.platform == "win32":
    sns.set(font="SimHei")
elif sys.platform == "linux":
    sns.set(font="Droid Sans Fallback")


class ChartData(BaseModel):
    name: str
    value: int | float
    category: str

    def array(self):
        return [self.name, self.value, self.category]


class Chart:
    data: pd.DataFrame
    title: str
    x: str = "name"
    y: str = "value"
    hue: str = "category"

    def set_data(self, *data: ChartData):
        self.data = pd.DataFrame([i.array() for i in data], columns=[self.x, self.y, self.hue])
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
        buf = BytesIO()
        barplot.get_figure().savefig(buf, format="png")
        buf.seek(0)
        return buf.read()
