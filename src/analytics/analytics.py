from dataclasses import dataclass
from creart import it
from src.database import Database

db = it(Database)


class LiveAnalysis:
    audiences: int
    fans_change: int
    medals_change: int
    total_revenue: float
    gift_revenue: float
    superchat_revenue: float
    guard_revenue: float
    send_gift_times: int
    live_duration: int # second
    danmus: int
    guards: int
    superchats: int
    interact_times: int
    average_danmu: float
    average_interact: float
    average_watchtime: float
    interactor_average_danmu: float
    interactor_average_interact: float
    interactor_average_watchtime: float


class AudienceAnalysis:
    uid: int
    danmu: int
    interact: int
    superchat: int
    guard: int
    entry: int
    gift: int
    watchtime: int
    revenue: float
    medal_level: int


class OverallAudienceAnalysis:
    interact_times: int
    interactor_average_watchtime: float
    total_watchtime: int

    non_fans: int
    non_fans_interact_times: int
    non_fans_interact_message_times: int
    non_fans_danmu_times: int

    primary_fans: int
    primary_fans_interact_times: int
    primary_fans_interact_message_times: int
    primary_fans_danmu_times: int

    intermediate_fans: int
    intermediate_fans_interact_times: int
    intermediate_fans_interact_message_times: int
    intermediate_fans_danmu_times: int

    senior_fans: int
    senior_fans_interact_times: int
    senior_fans_interact_message_times: int
    senior_fans_danmu_times: int

    guard_fans: int
    guard_fans_interact_times: int
    guard_fans_interact_message_times: int
    guard_fans_danmu_times: int






