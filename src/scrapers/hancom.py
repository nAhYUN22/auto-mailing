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
from scrapers.base import BaseCrawler

HNC_PATCH_LIST = [
    "HNC2024",
    "HNC2022",
    "HNC2020",
    "HNC2018",
    "HNCNEO",
]


class HancomCrawler(BaseCrawler):
    def __init__(self) -> None:
        url = SITES["HNC"]
        super().__init__(url)

    def _format_korean_date(self, date_str):
        m = re.search(r"(\d+)년\s*(\d+)월\s*(\d+)일", date_str)
        if m:
            return f"{int(m.group(1))}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        else:
            return None

    def _extract_common_version(self, summary: str) -> str | None:
        # 버전 패턴: 숫자.숫자.숫자.숫자 (예: 13.0.0.2151)
        m = re.search(r"\d+\.\d+\.\d+\.\d+", summary)
        if m:
            return m.group()
        return None

    def _get_update_date(self):
        try:
            modal_texts = self.driver.find_element(
                By.CSS_SELECTOR, "div.MuiDialogContent-root.css-jcka0z"
            ).text
            modal_texts = "".join(modal_texts)

            return self._format_korean_date(modal_texts)
        except Exception as e:
            logger.error(f"날짜 추출 실패: {str(e)}")
            return None

    def _crawl_detail_info(self) -> dict[str, str | list[str] | None]:
        try:
            # 모달이 열릴 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "MuiDialog-container"))
            )
            modal = self.driver.find_element(By.CLASS_NAME, "MuiDialog-container")
            patch_date = self._get_update_date()

            table = modal.find_element(By.TAG_NAME, "table")
            td_texts = [td.text for td in table.find_elements(By.XPATH, ".//td")]
            summary = " ".join(td_texts[3:])
            version = self._extract_common_version(summary)

            return {"patch_date": patch_date, "version": version}

        except Exception as e:
            logger.error(f"상세 정보 크롤링 실패: {str(e)}")
            return {"patch_date": None, "summary": None}

    def _close_modal(self):
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.MuiIconButton-root.css-1ds6e9m")
                )
            )
            close_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiDialog-container"))
            )
        except Exception as e:
            logger.warning(f"모달 닫기 실패: {str(e)}")

    def _get_latest_update(self):
        self.driver.maximize_window()  # 창을 최대화 해야만 왼쪽 ul이 생김
        muibox = self.wait_for_element(By.CSS_SELECTOR, "div.MuiBox-root.css-14mlc4i")
        ul_element = muibox.find_element(By.TAG_NAME, "ul")
        hnc_office_button = ul_element.find_element(By.XPATH, './/li[.//span[text()="한컴오피스"]]')
        hnc_office_button.click()

        hnc_office_patch_list = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.MuiBox-root.css-81t6mk.e1de0imv0")
            )
        )
        patches = hnc_office_patch_list[:5]  # 한컴오피스 2024부터 한컴오피스 NEO까지 5개만 수집
        target_patch_components = []
        hnc_model_dict = {}
        for i, patch in enumerate(patches):
            try:
                detail_button = patch.find_element(By.TAG_NAME, "a")
                detail_button.click()
                detail_info = self._crawl_detail_info()

                self._close_modal()

                target_patch_components.append(patch)

                hnc_model_dict.update(
                    {
                        HNC_PATCH_LIST[i]: [
                            detail_info.get("patch_date"),
                            detail_info.get("version"),
                        ]
                    }
                )

            except Exception as e:
                logger.error(f"패치 처리 실패: {str(e)}")
                continue
        print(hnc_model_dict)
        return hnc_model_dict


"""
hnc_version = HancomCrawler()
try:
    hnc_version._get_latest_update()
except Exception as e:
    time.sleep(100)
    print(f"error: {e}")
finally:

    hnc_version.close()
"""
