import os
import tempfile

from telegraph import Telegraph as Tel


class Platform:

    def upload_image(self, img: bytes) -> str:
        raise NotImplemented

    def send_report(self, report: str, title: str) -> str:
        raise NotImplemented


class Telegraph(Platform):
    telegraph: Tel

    def __init__(self):
        self.telegraph = Tel()
        self.telegraph.create_account("EOEDataGroup", "EOE数据组")

    def upload_image(self, img: bytes) -> str:
        tmp_img = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        tmp_img.write(img)
        tmp_img.close()
        resp = self.telegraph.upload_file(tmp_img.name)
        os.unlink(tmp_img.name)
        return resp[0]["src"]

    def send_report(self, report: str, title: str) -> str:
        resp = self.telegraph.create_page(title, html_content=report)
        return resp["url"]


PLATFORM_MATCHES = {"telegraph": Telegraph}
