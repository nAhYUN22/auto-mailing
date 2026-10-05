from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import SITES
from scrapers.base import BaseCrawler


class AdobeCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["ADOBE"]
        super().__init__(url)

    def _get_latest_update(self):
        recent_date = self.driver.find_element(
            By.XPATH,
            '//*[@id="root_content_flex_items_position"]/div/div[16]/div/table/tbody/tr[2]/td[1]',
        )
        recent_date = recent_date.text.strip()
        date_obj = datetime.strptime(recent_date, "%b %d, %Y").date()
        next_day = date_obj + timedelta(days=1)  # 하루 더하기
        formatted_date = next_day.strftime("%Y/%m/%d")  # 날짜 객체 → 문자열
        print(formatted_date)

        version = self.crawl_last_version()

        return formatted_date, version

    def crawl_last_version(self):
        url = self.driver.find_element(
            By.XPATH,
            '//*[@id="root_content_flex_items_position"]/div/div[16]/div/table/tbody/tr[2]/td[2]/a',
        ).get_attribute("href")
        # 세부 페이지 들어가기
        self.driver.get(url)
        # version 찾기!!
        version_element = self.driver.find_element(By.TAG_NAME, "h1").text.strip()

        version_match = re.search(r"\d+\.\d+\.\d+\w", version_element)
        if version_match:
            version = version_match.group(0)
        else:
            print("Version number not found.")
            raise
        # 패치 파일 download link 찾기
        # X86
        # 1. <a class="reference external"> 모두 가져오기
        link_elements = self.driver.find_elements(By.CSS_SELECTOR, "table#id1 a.reference.external")
        # 2. href 속성만 추출해서 리스트로 만들기
        vendorurl_list = [a.get_attribute("href") for a in link_elements]
        # 만약 version 마지막 글자가 x라면, link에서 full version 파악해야 함.
        if "x" in version:
            number_match = re.search(r"/(\d{10})/", vendorurl_list[0])
            if number_match:
                number = number_match.group(1)
                version = f"{number[:2]}.{number[2:5]}.{number[5:]}"
            print(version)

        return version


"""
adobe_version = AdobeCrawler()
try:
    date = adobe_version._get_latest_update()
finally:
    adobe_version.close()
"""
