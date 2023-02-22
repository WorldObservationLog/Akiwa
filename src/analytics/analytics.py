from decimal import Decimal
from typing import List
from creart import it
from loguru import logger
from src.analytics.types import AudienceAnalysis, LiveAnalysis, OverallAudienceAnalysis, RevenueAnalysics
from src.config import Config

from src.database.database import Database
from src.database.models import DB_TYPE_MATCHES
from src.types import SEND_GIFT, Live, Commands

db = it(Database)
config = it(Config).config

class Analytics:

    async def init(self, live: Live):
        self.live = live
        self.danmus = await db.get_danmu(live)

    def get_audience_analytics(self, uid: int):
        a_ana = AudienceAnalysis()
        a_ana.uid = uid
        interact_sign = "START"
        audience_latest_time = self.live.start_time

        for danmu in self.danmus:
            if danmu.command in DB_TYPE_MATCHES.keys():
                if danmu.data.uid == uid:
                    match danmu.command:
                        case Commands.SEND_GIFT | Commands.COMBO_SEND | Commands.SUPER_CHAT_MESSAGE:
                            if danmu.data.medal_info.anchor_roomid in config.listening.room:
                                if a_ana.medal_level < danmu.data.medal_info.medal_level:
                                    a_ana.medal_level = danmu.data.medal_info.medal_level
                        case Commands.DANMU_MSG:
                            if danmu.data.medal_room_id in config.listening.room:
                                if a_ana.medal_level < danmu.data.medal_level:
                                    a_ana.medal_level = danmu.data.medal_level
                        case Commands.INTERACT_WORD:
                            if danmu.data.fans_medal.anchor_roomid in config.listening.room:
                                if a_ana.medal_level < danmu.data.fans_medal.medal_level:
                                    a_ana.medal_level = danmu.data.fans_medal.medal_level
                    match danmu.command:
                        case Commands.INTERACT_WORD:
                            a_ana.entry += 1
                        case Commands.ENTRY_EFFECT:
                            a_ana.entry += 1
                        case Commands.DANMU_MSG:
                            a_ana.danmu += 1
                        case Commands.SUPER_CHAT_MESSAGE:
                            a_ana.superchat += 1
                            a_ana.revenue += danmu.data.price
                        case Commands.SEND_GIFT:
                            if Decimal(danmu.data.price) / 1000 != 0.01:
                                a_ana.gift += 1
                                a_ana.revenue += Decimal(danmu.data.price)
                        case Commands.COMBO_SEND:
                            if (danmu.data.combo_total_coin) / 1000 / danmu.data.combo_num != 0.01:
                                a_ana.gift += danmu.data.combo_num
                                a_ana.revenue += Decimal(danmu.data.combo_total_coin) / 1000
                        case Commands.GUARD_BUY:
                            a_ana.guard += 1
                            a_ana.revenue += Decimal(danmu.data.price) / 1000
                
                    match interact_sign:
                        case "START":
                            if danmu.command in [Commands.INTERACT_WORD, Commands.ENTRY_EFFECT]:
                                audience_latest_time = danmu.timestamp
                                interact_sign = "ENTRY"
                            else:
                                interact_sign = "INTERACT"
                        case "ENTRY":
                            if danmu.command in [Commands.INTERACT_WORD, Commands.ENTRY_EFFECT]:
                                a_ana.watchtime += 300
                                audience_latest_time = danmu.timestamp
                            else:
                                a_ana.watchtime += danmu.timestamp - audience_latest_time
                                audience_latest_time = danmu.timestamp
                                interact_sign = "INTERACT"
                        case "INTERACT":
                            a_ana.watchtime += danmu.timestamp - audience_latest_time
                            audience_latest_time = danmu.timestamp
                            interact_sign = "ENTRY"
        if interact_sign == "INTERACT":
            add_time = int((self.live.end_time - self.live.start_time) / 10)
        else:
            add_time = 300
        detla_time = self.live.end_time - self.danmus[-1].timestamp
        if add_time < detla_time:
            a_ana.watchtime += add_time
        else:
            a_ana.watchtime += detla_time

        a_ana.interact = a_ana.danmu + a_ana.gift + a_ana.superchat + a_ana.guard

        return a_ana
    
    def get_overall_audience_analytics(self, audiences: List[AudienceAnalysis]):
        oa_ana = OverallAudienceAnalysis()
        for ana in audiences:
            oa_ana.total_watchtime += ana.watchtime
            if ana.interact:
                oa_ana.interact_times += 1
                oa_ana.interactor_average_watchtime += ana.watchtime
            match ana.medal_level:
                case 0:
                    oa_ana.non_fans += 1
                    oa_ana.non_fans_interact_message_times += ana.interact
                    oa_ana.non_fans_danmu_times += ana.danmu
                case num if 1 <= num < 6:
                   oa_ana.primary_fans += 1
                   oa_ana.primary_fans_interact_message_times += ana.interact
                   oa_ana.primary_fans_danmu_times += ana.danmu
                case num if 6 <= num < 11:
                    oa_ana.intermediate_fans += 1
                    oa_ana.intermediate_fans_interact_message_times += ana.interact
                    oa_ana.intermediate_fans_danmu_times += ana.danmu
                case num if 11 <= num < 21:
                    oa_ana.senior_fans += 1
                    oa_ana.senior_fans_interact_message_times += ana.interact
                    oa_ana.senior_fans_danmu_times += ana.danmu
                case num if 21 <= num <= 40:
                    oa_ana.guard_fans += 1
                    oa_ana.guard_fans_interact_message_times += ana.interact
                    oa_ana.guard_fans_danmu_times += ana.danmu
        return oa_ana
    
    def get_revenge_analytics(self):
        r_ana = RevenueAnalysics()
        for danmu in self.danmus:
            match danmu.command:
                case Commands.SEND_GIFT:
                    price = Decimal(danmu.data.price) / 1000
                    if price != 0.01:
                        r_ana.total += price
                        r_ana.gift += price
                        r_ana.gift_with_time.append(
                                {"time": danmu.timestamp - self.live.start_time,
                                 "price": price}
                                )
                        if price <= 10:
                            r_ana.small_revenue += price
                        elif price <= 100:
                            r_ana.medium_revenue += price
                        else:
                            r_ana.big_revenue += price
                case Commands.COMBO_SEND:
                    price = Decimal(danmu.data.combo_total_coin / 1000)
                    if (price / danmu.data.combo_num) != 0.01:
                        r_ana.total += price
                        r_ana.gift += price
                        r_ana.gift_with_time.append({"time": danmu.timestamp - self.live.start_time,
                                                     "price": price})
                        if price <= 10:
                            r_ana.small_revenue += price
                        elif price <= 100:
                            r_ana.medium_revenue += price
                        else:
                            r_ana.big_revenue += price
                case Commands.SUPER_CHAT_MESSAGE:
                    r_ana.total += Decimal(danmu.data.price)
                    r_ana.superchat += Decimal(danmu.data.price)
                    r_ana.superchat_with_time.append({"time": danmu.timestamp - self.live.start_time,
                                                      "price": Decimal(danmu.data.price)})
                    if Decimal(danmu.data.price) <= 10:
                        r_ana.small_revenue += Decimal(danmu.data.price)
                    elif Decimal(danmu.data.price) <= 100:
                        r_ana.medium_revenue += Decimal(danmu.data.price)
                    else:
                        r_ana.big_revenue += Decimal(danmu.data.price)
                case Commands.GUARD_BUY:
                    price = Decimal(danmu.data.price) / 1000
                    r_ana.total += price
                    r_ana.guard += price
                    r_ana.guard_with_time.append({"time": danmu.timestamp - self.live.start_time,
                                                  "price": price})
                    if price <= 10:
                        r_ana.small_revenue += price
                    elif price <= 100:
                        r_ana.medium_revenue += price
                    else:
                        r_ana.big_revenue += price
        return r_ana

    def get_live_analytics(self):
        l_ana = LiveAnalysis()
        audiences = []
        for danmu in self.danmus:
            if danmu.command in DB_TYPE_MATCHES.keys():
                if not danmu.data.uid in audiences:
                    audiences.append(danmu.data.uid)
        interactors = []
        for danmu in self.danmus:
            if danmu.command in [Commands.DANMU_MSG, Commands.SUPER_CHAT_MESSAGE, Commands.GUARD_BUY, Commands.COMBO_SEND, Commands.SEND_GIFT]:
                if not danmu.data.uid in interactors:
                    interactors.append(danmu.data.uid)
        r_ana = self.get_revenge_analytics()
        a_anas = [self.get_audience_analytics(i) for i in audiences]
        o_ana = self.get_overall_audience_analytics(a_anas)
        danmu_msg = [i for i in self.danmus if i.command == Commands.DANMU_MSG]
        guard_msg = [i for i in self.danmus if i.command == Commands.GUARD_BUY]
        superchat_msg = [i for i in self.danmus if i.command == Commands.SUPER_CHAT_MESSAGE]

        l_ana.audiences = len(audiences)
        l_ana.total_revenue = r_ana.total
        l_ana.superchat_revenue = r_ana.superchat
        l_ana.guard_revenue = r_ana.guard
        l_ana.gift_revenue = r_ana.gift
        l_ana.send_gift_times = len(r_ana.gift_with_time)
        l_ana.live_duration = self.live.end_time - self.live.start_time
        l_ana.danmus = len(danmu_msg)
        l_ana.guards = len(guard_msg)
        l_ana.superchats = len(superchat_msg)
        l_ana.interact_times = o_ana.interact_times
        l_ana.average_danmu = len(danmu_msg) / len(audiences)
        l_ana.average_interact = o_ana.interact_times / len(audiences)
        l_ana.average_watchtime = o_ana.total_watchtime / len(audiences)
        l_ana.interactor_average_danmu = len(danmu_msg) / len(interactors)
        l_ana.interactor_average_interact = o_ana.interact_times / len(interactors)
        l_ana.interactor_average_watchtime = float(o_ana.interactor_average_watchtime)

        return l_ana
