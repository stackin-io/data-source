import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from data_source.config import Settings
from data_source.core.storage import LocalStorage
from data_source.exceptions import ExtractionError
from data_source.scrapers import confaz
from data_source.scrapers.confaz import CONFAZ_CV142_URL, ConfazCestScraper

# Shape of the CONFAZ page: an "ANEXO" heading, then a table per annex whose
# rows carry ITEM, CEST, NCM/SH and DESCRIÇÃO.
PAGE = """
<html><body>
  <p>ANEXO II</p>
  <p>AUTOPEÇAS</p>
  <table>
    <tr><th>ITEM</th><th>CEST</th><th>NCM/SH</th><th>DESCRIÇÃO</th></tr>
    <tr><td>1.0</td><td>01.001.00</td><td>3815.12.10 3815.12.90</td>
        <td>Catalisadores em colmeia cerâmica ou metálica</td></tr>
    <tr><td>2.0</td><td>01.002.00</td><td>3917</td>
        <td>Tubos e seus acessórios, de plásticos</td></tr>
    <tr><td>2.0</td><td>01.002.00</td><td>3917</td><td>duplicate, ignored</td></tr>
  </table>
  <h3>ANEXO   XXI</h3>
  <table>
    <tr><td>46.1</td><td>21.046.01</td><td>8517.13.00</td>
        <td>Smartphones</td></tr>
    <tr><td>x</td><td>not a cest</td><td>1234</td><td>ignored row</td></tr>
    <tr><td>21.099.00</td><td></td></tr>
  </table>
</body></html>
"""


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        browser = MagicMock()
        browser.__enter__.return_value = browser
        downloader = MagicMock()
        downloader.__enter__.return_value = downloader
        self.browser = browser
        self.scraper = ConfazCestScraper(
            settings=Settings(output_dir=self.root, headless=True, max_retries=1),
            storage=LocalStorage(self.root),
            browser=browser,
            downloader=downloader,
        )
        self.browser.driver.page_source = PAGE

    def tearDown(self):
        self._tmp.cleanup()


class TestParse(_Base):
    def test_rows_carry_annex_cest_ncm_and_description(self):
        with patch.object(confaz, "MIN_ROWS", 1):
            [artifact] = list(self.scraper.extract(next(iter(self.scraper.discover()))))

        rows = json.loads(artifact.data)["rows"]

        self.assertEqual([r["cest"] for r in rows], ["01.001.00", "01.002.00", "21.046.01"])
        self.assertEqual(rows[0]["anexo"], "ANEXO II")
        self.assertEqual(rows[0]["ncm"], "3815.12.10 3815.12.90")
        self.assertEqual(rows[0]["description"], "Catalisadores em colmeia cerâmica ou metálica")
        self.assertEqual(rows[2]["anexo"], "ANEXO XXI")
        self.assertEqual(artifact.filename, "tabela-cest.json")
        self.assertTrue(artifact.subpath.endswith("_convenio-icms-142-2018"))

    def test_page_is_loaded_through_the_browser(self):
        with patch.object(confaz, "MIN_ROWS", 1):
            list(self.scraper.extract(next(iter(self.scraper.discover()))))

        self.browser.driver.get.assert_called_once_with(CONFAZ_CV142_URL)


class TestGuards(_Base):
    def test_too_few_rows_is_an_extraction_error(self):
        """A block page or new markup parses to almost nothing; never save it."""
        with self.assertRaises(ExtractionError):
            list(self.scraper.extract(next(iter(self.scraper.discover()))))

    def test_run_with_too_few_rows_fails_and_writes_no_table(self):
        result = self.scraper.run()

        self.assertEqual(result.failed, 1)
        self.assertEqual(result.persisted, 0)
        self.assertEqual(list(self.root.glob("confaz/cest/*/tabela-cest.json")), [])

    def test_unchanged_table_is_not_written_again(self):
        with patch.object(confaz, "MIN_ROWS", 1):
            rows = list(self.scraper._extract_rows(confaz.BeautifulSoup(PAGE, "lxml")))
            old = self.root / "confaz/cest/2026-09-09_convenio-icms-142-2018"
            old.mkdir(parents=True)
            (old / "tabela-cest.json").write_text(json.dumps({"rows": rows}))

            result = self.scraper.run()

        self.assertEqual(result.persisted, 0)
        self.assertEqual(result.items[0].status, "unchanged")
        self.assertEqual(len(list(self.root.glob("confaz/cest/*/tabela-cest.json"))), 1)

    def test_changed_table_is_written_to_a_new_folder(self):
        with patch.object(confaz, "MIN_ROWS", 1):
            old = self.root / "confaz/cest/2026-09-09_convenio-icms-142-2018"
            old.mkdir(parents=True)
            (old / "tabela-cest.json").write_text(json.dumps({"rows": []}))

            result = self.scraper.run()

        self.assertEqual(result.persisted, 1)
        self.assertEqual(result.items[0].status, "ok")
        self.assertEqual(len(list(self.root.glob("confaz/cest/*/tabela-cest.json"))), 2)


if __name__ == "__main__":
    unittest.main()
