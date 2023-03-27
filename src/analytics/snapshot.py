# https://github.com/pyecharts/snapshot-selenium/blob/dev/snapshot_selenium/snapshot.py
# Add some argument to adapt linux

import os
import time
import platform
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from tenacity import retry, retry_if_exception_type, stop_after_attempt

SNAPSHOT_JS = """
    var ele = document.querySelector('div[_echarts_instance_]');
    var mychart = echarts.getInstanceByDom(ele);
    return mychart.getDataURL({
        type: '%s',
        pixelRatio: %s,
         excludeComponents: ['toolbox']
    });
"""

SNAPSHOT_SVG_JS = """
   var element = document.querySelector('div[_echarts_instance_] div');
   return element.innerHTML;
"""


@retry(retry=retry_if_exception_type(WebDriverException), stop=stop_after_attempt(3))
def make_snapshot(
        html_path: str,
        file_type: str,
        pixel_ratio: int = 2,
        delay: int = 2,
        browser="Chrome",
        driver: Any = None,
):
    if delay < 0:
        raise Exception("Time travel is not possible")
    if not driver:
        if browser == "Chrome":
            driver = get_chrome_driver()
        elif browser == "Safari":
            driver = get_safari_driver()
        else:
            raise Exception("Unknown browser!")

    if file_type == "svg":
        snapshot_js = SNAPSHOT_SVG_JS
    else:
        snapshot_js = SNAPSHOT_JS % (file_type, pixel_ratio)

    if not html_path.startswith("http"):
        html_path = "file://" + os.path.abspath(html_path)

    driver.get(html_path)
    time.sleep(delay)

    return driver.execute_script(snapshot_js)


def get_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    if platform.system() == "Linux":
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
    return webdriver.Chrome(options=options)


def get_safari_driver():
    return webdriver.Safari()
