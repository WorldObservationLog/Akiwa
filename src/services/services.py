import asyncio
from datetime import datetime

from creart import it
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from quart import Quart, request
from quart_schema import QuartSchema, validate_response

from src.analysis.live import LiveAnalysis
from src.config import Config
from src.database.database import Database
from src.events import CollectorStartEvent
from src.global_vars import GlobalVars
from src.realtime.analysis import RealtimeLiveAnalysis
from src.realtime.database import RealtimeDatabase
from src.services.models import Live, Revenue, Response, Error, DataWithTimestamp

saya = Saya.current()
channel = Channel.current()
app = Quart(__name__)
QuartSchema(app)

db = it(Database)
config = it(Config)
global_vars = it(GlobalVars)
analysis: dict[str, LiveAnalysis] = {}
realtime_analysis = RealtimeLiveAnalysis()


async def check_analysis_exist(live_id):
    if live_id not in analysis:
        live = await db.get_live(live_id)
        if live.end_time == 0:
            live.end_time = int(datetime.timestamp(datetime.now()))
        ana = LiveAnalysis()
        ana.init(live, await db.get_danmu(live))
        analysis[live_id] = ana


async def check_realtime_analysis_exist(live_id):
    if not realtime_analysis.live:
        live = await db.get_live(live_id)
        realtime_analysis.init_from_database(live, it(RealtimeDatabase).db)


@channel.use(ListenerSchema(listening_events=[CollectorStartEvent]))
async def startup():
    loop = asyncio.get_running_loop()
    loop.create_task(app.run_task(host=config.config.service.host, port=config.config.service.port))


@app.route("/live/all")
@validate_response(Response)
async def get_lives():
    return Response(data=[Live(live_id=i.live_id, room_id=i.room_id, title=i.title,
                               start_time=i.start_time, end_time=i.end_time) for i in await db.get_lives()])


@app.route("/live/latest/<int:room_id>")
@validate_response(Response)
async def get_latest_live(room_id: int):
    latest_live = await db.get_latest_live(room_id)
    return Response(data=Live(live_id=latest_live.live_id, room_id=latest_live.room_id, title=latest_live.title,
                              start_time=latest_live.start_time, end_time=latest_live.end_time))


@app.route("/live/now")
@validate_response(Response)
async def get_streaming_live():
    if global_vars.current_live:
        results = [Live(live_id=live.live_id, room_id=live.room_id,
                        title=live.title, start_time=live.start_time,
                        end_time=live.end_time) for live in global_vars.current_live]
        return Response(data=results)
    else:
        return Response(data=None, error=Error("NO_LIVE", "There is not any live streaming now!"))


@app.route("/live/<live_id>/revenue")
@validate_response(Response)
async def get_revenue(live_id: str):
    await check_analysis_exist(live_id)
    return Response(data=Revenue(analysis[live_id].du.sum_earning()))


@app.route("/live/<live_id>/audience_compare")
@validate_response(Response)
async def get_audience_compare(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_audience_compare(data=True))
    return await analysis[live_id].generate_audience_compare()


@app.route("/live/<live_id>/medal_compare")
@validate_response(Response)
async def get_medal_compare(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_medal_compare(data=True))
    return await analysis[live_id].generate_medal_compare()


@app.route("/live/<live_id>/word_frequency")
@validate_response(Response)
async def get_word_frequency(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_word_frequency(data=True))
    return await analysis[live_id].generate_word_frequency()


@app.route("/live/<live_id>/word_cloud")
@validate_response(Response)
async def get_word_cloud(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_wordcloud(data=True))
    return Response(data=await analysis[live_id].generate_wordcloud())


@app.route("/live/<live_id>/revenue_scale")
@validate_response(Response)
async def get_revenue_scale(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_revenue_scale(data=True))
    return await analysis[live_id].generate_revenue_scale()


@app.route("/live/<live_id>/revenue_type_scale")
@validate_response(Response)
async def get_revenue_type_scale(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_revenue_type_scale(data=True))
    return await analysis[live_id].generate_revenue_type_scale()


@app.route("/live/<live_id>/revenue_type_scale_by_times")
@validate_response(Response)
async def get_revenue_type_scale_by_times(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_revenue_type_scale_by_times(data=True))
    return await analysis[live_id].generate_revenue_type_scale_by_times()


@app.route("/live/<live_id>/medal_scale")
@validate_response(Response)
async def get_medal_scale(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_medal_scale(data=True))
    return await analysis[live_id].generate_medal_scale()


@app.route("/live/<live_id>/earning_timing")
@validate_response(Response)
async def get_earning_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_earning_timing(data=True))
    return await analysis[live_id].generate_earning_timing()


@app.route("/live/<live_id>/danmu_timing")
@validate_response(Response)
async def get_danmu_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_danmu_timing(data=True))
    return await analysis[live_id].generate_danmu_timing()


@app.route("/live/<live_id>/guard_timing")
@validate_response(Response)
async def get_guard_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_guard_timing(data=True))
    return await analysis[live_id].generate_guard_timing()


@app.route("/live/<live_id>/superchat_timing")
@validate_response(Response)
async def get_superchat_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_superchat_timing(data=True))
    return await analysis[live_id].generate_superchat_timing()


@app.route("/live/<live_id>/paid_and_online_timing")
@validate_response(Response)
async def get_paid_and_online_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_paid_and_online_timing(data=True))
    return await analysis[live_id].generate_paid_and_online_timing()


@app.route("/live/<live_id>/popular_rank_timing")
@validate_response(Response)
async def get_popular_rank_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_popular_rank_timing(data=True))
    return await analysis[live_id].generate_popular_rank_timing()


@app.route("/live/<live_id>/like_timing")
@validate_response(Response)
async def get_like_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_like_timing(data=True))
    return await analysis[live_id].generate_like_timing()


@app.route("/live/<live_id>/watched_timing")
@validate_response(Response)
async def get_watched_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_watched_timing(data=True))
    return await analysis[live_id].generate_watched_timing()


@app.route("/live/<live_id>/followers_increment_timing")
@validate_response(Response)
async def get_followers_increment_timing(live_id: str):
    await check_analysis_exist(live_id)
    if request.args.get("data"):
        return Response(data=await analysis[live_id].generate_followers_increment_timing(data=True))
    return await analysis[live_id].generate_followers_increment_timing()


@app.route("/live/<live_id>/realtime/revenue")
@validate_response(Response)
async def get_realtime_revenue(live_id: str):
    await check_realtime_analysis_exist(live_id)
    return Response(data=Revenue(realtime_analysis.du.sum_earning()))


@app.route("/live/<live_id>/realtime/watched")
@validate_response(Response)
async def get_realtime_watched(live_id: str):
    await check_analysis_exist(live_id)
    watched = realtime_analysis.du.get_watched_counts()
    if watched:
        watched = watched[-1]
        return Response(data=DataWithTimestamp(timestamp=watched["timestamp"],
                                               value=watched["data"]["count"]))
    else:
        return Response(data=None, error=Error(type="NO_DATA", message="There is no data now!"))


@app.route("/live/<live_id>/realtime/paid")
@validate_response(Response)
async def get_realtime_paid(live_id: str):
    await check_analysis_exist(live_id)
    paid = realtime_analysis.du.get_paid_count()
    if paid:
        paid = paid[-1]
        return Response(data=DataWithTimestamp(timestamp=paid["timestamp"],
                                               value=paid["data"]["count"]))
    else:
        return Response(data=None, error=Error(type="NO_DATA", message="There is no data now!"))


@app.route("/live/<live_id>/realtime/online")
@validate_response(Response)
async def get_realtime_online(live_id: str):
    await check_analysis_exist(live_id)
    online = realtime_analysis.du.get_online_count()
    if online:
        online = online[-1]
        return Response(data=DataWithTimestamp(timestamp=online["timestamp"],
                                               value=online["data"]["count"]))
    else:
        return Response(data=None, error=Error(type="NO_DATA", message="There is no data now!"))


@app.route("/live/<live_id>/realtime/popular_rank")
@validate_response(Response)
async def get_realtime_rank(live_id: str):
    await check_analysis_exist(live_id)
    popular_rank = realtime_analysis.du.get_popular_rank()
    if popular_rank:
        popular_rank = popular_rank[-1]
        return Response(data=DataWithTimestamp(timestamp=popular_rank["timestamp"],
                                               value=popular_rank["data"]["rank"]))
    else:
        return Response(data=None, error=Error(type="NO_DATA", message="There is no data now!"))
