import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta


from config import SITES
from scrapers.base import BaseCrawler


class Adobe2020Crawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["ADOBE"]
        super().__init__(url)

    def _get_latest_update(self):  # 날짜
        # ID로 섹션 타이틀 찾기
        section = self.driver.find_element(
            By.ID, "Acrobat2017andAcrobatReader2017ClassicTrackreleasenotes"
        )

        # 섹션 다음에 나오는 테이블을 찾기 위해 부모에서 다음 요소 탐색
        table = section.find_element(By.XPATH, "following::table[1]")

        # 테이블의 두 번째 행 첫 번째 열 (날짜)
        recent_date = table.find_element(By.XPATH, ".//tr[2]/td[1]")
        recent_date = recent_date.get_attribute("textContent")
        recent_date = recent_date.splitlines()[0].strip()
        # recent_date = recent_date.text.strip()

        date_obj = datetime.strptime(recent_date, "%b %d, %Y").date()
        next_day = date_obj + timedelta(days=1)  # 하루 더하기
        formatted_date = next_day.strftime("%Y/%m/%d")  # 날짜 객체 → 문자열
        print(formatted_date)

        version = self.crawl_last_version()

        return date_obj, version

    def crawl_last_version(self):
        # 세부 페이지 크롤링
        # ID로 섹션 타이틀 찾기
        section = self.driver.find_element(
            By.ID, "Acrobat2017andAcrobatReader2017ClassicTrackreleasenotes"
        )

        # 섹션 다음에 나오는 테이블을 찾기 위해 부모에서 다음 요소 탐색
        table = section.find_element(By.XPATH, "following::table[1]")

        # 테이블의 두 번째 행 첫 번째 열 (날짜)
        url = table.find_element(By.XPATH, ".//tr[2]/td[2]/a").get_attribute("href")
        # 세부 페이지 들어가기
        self.driver.get(url)
        # version 찾기!!
        version_element = self.driver.find_element(By.TAG_NAME, "h1").text.strip()

        version_match = re.search(r"\d+\.\d+\.\d+\w", version_element)
        if version_match:
            version = version_match.group(0)
            print(f"버전: {version}")
        else:
            print("Version number not found.")
            raise
        # 패치 파일 download link 찾기
        # window installer
        # 1. <a class="reference external"> 모두 가져오기
        link_element = self.driver.find_element(By.CSS_SELECTOR, "table#id1 a.reference.external")
        # 2. href 속성만 추출해서 리스트로 만들기
        vendorurl_list = [link_element.get_attribute("href")]

        # 만약 version 마지막 글자가 x라면, link에서 full version 파악해야 함.
        if "x" in version:
            number_match = re.search(r"/(\d{10})/", vendorurl_list[0])
            if number_match:
                number = number_match.group(1)
                version = f"{number[:2]}.{number[2:5]}.{number[5:]}"

        return version


"""
adobe_version = Adobe2020Crawler()
try:
    adobe_version._get_latest_update()
finally:
    adobe_version.close()
"""
