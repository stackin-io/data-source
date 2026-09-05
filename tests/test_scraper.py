import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path
from unittest.mock import MagicMock

from data_source.config import Settings
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem
from data_source.core.storage import LocalStorage
from data_source.exceptions import DiscoveryError, ScraperError


class _FakeScraper(BaseScraper):
    context = "fake"

    def __init__(self, items, artifacts_by_url, **kwargs):
        super().__init__(**kwargs)
        self._items = items
        self._artifacts_by_url = artifacts_by_url

    def discover(self) -> Iterable[ScrapeItem]:
        yield from self._items

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        return self._artifacts_by_url[item.url]


class TestBaseScraperContract(unittest.TestCase):

    def test_requires_context_attribute(self):
        class NoContext(BaseScraper):
            def discover(self):
                return []

            def extract(self, item):  # noqa: ARG002
                return []

        with self.assertRaises(ScraperError):
            NoContext()


class TestBaseScraperRun(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.settings = Settings(output_dir=self.root, headless=True)
        self.storage = LocalStorage(self.root)
        self.browser = MagicMock()
        self.downloader = MagicMock()
        self.downloader.__enter__.return_value = self.downloader
        self.browser.__enter__.return_value = self.browser

    def tearDown(self):
        self._tmp.cleanup()

    def _make(self, items, artifacts_by_url):
        return _FakeScraper(
            items,
            artifacts_by_url,
            settings=self.settings,
            storage=self.storage,
            browser=self.browser,
            downloader=self.downloader,
        )

    def test_persists_every_artifact_discovered(self):
        items = [ScrapeItem(url="https://x/1", kind="file")]
        artifacts_by_url = {
            "https://x/1": [Artifact(filename="a.xml", data=b"<a/>")],
        }
        scraper = self._make(items, artifacts_by_url)

        result = scraper.run()

        self.assertEqual(result.discovered, 1)
        self.assertEqual(result.persisted, 1)
        self.assertEqual(result.failed, 0)
        self.assertTrue(Path(result.paths[0]).exists())

    def test_counts_extract_errors_as_failed_and_continues(self):
        items = [
            ScrapeItem(url="https://x/1", kind="file"),
            ScrapeItem(url="https://x/2", kind="file"),
        ]

        class Boom(_FakeScraper):
            def extract(self, item):
                if item.url == "https://x/1":
                    raise RuntimeError("kaboom")
                return [Artifact(filename="b.xml", data=b"<b/>")]

        scraper = Boom(
            items,
            {},
            settings=self.settings,
            storage=self.storage,
            browser=self.browser,
            downloader=self.downloader,
        )

        result = scraper.run()

        self.assertEqual(result.discovered, 2)
        self.assertEqual(result.persisted, 1)
        self.assertEqual(result.failed, 1)

    def test_raises_discovery_error_when_discover_fails(self):
        class BadDiscover(_FakeScraper):
            def discover(self):
                raise RuntimeError("network down")

        scraper = BadDiscover(
            [],
            {},
            settings=self.settings,
            storage=self.storage,
            browser=self.browser,
            downloader=self.downloader,
        )

        with self.assertRaises(DiscoveryError):
            scraper.run()


if __name__ == "__main__":
    unittest.main()
