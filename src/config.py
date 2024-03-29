from typing import List, Optional

import tomli
from creart import exists_module
from creart.creator import AbstractCreator, CreateTargetInfo
from pydantic import BaseModel
from bilibili_api import Credential


class Listening(BaseModel):
    room: List[int]
    user: List[int]
    check_interval: int


class Jieba(BaseModel):
    words: List[str]
    ignore_words: List[str]
    stop_words: List[str]


class Render(BaseModel):
    seaborn_style: str
    font: str


class Service(BaseModel):
    host: str
    port: int


class Yomiuri(BaseModel):
    enable: bool
    token: str


class Account(BaseModel):
    sessdata: str
    bili_jct: str
    buvid3: str
    deaduserid: str
    ac_time_value: str

    def to_credential(self):
        return Credential(sessdata=self.sessdata, bili_jct=self.bili_jct, buvid3=self.buvid3,
                          dedeuserid=self.deaduserid, ac_time_value=self.ac_time_value)


class ConfigModel(BaseModel):
    listening: Listening
    jieba: Jieba
    account: Account
    render: Render
    service: Service
    yomiuri: Yomiuri
    conn_str: str
    database_name: str
    log_level: str
    schedule_interval: int
    commands: List[str]


class Config:
    config: ConfigModel

    def __init__(self) -> None:
        with open("config.toml", "rb") as f:
            self.config = ConfigModel.model_validate(tomli.load(f))


class ConfigCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.config", "Config"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.config")

    @staticmethod
    def create(create_type: type[Config]) -> Config:
        return create_type()
