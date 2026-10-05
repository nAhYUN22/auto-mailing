import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

from config import SITES
from scrapers.base import BaseCrawler


class EngineCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["ENGINE"]
        super().__init__(url)

    def _get_latest_update(self):
        date = self.driver.find_element(
            By.XPATH, '//*[@id="main"]/div[2]/div[1]/div[5]/ul[8]/li[2]/strong[1]'
        ).text
        print(date)

        # 괄호 및 이후 텍스트 제거
        date = date.split(" (")[0]
        formats = ["%B %d, %Y", "%b %d, %Y"]
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date, fmt).date()
            except ValueError:
                continue

        next_day = date_obj + timedelta(days=1)  # 하루 더하기
        formatted_date = next_day.strftime("%Y/%m/%d")  # 날짜 객체 → 문자열
        print(formatted_date)

        version = self.crawl_last_version()

        return formatted_date, version

    def crawl_last_version(self):

        version = (
            WebDriverWait(self.driver, 10)
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/div[2]/div[1]/div[5]/ul[8]/li[4]/strong',
                    )
                )
            )
            .text
        )
        print(version)
        return version


"""
engine_version = EngineCrawler()
try:
    engine_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    engine_version.close()
"""
