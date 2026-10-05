import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

from config import SITES
from scrapers.base import BaseCrawler


class EdgeCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["EDGE"]
        super().__init__(url)

    def _update_date(self):
        now = datetime.now()
        formatted_date = now.strftime("%Y/%m/%d")
        print(formatted_date)
        return formatted_date

    def _get_latest_update(self):
        self.driver.get(self.url)

        # p.enterprise-latest__release-card-version 이 나타날 때까지 최대 10초 대기
        version = (
            WebDriverWait(self.driver, 10)
            .until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "p.enterprise-latest__release-card-version")
                )
            )
            .text
        )
        print(version)

        date = self._update_date()

        return date, version


"""
edge_version = EdgeCrawler()
try:
    edge_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    edge_version.close()
"""
