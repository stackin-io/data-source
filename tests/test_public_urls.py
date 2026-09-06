import json
import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path
from unittest.mock import MagicMock

from data_source.config import Settings
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem
from data_source.core.storage import LocalStorage

RAW = "https://raw.example/data"
TREE = "https://tree.example/data"


class _OneFileScraper(BaseScraper):
    context = "nfse"
    uses_browser = False

    def discover(self) -> Iterable[ScrapeItem]:
        yield ScrapeItem(
            url="https://portal/doc.pdf",
            kind="download",
            metadata={"title": "Manual", "published_at": "2026-02-09"},
        )

    def subpath_for(self, item: ScrapeItem) -> str:  # noqa: ARG002
        return "2026-02-09_manual"

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:  # noqa: ARG002
        yield Artifact(filename="doc.pdf", data=b"%PDF-", subpath="2026-02-09_manual")


class TestFolderUrlsNeverUseRaw(unittest.TestCase):
    """raw.githubusercontent serves files only — a directory URL always 404s."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        downloader = MagicMock()
        downloader.__enter__.return_value = downloader
        self.result = _OneFileScraper(
            settings=Settings(
                output_dir=self.root, public_base_url=RAW, browse_base_url=TREE
            ),
            storage=LocalStorage(self.root),
            browser=MagicMock(),
            downloader=downloader,
        ).run()

    def tearDown(self):
        self._tmp.cleanup()

    def _manifest(self) -> dict:
        with (self.root / "nfse" / "manifest.json").open(encoding="utf-8") as fh:
            return json.load(fh)

    def _feed(self) -> str:
        return (self.root / "nfse" / "feed.xml").read_text(encoding="utf-8")

    def test_file_urls_use_raw(self):
        item = self._manifest()["items"][0]
        self.assertEqual(
            item["file_urls"], [f"{RAW}/nfse/2026-02-09_manual/doc.pdf"]
        )

    def test_folder_url_uses_the_browse_base(self):
        item = self._manifest()["items"][0]
        self.assertEqual(item["folder_url"], f"{TREE}/nfse/2026-02-09_manual")

    def test_manifest_carries_both_bases(self):
        manifest = self._manifest()
        self.assertEqual(manifest["public_base_url"], f"{RAW}/nfse")
        self.assertEqual(manifest["browse_url"], f"{TREE}/nfse")

    def test_feed_entry_links_to_the_folder_on_the_browse_base(self):
        self.assertIn(f'href="{TREE}/nfse/2026-02-09_manual"', self._feed())

    def test_feed_site_link_is_not_a_raw_folder(self):
        self.assertIn(f'href="{TREE}/nfse"', self._feed())
        self.assertNotIn(f'href="{RAW}/nfse/"', self._feed())

    def test_root_sitemap_lists_the_browse_url(self):
        with (self.root / "manifest.json").open(encoding="utf-8") as fh:
            root = json.load(fh)
        self.assertEqual(root["browse_base_url"], TREE)
        self.assertEqual(root["contexts"][0]["browse_url"], f"{TREE}/nfse")


class _EmptyFileScraper(_OneFileScraper):
    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:  # noqa: ARG002
        yield Artifact(filename="doc.pdf", data=b"", subpath="2026-02-09_manual")


class TestEmptyDownloadsAreNotPersisted(unittest.TestCase):
    """The SVRS portal answers 200 with zero bytes on its own dead links."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        downloader = MagicMock()
        downloader.__enter__.return_value = downloader
        self.result = _EmptyFileScraper(
            settings=Settings(
                output_dir=self.root, public_base_url=RAW, browse_base_url=TREE
            ),
            storage=LocalStorage(self.root),
            browser=MagicMock(),
            downloader=downloader,
        ).run()

    def tearDown(self):
        self._tmp.cleanup()

    def test_nothing_is_written(self):
        self.assertEqual(self.result.persisted, 0)
        self.assertFalse((self.root / "nfse" / "2026-02-09_manual").exists())

    def test_it_is_not_counted_as_a_failure(self):
        self.assertEqual(self.result.failed, 0)
