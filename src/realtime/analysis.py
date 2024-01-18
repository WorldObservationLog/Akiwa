from datetime import datetime

from creart import it
from tinydb import TinyDB

from src.analysis.live import LiveAnalysis
from src.analysis.danmu_utils import DanmuUtils
from src.config import Config
from src.database.models.live import Live


class RealtimeLiveAnalysis(LiveAnalysis):
    live: Live = None
    config = it(Config).config
    du = DanmuUtils()

    def init_from_database(self, live: Live, database: TinyDB):
        self.live = live
        self.du.create_from_database(database, live.room_id)
