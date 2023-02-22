from decimal import Decimal, getcontext
from typing import List

from creart import it

from src.database.database import Database

db = it(Database)
getcontext().prec = 5


class LiveAnalysis:
    audiences: int = 0
    fans_change: int = 0
    medals_change: int = 0
    total_revenue: Decimal = Decimal(0)
    gift_revenue: Decimal = Decimal(0)
    superchat_revenue: Decimal = Decimal(0)
    guard_revenue: Decimal = Decimal(0)
    send_gift_times: int = 0
    live_duration: int = 0  # second
    danmus: int = 0
    guards: int = 0
    superchats: int = 0
    interact_times: int = 0
    average_danmu: float = 0.0
    average_interact: float = 0.0
    average_watchtime: float = 0.0
    interactor_average_danmu: float = 0.0
    interactor_average_interact: float = 0.0
    interactor_average_watchtime: float = 0.0


class AudienceAnalysis:
    uid: int = 0
    danmu: int = 0
    interact: int = 0
    superchat: int = 0
    guard: int = 0
    entry: int = 0
    gift: int = 0
    watchtime: int = 0
    revenue: Decimal = Decimal(0)
    medal_level: int = 0


class OverallAudienceAnalysis:
    interact_times: int = 0
    interactor_average_watchtime: Decimal = Decimal(0)
    total_watchtime: int = 0

    non_fans: int = 0
    # non_fans_interact_times: int
    non_fans_interact_message_times: int = 0
    non_fans_danmu_times: int = 0

    # 1-5
    primary_fans: int = 0
    # primary_fans_interact_times: int
    primary_fans_interact_message_times: int = 0
    primary_fans_danmu_times: int = 0

    # 6-10
    intermediate_fans: int = 0
    # intermediate_fans_interact_times: int
    intermediate_fans_interact_message_times: int = 0
    intermediate_fans_danmu_times: int = 0

    # 11-20
    senior_fans: int = 0
    # senior_fans_interact_times: int
    senior_fans_interact_message_times: int = 0
    senior_fans_danmu_times: int = 0

    # 21-40
    guard_fans: int = 0
    # guard_fans_interact_times: int
    guard_fans_interact_message_times: int = 0
    guard_fans_danmu_times: int = 0


class RevenueAnalysics:
    total: Decimal = Decimal(0)
    gift: Decimal = Decimal(0)
    superchat: Decimal = Decimal(0)
    guard: Decimal = Decimal(0)
    gift_with_time: List[dict] = []
    superchat_with_time: List[dict] = []
    guard_with_time: List[dict] = []
    # 0-10
    small_revenue: Decimal = Decimal(0)
    # 10-100
    medium_revenue: Decimal = Decimal(0)
    # 100+
    big_revenue: Decimal = Decimal(0)
