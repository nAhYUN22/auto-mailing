import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from my_logging import logger

from config import SITES
from error import CustomError, CustomErrorType
from scrapers.base import BaseCrawler


class WhaleCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["WHALE"]
        super().__init__(url)

    # whale의 change log를 크롤링해오는 메서드
    def _get_latest_update(self):
        iframe = self.driver.find_element(By.ID, "NAVER_COMMON_BOARD_IFRAME")
        self.driver.switch_to.frame(iframe)
        ul_element = self.wait_for_element(By.TAG_NAME, "ul")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        li_elements[0].click()
        if not self._is_stable_patch():
            raise CustomError(CustomErrorType.NOT_RELEASE, "Beta 버전 패치는 수집하지 않습니다.")

        patch_date = self._crawl_release_date()

        version = self._crawl_version()
        formatted_patch_date = patch_date.strftime("%Y/%m/%d")

        print(version, formatted_patch_date)

        return formatted_patch_date, version

    def _is_stable_patch(self) -> bool:
        try:
            component_content = self.wait_for_element(
                By.CSS_SELECTOR, "div.se-section.se-section-text.se-l-default"
            )
            state_span = component_content.find_element(
                By.XPATH,
                '//span[(contains(text(), "Stable") or contains(text(), "Beta"))]',
            )
            if "Stable" in state_span.text:
                return True
            else:
                return False

        except Exception as e:
            raise CustomError(CustomErrorType.EMPTY_VALUE, f"Stable 여부 크롤링 실패: {e}") from e

    def _crawl_release_date(self):
        try:
            component_content = self.wait_for_element(
                By.CSS_SELECTOR, "div.se-section.se-section-text.se-l-default"
            )
            content_text = component_content.text
            # 날짜 추출 및 포맷팅
            formatted_date = self._extract_date(content_text)
            if formatted_date:
                return datetime.strptime(formatted_date, "%Y.%m.%d").date()
            return None

        except Exception as e:
            logger.error(f"릴리스 날짜 크롤링 실패: {e}", exc_info=True)
            raise CustomError(CustomErrorType.UNKNOWN_ERROR, e) from e

    def _crawl_version(self) -> str:
        try:
            contents_table = self.wait_for_element(By.CSS_SELECTOR, "span.se-fs-.se-ff-")
            contents_table_text = contents_table.text
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", contents_table_text)
            if match:
                version = match.group(1)
            return version

        except Exception as e:
            raise CustomError(CustomErrorType.EMPTY_VALUE, f"버전 크롤링 실패: {e}") from e

    def _extract_date(self, date_str: str) -> str | None:
        """미국 날짜 형식 → %Y.%m.%d 형식 변환"""
        pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}"
        match = re.search(pattern, date_str)
        if match:
            date_str = match.group()
            try:
                dt = datetime.strptime(date_str, "%B %d, %Y")
                return dt.strftime("%Y.%m.%d")
            except ValueError:
                return None
        return None


"""
whale_version = WhaleCrawler()
try:
    whale_version._get_latest_update()
except Exception as e:
    time.sleep(50)
    print(f"error: {e}")
finally:

    whale_version.close()
"""
