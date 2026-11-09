import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from data_source.config import Settings
from data_source.scrapers.nfse import ADN_ROOT, PAGES, NFSeScraper

_DOCS = "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica"

PRODUCTION = f"""
<html><body><table>
  <tr><td><strong>Esquemas XSD</strong></td>
      <td><a href="{ADN_ROOT}/nfse-esquemas_xsd-v1-01-20260209.zip">NFSe-ESQUEMAS_XSD-v1.01-20260209</a></td></tr>
  <tr><td><a href="{_DOCS}/rtc/anexovi-leiautesrn_rtc_ibscbs-v1-04-01-nt009.xlsx">AnexoVI NT009</a></td></tr>
</table></body></html>
"""

RESTRICTED = f"""
<html><body>
  <a href="{_DOCS}/producao-restrita/esquemas_prod_restrita_20261020.zip">Esquemas XSD</a>
  <a href="{_DOCS}/producao-restrita/documentacao-tecnica-rtc-producao-restrita">a page, not a file</a>
</body></html>
"""

RTC = f"""
<html><body>
  <a href="{_DOCS}/rtc/nota-tecnica-009-se-cgnfs-e-v-1-01.pdf">Nota Técnica SE/CGNFS-e nº 009</a>
  <a href="{_DOCS}/rtc/anexovi-leiautesrn_rtc_ibscbs-v1-04-01-nt009.xlsx">AnexoVI NT009</a>
</body></html>
"""


class TestNFSeScraperReadsEveryPageWhereNotesLand(unittest.TestCase):
    """NT 009 was published on produção restrita and RTC and never seen.

    Only `documentacao-atual` was read, so stackin learnt of the new DPS
    layout from an E1235 rejection instead of from the feed.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scraper = NFSeScraper(
            settings=Settings(output_dir=Path(self._tmp.name), headless=True),
            browser=MagicMock(),
            downloader=MagicMock(),
        )
        pages = {
            ADN_ROOT: PRODUCTION,
            f"{_DOCS}/producao-restrita": RESTRICTED,
            f"{_DOCS}/rtc": RTC,
        }
        with patch.object(
            NFSeScraper, "download", side_effect=lambda url: pages[url].encode()
        ):
            self.items = list(self.scraper.discover())
        self.by_url = {item.url: item for item in self.items}

    def tearDown(self):
        self._tmp.cleanup()

    def test_it_reads_production_restricted_and_rtc(self):
        self.assertEqual([page for page, _ in PAGES], [ADN_ROOT, f"{_DOCS}/producao-restrita", f"{_DOCS}/rtc"])

    def test_the_restricted_schemas_are_found(self):
        item = self.by_url[f"{_DOCS}/producao-restrita/esquemas_prod_restrita_20261020.zip"]

        self.assertEqual(self.scraper.subpath_for(item), "2026-10-20_prodrest-esquemas-xsd")

    def test_the_technical_note_is_found(self):
        item = self.by_url[f"{_DOCS}/rtc/nota-tecnica-009-se-cgnfs-e-v-1-01.pdf"]

        self.assertTrue(self.scraper.subpath_for(item).startswith("undated_rtc-"))

    def test_production_keeps_the_folder_it_always_had(self):
        item = self.by_url[f"{ADN_ROOT}/nfse-esquemas_xsd-v1-01-20260209.zip"]

        self.assertEqual(
            self.scraper.subpath_for(item),
            "2026-02-09_nfse-esquemasxsd-v1.01-20260209",  # the folder already in data/nfse/
        )

    def test_a_file_linked_twice_is_kept_once_under_the_first_page(self):
        url = f"{_DOCS}/rtc/anexovi-leiautesrn_rtc_ibscbs-v1-04-01-nt009.xlsx"

        self.assertEqual(sum(1 for it in self.items if it.url == url), 1)
        self.assertEqual(self.by_url[url].metadata["page"], ADN_ROOT)

    def test_a_link_to_a_page_is_not_a_download(self):
        self.assertNotIn(
            f"{_DOCS}/producao-restrita/documentacao-tecnica-rtc-producao-restrita",
            self.by_url,
        )
