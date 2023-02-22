from typing import List

import tomli
from creart import exists_module
from creart.creator import AbstractCreator, CreateTargetInfo
from pydantic import BaseModel


class Listening(BaseModel):
    room: List[int]
    user: List[int]


class ConfigModel(BaseModel):
    listening: Listening
    conn_str: str
    commands: List[str]


class Config:
    config: ConfigModel

    def __init__(self) -> None:
        with open("config.toml", "rb") as f:
            self.config = ConfigModel.parse_obj(tomli.load(f))


class ConfigCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.config", "Config"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.config")

    @staticmethod
    def create(create_type: type[Config]) -> Config:
        return create_type()
