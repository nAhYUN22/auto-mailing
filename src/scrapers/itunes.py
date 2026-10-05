import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

from config import SITES
from scrapers.base import BaseCrawler


class ItunesCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["ITUNES"]
        super().__init__(url)

    def _format_datetime(self, crawl_date: str):
        for prefix in ["Released Date: ", "Released "]:
            if crawl_date.startswith(prefix):
                crawl_date = crawl_date.replace(prefix, "")
                break

        date_obj = datetime.strptime(crawl_date.strip(), "%B %d, %Y")
        new_date_obj = date_obj + timedelta(days=1)
        new_date_str = new_date_obj.strftime("%Y/%m/%d")
        return new_date_str

    def _get_latest_update(self):
        try:
            itunes_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'iTunes')]")
            document_url = itunes_link.get_attribute("href")
            title = itunes_link.text
            version = self._extract_version(title)
            print(version)

            self.driver.get(document_url)
            new_window = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_window)

            section = self.driver.find_element(By.ID, "sections")
            children = section.find_elements(By.XPATH, "./*")

            target_index = None

            for i, elem in enumerate(children):
                if elem.tag_name == "h2" and elem.text.strip() == title:
                    target_index = i
                    break

            for elem in children[target_index + 1 :]:
                tag = elem.tag_name

                if tag == "div" and "note" in elem.get_attribute("class"):
                    date_p = elem.find_element(By.TAG_NAME, "p")
                    if "Released" in date_p.text:
                        release_date = self._format_datetime(date_p.text)
                        print(release_date)

            return release_date, version
        except Exception as e:
            print(f"신버전 패치 크롤링 실패: {e}")

    def _extract_version(self, title: str):
        match = re.search(r"\d+(\.\d+)+", title)
        if match:
            version = match.group()
        return version


"""
itunes_version = ItunesCrawler()
try:
    itunes_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    itunes_version.close()
"""
