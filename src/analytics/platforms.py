import os
import tempfile
from io import BytesIO
from typing import Optional

import httpx
from bilibili_api import Credential
from creart import it
from pydantic import BaseModel
from telegraph import Telegraph as Tel

from src.config import Config


class Platform:

    async def upload_image(self, img: bytes) -> str:
        raise NotImplemented

    async def send_report(self, report: str, title: str) -> str:
        raise NotImplemented


class Telegraph(Platform):
    telegraph: Tel

    def __init__(self):
        self.telegraph = Tel()
        self.telegraph.create_account("Akiwa")

    async def upload_image(self, img: bytes) -> str:
        tmp_img = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        tmp_img.write(img)
        tmp_img.close()
        resp = self.telegraph.upload_file(tmp_img.name)
        os.unlink(tmp_img.name)
        return resp[0]["src"]

    async def send_report(self, report: str, title: str) -> str:
        resp = self.telegraph.create_page(title, html_content=report)
        return resp["url"]


class PostArticleModel(BaseModel):
    title: str
    content: str
    summary: str
    words: int
    tid: int
    aid: int
    csrf: str

    category: int = 0
    list_id: int = 0
    banner_url: Optional[str]
    reprint: int = 0
    tags: Optional[str]
    image_urls: Optional[str]
    origin_image_urls: Optional[str]
    dynamic_intro: Optional[str]
    media_id: int = 0
    spoiler: int = 0
    original: int = 0
    top_video_bvid: Optional[str]
    up_reply_closed: int = 0
    comment_selected: int = 0
    publish_time: int = 0
    items: Optional[str]
    platform: str = "web"
    buvid: Optional[str]
    device: Optional[str]
    build: Optional[str]
    mobi_app: Optional[str]


class GetAidModel(BaseModel):
    title: str
    banner_url: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    words: Optional[str] = None
    category: Optional[str] = None
    list_id: Optional[str] = None
    tid: Optional[str] = None
    reprint: Optional[str] = None
    tags: Optional[str] = None
    image_urls: Optional[str] = None
    origin_image_urls: Optional[str] = None
    dynamic_intro: Optional[str] = None
    media_id: Optional[str] = None
    spoiler: Optional[str] = None
    original: Optional[str] = None
    top_video_bvid: Optional[str] = None
    csrf: str


class Bilibili(Platform):
    user: Credential

    def __init__(self):
        config = it(Config).config.platform.find_platform_config("bilibili").data
        self.user = Credential(bili_jct=config["bili_jct"],
                               buvid3=config["buvid3"],
                               sessdata=config["sessdata"],
                               dedeuserid=config["deduserid"])

    def get_aid(self):
        endpoint = "https://api.bilibili.com/x/article/creative/draft/addupdate"
        resp = httpx.post(endpoint, data=GetAidModel(title="Akiwa Report", csrf=self.user.bili_jct).dict(),
                          cookies=self.user.get_cookies()).json()
        # 懒得转成模型了
        return resp["data"]["aid"]

    async def upload_image(self, img: bytes) -> str:
        endpoint = "https://api.bilibili.com/x/article/creative/article/upcover"
        resp = httpx.post(endpoint, data={"csrf": self.user.bili_jct}, files={"binary": BytesIO(img)},
                          cookies=self.user.get_cookies()).json()
        return resp["data"]["url"]

    async def send_report(self, report: str, title: str) -> str:
        endpoint = "https://api.bilibili.com/x/article/creative/article/submit"
        config = it(Config).config.platform.find_platform_config("bilibili").data
        resp = httpx.post(endpoint,
                          data=PostArticleModel(title=title, content=report, summary="Akiwa Live Report", words=100,
                                                tid=4,
                                                aid=self.get_aid(), csrf=self.user.bili_jct,
                                                build=self.user.buvid3,
                                                tags=config["tags"]).dict(),
                          cookies=self.user.get_cookies()).json()
        return ""


PLATFORM_MATCHES = {"telegraph": Telegraph, "bilibili": Bilibili}
