import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from data_source.config import Settings
from data_source.core.index import rebuild

NS = "{http://www.w3.org/2005/Atom}"
RAW = "https://raw.example/data"
TREE = "https://tree.example/data"


def manifest(context: str, slug: str, published: str) -> dict:
    return {
        "context": context,
        "generated_at": "2026-09-06T00:00:00+00:00",
        "totals": {"discovered": 1, "persisted": 1, "skipped": 0, "failed": 0},
        "items": [
            {
                "slug": slug,
                "title": slug,
                "description": slug,
                "published_at": published,
                "folder_url": f"{TREE}/{context}/{slug}",
                "files": [],
                "downloaded_at": "2026-09-06T00:00:00+00:00",
            }
        ],
    }


class TestRebuildAggregatesEveryContext(unittest.TestCase):
    """A parallel run leaves each context written by a different job."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for context, slug, published in (
            ("svrs/nfe/documentos", "a-nfe", "2026-08-25"),
            ("svrs/cte/documentos", "b-cte", "2026-01-10"),
            ("nfse", "c-nfse", "2026-05-05"),
        ):
            folder = self.root / context
            folder.mkdir(parents=True)
            (folder / "manifest.json").write_text(
                json.dumps(manifest(context, slug, published)), encoding="utf-8"
            )
        self.settings = Settings(
            output_dir=self.root, public_base_url=RAW, browse_base_url=TREE
        )
        self.contexts = rebuild(self.settings)

    def tearDown(self):
        self._tmp.cleanup()

    def _root_manifest(self) -> dict:
        with (self.root / "manifest.json").open(encoding="utf-8") as fh:
            return json.load(fh)

    def test_returns_every_context_found_on_disk(self):
        self.assertEqual(
            sorted(self.contexts),
            ["nfse", "svrs/cte/documentos", "svrs/nfe/documentos"],
        )

    def test_root_sitemap_lists_all_three(self):
        listed = [c["context"] for c in self._root_manifest()["contexts"]]
        self.assertEqual(len(listed), 3)
        self.assertIn("svrs/cte/documentos", listed)

    def test_root_feed_carries_an_entry_per_context_newest_first(self):
        root = ET.parse(self.root / "feed.xml").getroot()
        titles = [e.find(f"{NS}title").text for e in root.findall(f"{NS}entry")]
        self.assertEqual(len(titles), 3)
        self.assertTrue(titles[0].startswith("[SVRS/NFE/DOCUMENTOS]"))
        self.assertTrue(titles[-1].startswith("[SVRS/CTE/DOCUMENTOS]"))

    def test_each_context_gets_its_own_feed(self):
        for context in self.contexts:
            with self.subTest(context=context):
                feed = ET.parse(self.root / context / "feed.xml").getroot()
                self.assertEqual(len(feed.findall(f"{NS}entry")), 1)

    def test_a_context_feed_can_be_skipped(self):
        (self.root / "nfse" / "feed.xml").unlink()
        rebuild(self.settings, feeds=False)
        self.assertFalse((self.root / "nfse" / "feed.xml").exists())

    def test_an_unreadable_manifest_is_skipped_not_fatal(self):
        broken = self.root / "broken"
        broken.mkdir()
        (broken / "manifest.json").write_text("{not json", encoding="utf-8")
        self.assertEqual(len(rebuild(self.settings)), 3)
