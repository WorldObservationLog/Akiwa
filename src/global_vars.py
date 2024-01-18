from bilibili_api import Credential
from creart import AbstractCreator, CreateTargetInfo, exists_module, it

from src.config import Config
from src.database.models.live import Live


class GlobalVars:
    live_status: bool = False
    credential: Credential = None
    current_live: list[Live] = []

    def __init__(self):
        self.credential = it(Config).config.account.to_credential()


class GlobalVarsCreator(AbstractCreator):
    targets = (CreateTargetInfo("src.global_vars", "GlobalVars"),)

    @staticmethod
    def available() -> bool:
        return exists_module("src.global_vars")

    @staticmethod
    def create(create_type: type[GlobalVars]) -> GlobalVars:
        return create_type()
