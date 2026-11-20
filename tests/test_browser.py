import unittest
from unittest.mock import MagicMock, patch

from selenium.common.exceptions import WebDriverException

from data_source.core.browser import Browser, browser_session
from data_source.exceptions import BrowserError


class _ChromeTest(unittest.TestCase):
    """Patches the driver download and Chrome itself: no browser starts in tests."""

    def setUp(self):
        self.manager = self._patch("data_source.core.browser.ChromeDriverManager")
        self.manager.return_value.install.return_value = "/fake/chromedriver"
        self.service = self._patch("data_source.core.browser.Service")
        self.chrome = self._patch("data_source.core.browser.webdriver.Chrome")
        self.driver = self.chrome.return_value

    def _patch(self, target):
        patcher = patch(target)
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked


class TestBuildOptions(unittest.TestCase):
    def test_headless_with_user_agent(self):
        args = Browser(headless=True, user_agent="UA/1.0")._build_options().arguments

        self.assertIn("--headless=new", args)
        self.assertIn("--user-agent=UA/1.0", args)
        for flag in ("--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"):
            self.assertIn(flag, args)

    def test_headed_without_user_agent(self):
        args = Browser(headless=False)._build_options().arguments

        self.assertNotIn("--headless=new", args)
        self.assertFalse(any(a.startswith("--user-agent=") for a in args))


class TestStart(_ChromeTest):
    def test_starts_chrome_with_the_installed_driver_and_timeouts(self):
        browser = Browser(timeout_s=30)

        driver = browser.start()

        self.assertIs(driver, self.driver)
        self.service.assert_called_once_with("/fake/chromedriver")
        self.assertIs(self.chrome.call_args.kwargs["service"], self.service.return_value)
        self.driver.set_page_load_timeout.assert_called_once_with(30)
        self.driver.implicitly_wait.assert_called_once_with(10)
        self.assertIs(browser.driver, self.driver)

    def test_starting_twice_reuses_the_driver(self):
        browser = Browser()

        self.assertIs(browser.start(), browser.start())
        self.chrome.assert_called_once()

    def test_webdriver_failure_becomes_browser_error(self):
        self.chrome.side_effect = WebDriverException("chrome not reachable")

        with self.assertRaises(BrowserError) as ctx:
            Browser().start()

        self.assertIn("chrome not reachable", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, WebDriverException)


class TestStop(_ChromeTest):
    def test_quits_and_forgets_the_driver(self):
        browser = Browser()
        browser.start()

        browser.stop()

        self.driver.quit.assert_called_once()
        with self.assertRaises(BrowserError):
            _ = browser.driver

    def test_a_failing_quit_is_swallowed_and_the_driver_forgotten(self):
        self.driver.quit.side_effect = WebDriverException("already gone")
        browser = Browser()
        browser.start()

        browser.stop()

        with self.assertRaises(BrowserError):
            _ = browser.driver

    def test_stop_before_start_does_nothing(self):
        Browser().stop()

        self.chrome.assert_not_called()


class TestDriverProperty(unittest.TestCase):
    def test_raises_before_start(self):
        with self.assertRaises(BrowserError):
            _ = Browser().driver


class TestContextManagers(_ChromeTest):
    def test_with_browser_starts_and_stops(self):
        with Browser() as browser:
            self.assertIs(browser.driver, self.driver)
            self.driver.quit.assert_not_called()

        self.driver.quit.assert_called_once()

    def test_browser_session_stops_even_on_error(self):
        with self.assertRaises(RuntimeError), browser_session(headless=True, timeout_s=9) as b:
            self.assertIsInstance(b, Browser)
            self.driver.set_page_load_timeout.assert_called_once_with(9)
            raise RuntimeError("scrape blew up")

        self.driver.quit.assert_called_once()


class TestStopLogging(unittest.TestCase):
    def test_stop_logs_quit_failure(self):
        browser = Browser()
        browser._driver = MagicMock()
        browser._driver.quit.side_effect = WebDriverException("boom")
        browser._log = MagicMock()

        browser.stop()

        browser._log.warning.assert_called_once()
        self.assertEqual(browser._log.warning.call_args.args[0], "browser.stop_failed")


if __name__ == "__main__":
    unittest.main()
