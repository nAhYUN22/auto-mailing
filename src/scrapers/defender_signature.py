import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

from config import SITES
from scrapers.base import BaseCrawler


class SignatureCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["SIGNATURE"]
        super().__init__(url)

    def _get_latest_update(self):
        date = self.driver.find_element(By.XPATH, '//*[@id="releaseDate_0"]').text
        print(date)

        dt = datetime.strptime(date, "%m/%d/%Y %I:%M:%S %p")
        next_day = dt + timedelta(days=1)  # 하루 더하기
        formatted_date = next_day.strftime("%Y/%m/%d")  # 날짜 객체 → 문자열
        print(formatted_date)

        version = self.crawl_last_version()

        return formatted_date, version

    def crawl_last_version(self):
        version = (
            WebDriverWait(self.driver, 10)
            .until(EC.visibility_of_element_located(((By.XPATH, '//*[@id="comboVersion"]'))))
            .get_attribute("value")
            .strip()
        )
        print(version)
        return version


"""
signature_version = SignatureCrawler()
try:
    signature_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    signature_version.close()
"""
