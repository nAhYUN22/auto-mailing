import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

from config import SITES
from error import CustomError, CustomErrorType
from scrapers.base import BaseCrawler


class BandizipCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["BANDIZIP"]
        super().__init__(url)

    def _update_date(self):
        now = datetime.now()
        formatted_date = now.strftime("%Y/%m/%d")
        print(formatted_date)

    def _get_latest_update(self):
        try:
            div_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.row"))
            )
            current_div_element = div_elements[0]

            version = current_div_element.find_element(By.CLASS_NAME, "cell1").text.lstrip("v")
            print(version)
            date = current_div_element.find_element(By.CLASS_NAME, "cell2").text.strip()
            date_obj = datetime.strptime(date, "%b %d, %Y").date()
            next_day = date_obj + timedelta(days=1)  # 하루 더하기
            formatted_date = next_day.strftime("%Y/%m/%d")  # 날짜 객체 → 문자열
            print(formatted_date)
            return formatted_date, version

        except Exception as e:
            raise CustomError(
                CustomError.raise_error(CustomErrorType.UNKNOWN_ERROR),
                f"반디집 신버전 패치 크롤링 실패: {e}",
            ) from e


"""
bandi_version = BandizipCrawler()
try:
    bandi_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    bandi_version.close()
"""
