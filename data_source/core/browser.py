from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from data_source.core.logger import get_logger
from data_source.exceptions import BrowserError


class Browser:
    """Thin Selenium wrapper. Scrapers depend on this, never on webdriver directly."""

    def __init__(
        self,
        *,
        headless: bool = True,
        timeout_s: int = 30,
        user_agent: str | None = None,
    ) -> None:
        self._headless = headless
        self._timeout_s = timeout_s
        self._user_agent = user_agent
        self._driver: WebDriver | None = None
        self._log = get_logger(__name__)

    def _build_options(self) -> Options:
        opts = Options()
        if self._headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        if self._user_agent:
            opts.add_argument(f"--user-agent={self._user_agent}")
        return opts

    def start(self) -> WebDriver:
        if self._driver is not None:
            return self._driver
        try:
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=self._build_options())
            self._driver.set_page_load_timeout(self._timeout_s)
            self._driver.implicitly_wait(self._timeout_s / 3)
            self._log.info("browser.started", headless=self._headless)
            return self._driver
        except WebDriverException as exc:
            raise BrowserError(f"failed to start webdriver: {exc}") from exc

    def stop(self) -> None:
        if self._driver is None:
            return
        try:
            self._driver.quit()
            self._log.info("browser.stopped")
        except WebDriverException as exc:
            self._log.warning("browser.stop_failed", error=str(exc))
        finally:
            self._driver = None

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise BrowserError("browser not started; use `with Browser(...)` or call .start() first")
        return self._driver

    def __enter__(self) -> Browser:
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.stop()


@contextmanager
def browser_session(**kwargs: object) -> Iterator[Browser]:
    b = Browser(**kwargs)  # type: ignore[arg-type]
    try:
        b.start()
        yield b
    finally:
        b.stop()
