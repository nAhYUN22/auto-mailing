from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import SITES
from scrapers.base import BaseCrawler


class FirefoxCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["FIREFOX"]
        super().__init__(url)

    def _get_latest_update(self):
        try:
            li_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
            )
            max_version = None
            version_pattern = re.compile(
                r"https://www\.mozilla\.org/en-US/firefox/(\d+\.\d+(\.\d+)?)/releasenotes/"
            )

            for li_element in li_elements:
                a_tag = li_element.find_element(By.TAG_NAME, "a")
                href = a_tag.get_attribute("href")
                if href:
                    match = version_pattern.match(href)
                    if match:
                        version_number = match.group(1)
                        if max_version is None or ((max_version) < version_number):
                            max_version = version_number
                        else:
                            break

            if max_version:
                new_patch_url = f"https://www.mozilla.org/en-US/firefox/{max_version}/releasenotes/"
                print(max_version)
                self.driver.get(new_patch_url)

                new_window = self.driver.window_handles[-1]
                self.driver.switch_to.window(new_window)

                # 패치 출시 날짜
                release_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p.c-release-date"))
                )
                release_date = self._format_datetime(release_element.text)
                print(release_date)
                release_note_contents = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "release-note-content"))
                )
            return release_date, max_version
        except Exception as e:
            print(f"신버전 패치 찾기 실패 {e}")

    def _format_datetime(self, crawl_date: str):
        date_obj = datetime.strptime(crawl_date, "%B %d, %Y")
        new_date_obj = date_obj + timedelta(days=1)
        new_date_str = new_date_obj.strftime("%Y/%m/%d")
        return new_date_str


"""
firefox_version = FirefoxCrawler()
try:
    firefox_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    firefox_version.close()
"""
