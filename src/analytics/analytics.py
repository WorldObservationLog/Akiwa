from typing import List
from creart import it
from src.analytics.types import AudienceAnalysis, OverallAudienceAnalysis
from src.config import Config

from src.database import Database
from src.types import Live, Commands

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
            if danmu.data.uid == uid:
                match danmu.command:
                    case Commands.ENTRY_EFFECT | Commands.SEND_GIFT | Commands.COMBO_SEND | Commands.SUPER_CHAT_MESSAGE:
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
                    case Commands.SEND_GIFT:
                        if danmu.data.price != 0.01:
                            a_ana.gift += 1
                            a_ana.revenue += danmu.data.price
                    case Commands.COMBO_SEND:
                        if (danmu.data.combo_total_coin / 1000 / danmu.data.combo_num) != 0.01:
                           a_ana.gift += danmu.data.combo_gift_num
                           a_ana.revenue += danmu.data.combo_total_coin / 1000
                    case Commands.GUARD_BUY:
                        a_ana.guard += 1
                        a_ana.revenue += danmu.data.price
                
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
    
    def get_overall_audience_analytics(audiences: List[AudienceAnalysis]):
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

