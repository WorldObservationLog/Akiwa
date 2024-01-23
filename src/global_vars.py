import json
from pathlib import Path

from bilibili_api import Credential
from creart import AbstractCreator, CreateTargetInfo, exists_module, it

from src.config import Config
from src.database.models.live import Live


class GlobalVars:
    live_status: bool = False
    credential: Credential = None
    current_live: list[Live] = []

    def __init__(self):
        if Path("credential.json").exists():
            with open("credential.json", "r") as f:
                data = json.load(f)
                self.credential = Credential(sessdata=data["sessdata"], bili_jct=data["bili_jct"],
                                             buvid3=data["buvid3"], dedeuserid=data["deaduserid"],
                                             ac_time_value=data["ac_time_value"])
        else:
            self.credential = it(Config).config.account.to_credential()
            with open("credential.json", "w") as f:
                json.dump({"sessdata": self.credential.sessdata, "bili_jct": self.credential.bili_jct,
                           "buvid3": self.credential.buvid3, "deaduserid": self.credential.dedeuserid,
                           "ac_time_value": self.credential.ac_time_value}, f)


class GlobalVarsCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.global_vars", "GlobalVars"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.global_vars")

    @staticmethod
    def create(create_type: type[GlobalVars]) -> GlobalVars:
        return create_type()
