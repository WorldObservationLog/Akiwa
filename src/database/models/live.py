from beanie import Document


class Live(Document):
    live_id: str
    room_id: int
    title: str
    start_time: int
    end_time: int

    class Settings:
        name = "live"
