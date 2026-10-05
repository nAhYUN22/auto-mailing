from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import SELENIUM_GRID_URL


class BaseCrawler:
    def __init__(self, url: Optional[str] = None, driver=None):
        self.url = url
        self.selenium_grid_url = SELENIUM_GRID_URL
        self._driver: Optional[webdriver.Remote] = driver

    @property
    def driver(self) -> webdriver.Remote:
        if self._driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--lang=en-US")
            self._driver = webdriver.Remote(
                command_executor=self.selenium_grid_url, options=chrome_options
            )
            if self.url:
                self.load_page()

        return self._driver

    def load_page(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutError:
            print("페이지 로딩 시간 초과(10sec 초과)")

    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException as e:
            raise e

    def close(self):
        if self._driver:
            try:
                self._driver.quit()
            except Exception as e:
                print("세선 이미 종료: ", e)
            finally:
                self._driver = None
