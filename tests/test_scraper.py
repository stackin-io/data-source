import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path
from unittest.mock import MagicMock

from data_source.config import Settings
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem
from data_source.core.storage import LocalStorage
from data_source.exceptions import DiscoveryError, ScraperError, TooFewItemsError


class _FakeScraper(BaseScraper):
    context = "fake"

    def __init__(self, items, artifacts_by_url, **kwargs):
        super().__init__(**kwargs)
        self._items = items
        self._artifacts_by_url: dict[str, list[Artifact]] = artifacts_by_url

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

    def test_retries_discovery_until_it_succeeds(self):
        calls = []

        class Flaky(_FakeScraper):
            def discover(self):
                calls.append(1)
                if len(calls) < 2:
                    raise RuntimeError("renderer timeout")
                yield from self._items

        items = [ScrapeItem(url="https://x/1", kind="file")]
        scraper = Flaky(
            items,
            {"https://x/1": [Artifact(filename="a.xml", data=b"<a/>")]},
            settings=self.settings,
            storage=self.storage,
            browser=self.browser,
            downloader=self.downloader,
        )

        result = scraper.run()

        self.assertEqual(len(calls), 2)
        self.assertEqual(result.persisted, 1)

    def test_gives_up_after_max_retries(self):
        calls = []

        class AlwaysDown(_FakeScraper):
            def discover(self):
                calls.append(1)
                raise RuntimeError("network down")

        scraper = AlwaysDown(
            [],
            {},
            settings=self.settings,
            storage=self.storage,
            browser=self.browser,
            downloader=self.downloader,
        )

        with self.assertRaises(DiscoveryError):
            scraper.run()
        self.assertEqual(len(calls), self.settings.max_retries)


class TestItemStatus(TestBaseScraperRun):
    """SVRS serves some links as 200 with 0 bytes; they were recorded as `ok`."""

    def _status_of(self, artifacts):
        items = [ScrapeItem(url="https://x/1", kind="file")]
        scraper = self._make(items, {"https://x/1": artifacts})
        return scraper.run().items[0].status

    def test_written_file_is_ok(self):
        self.assertEqual(self._status_of([Artifact(filename="a.xml", data=b"<a/>")]), "ok")

    def test_zero_byte_download_is_empty(self):
        self.assertEqual(self._status_of([Artifact(filename="a.xml", data=b"")]), "empty")

    def test_no_artifact_is_no_file(self):
        self.assertEqual(self._status_of([]), "no_file")


class TestMinimumItems(TestBaseScraperRun):
    """A source that lists nothing must fail the run, not pass it.

    scrape-nfe discovered 0 items in all five contexts on 2026-11-19, stayed
    green and committed empty manifests (issue #11).
    """

    def _items(self, n):
        return [ScrapeItem(url=f"https://x/{i}", kind="file") for i in range(n)]

    def _artifacts(self, n):
        return {f"https://x/{i}": [Artifact(filename=f"{i}.xml", data=b"<a/>")] for i in range(n)}

    def test_zero_items_fails_by_default(self):
        scraper = self._make([], {})

        with self.assertRaises(TooFewItemsError) as ctx:
            scraper.run()

        self.assertEqual(ctx.exception.found, 0)
        self.assertEqual(ctx.exception.minimum, 1)
        self.assertIn("expected at least 1", str(ctx.exception))

    def test_fewer_than_the_class_floor_fails(self):
        scraper = self._make(self._items(2), self._artifacts(2))
        scraper.min_items = 3

        with self.assertRaises(TooFewItemsError):
            scraper.run()

    def test_at_the_floor_succeeds(self):
        scraper = self._make(self._items(3), self._artifacts(3))
        scraper.min_items = 3

        result = scraper.run()

        self.assertEqual(result.discovered, 3)

    def test_run_argument_overrides_the_class_floor(self):
        scraper = self._make([], {})
        scraper.min_items = 50

        result = scraper.run(min_items=0)

        self.assertEqual(result.discovered, 0)

    def test_previous_manifest_survives_a_short_discovery(self):
        good = self._make(self._items(2), self._artifacts(2))
        good.run()
        manifest = self.root / "fake" / "manifest.json"
        before = manifest.read_text()

        with self.assertRaises(TooFewItemsError):
            self._make([], {}).run()

        self.assertEqual(manifest.read_text(), before)

    def test_short_discovery_is_retried(self):
        calls = []

        class HalfRendered(_FakeScraper):
            def discover(self):
                calls.append(1)
                if len(calls) < 2:
                    return
                yield from self._items

        scraper = HalfRendered(
            self._items(1),
            self._artifacts(1),
            settings=self.settings,
            storage=self.storage,
            browser=self.browser,
            downloader=self.downloader,
        )

        result = scraper.run()

        self.assertEqual(len(calls), 2)
        self.assertEqual(result.discovered, 1)


class TestEveryRegisteredScraperHasAFloor(unittest.TestCase):
    def test_floor_is_at_least_one(self):
        from data_source.scrapers import REGISTRY

        for name, cls in REGISTRY.items():
            with self.subTest(scraper=name):
                self.assertGreaterEqual(cls.min_items, 1)


if __name__ == "__main__":
    unittest.main()
