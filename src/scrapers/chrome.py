from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import url_changes

from selenium.common.exceptions import NoSuchElementException


from config import SITES
from scrapers.base import BaseCrawler


class ChromeCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["CHROME"]
        super().__init__(url)

    def _get_latest_update(self):
        self.driver.get(self.url)

        while True:
            try:
                old_url = self.driver.current_url
                # 1) “Stable Channel Update for Desktop” 링크가 있는 post 컨테이너 찾기
                post = self.driver.find_element(
                    By.XPATH,
                    '//div[contains(@class,"post") and .//a[@title="Stable Channel Update for Desktop"]]',
                )
            except NoSuchElementException:
                try:
                    next_page = self.driver.find_element(
                        By.ID,
                        "Blog1_blog-pager-older-link",  # By.XPATH, '//*[@id="Blog1_blog-pager-older-link"]/i'
                    )
                    next_page.click()
                    WebDriverWait(self.driver, 10).until(url_changes(old_url))
                    continue
                except NoSuchElementException:
                    print("다음버튼 없음!")
                    raise

            # 2) 해당 컨테이너 안에서 publishdate 텍스트 추출
            date_text = post.find_element(By.CSS_SELECTOR, "span.publishdate").text.strip()
            #    e.g. "Wednesday, May 14, 2025"
            # 3) datetime.date 객체로 파싱
            date_obj = datetime.strptime(date_text, "%A, %B %d, %Y").date()
            next_day = date_obj + timedelta(days=1)  # 하루 더하기
            formatted_date = next_day.strftime("%Y/%m/%d")  # 날짜 객체 → 문자열
            print(formatted_date)

            link = post.find_element(By.XPATH, './/a[@title="Stable Channel Update for Desktop"]')
            href = link.get_attribute("href")
            return self._crawl_release_note(href, formatted_date)

    def _crawl_release_note(self, url, formatted_date):
        # 세부 페이지 들어가기
        self.driver.get(url)
        article = self.driver.find_element(By.CSS_SELECTOR, "div.post-content.post-original")

        version_text = article.find_elements(By.TAG_NAME, "p")

        match = re.search(r"(\d+\.\d+\.\d+)\.(\d+)/\.?(\d+)", version_text[0].text.strip())
        if not match:
            match = re.search(r"(\d+\.\d+\.\d+)\.\d+/\.?(\d+)", version_text[1].text.strip())
            if not match:
                raise RuntimeError("버전을 찾을 수 없습니다.!!!!")
        base, _, tail = match.groups()
        # head, tail = version_pair.split("/")
        # base = ".".join(head.split(".")[:-1])
        # version = f"{base}.{tail.lstrip('.')}"

        version = f"{base}.{tail}"

        print(version)
        return formatted_date, version


"""
chrome_version = ChromeCrawler()
try:
    chrome_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:
    chrome_version.close()
"""
