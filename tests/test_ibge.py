import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from data_source.config import Settings
from data_source.core.storage import LocalStorage
from data_source.exceptions import DiscoveryError
from data_source.scrapers import REGISTRY, ibge
from data_source.scrapers.ibge import (
    SUBCLASSES_URL,
    IbgeCnaeScraper,
    format_cnae,
    parse_subclasses,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "ibge_cnae_subclasses.json").read_bytes()


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.response = FIXTURE
        downloader = MagicMock()
        downloader.__enter__.return_value = downloader
        downloader.get.side_effect = self._serve
        self.scraper = IbgeCnaeScraper(
            settings=Settings(output_dir=self.root, max_retries=1),
            storage=LocalStorage(self.root),
            browser=MagicMock(),
            downloader=downloader,
        )

    def _serve(self, url):
        if url == SUBCLASSES_URL:
            return self.response
        raise AssertionError(url)

    def tearDown(self):
        self._tmp.cleanup()

    def _folders(self):
        return sorted(p.name for p in (self.root / "ibge/cnae").glob("*_cnae-2.3-subclasses"))


class TestParse(unittest.TestCase):
    def test_flattens_the_hierarchy(self):
        rows = parse_subclasses(FIXTURE)

        self.assertEqual([r["code"] for r in rows], sorted(r["code"] for r in rows))
        row = next(r for r in rows if r["code"] == "8599603")
        self.assertEqual(row["formatted"], "8599-6/03")
        self.assertEqual(row["description"], "TREINAMENTO EM INFORMÁTICA")
        self.assertEqual(row["class"]["code"], "85996")
        self.assertEqual(row["group"]["code"], "859")
        self.assertEqual(row["division"]["code"], "85")
        self.assertEqual(row["section"], {"code": "P", "description": "EDUCAÇÃO"})

    def test_skips_entries_without_a_seven_digit_code(self):
        raw = json.dumps([{"id": "123", "descricao": "x"}, {"descricao": "y"}]).encode()

        self.assertEqual(parse_subclasses(raw), [])

    def test_not_json_is_a_discovery_error(self):
        with self.assertRaises(DiscoveryError):
            parse_subclasses(b"<html>blocked</html>")

    def test_format(self):
        self.assertEqual(format_cnae("0111301"), "0111-3/01")


class TestDiscover(_Base):
    def test_registered(self):
        self.assertIs(REGISTRY["ibge/cnae"], IbgeCnaeScraper)

    def test_new_content_gets_a_dated_folder(self):
        [item] = list(self.scraper.discover())

        self.assertRegex(self.scraper.subpath_for(item), r"^\d{4}-\d{2}-\d{2}_cnae-2.3-subclasses$")
        self.assertEqual(len(item.metadata["sha256"]), 64)


class TestRun(_Base):
    def test_writes_the_subclasses(self):
        with patch.object(ibge, "MIN_ROWS", 1):
            result = self.scraper.run()

        self.assertEqual(result.persisted, 1)
        [folder] = self._folders()
        payload = json.loads(
            (self.root / "ibge/cnae" / folder / "cnae-subclasses.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["source"], SUBCLASSES_URL)
        self.assertEqual(len(payload["rows"]), 5)
        self.assertEqual(
            set(payload["rows"][0]),
            {"code", "formatted", "description", "class", "group", "division", "section"},
        )

    def test_unchanged_content_is_skipped(self):
        with patch.object(ibge, "MIN_ROWS", 1):
            self.scraper.run()
            result = self.scraper.run()

        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.persisted, 0)
        self.assertEqual(len(self._folders()), 1)

    def test_changed_content_writes_a_new_folder(self):
        old = self.root / "ibge/cnae/2026-01-01_cnae-2.3-subclasses"
        old.mkdir(parents=True)
        (old / "cnae-subclasses.json").write_text(json.dumps({"sha256": "old"}), encoding="utf-8")

        with patch.object(ibge, "MIN_ROWS", 1):
            result = self.scraper.run()

        self.assertEqual(result.persisted, 1)
        self.assertEqual(len(self._folders()), 2)

    def test_too_few_rows_writes_nothing(self):
        result = self.scraper.run()

        self.assertEqual(result.failed, 1)
        self.assertEqual(self._folders(), [])


if __name__ == "__main__":
    unittest.main()
