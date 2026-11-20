import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from data_source.config import Settings
from data_source.core.downloader import DownloadedFile
from data_source.core.scraper import ScrapeItem
from data_source.scrapers.nfe import (
    PORTAL_ROOT,
    NFeEsquemasXMLScraper,
    NFeManuaisScraper,
    NFeScraper,
    _clean_description,
    _extract_iso_date,
)

LIST_PAGE = """
<html><body>
  <a href="exibirArquivo.aspx?conteudo=old">
    <span class="tituloConteudo">Pacote de Liberação nº 8 (ZIP). Publicado em 01/03/2024</span>
  </a>
  <a href="download.aspx?id=new">  Schema   XML  NT 2025.002 (15/07/25)  </a>
  <a href="exibirArquivo.aspx?conteudo=nodate"><span class="tituloConteudo">Leia-me</span></a>
  <a href="exibirArquivo.aspx?conteudo=empty">   </a>
  <a href="listaConteudo.aspx?tipoConteudo=x">Outra categoria</a>
  <a href="https://elsewhere/file.zip">Fora do portal</a>
  <a name="anchor-without-href">Sem link</a>
</body></html>
"""


def _scraper(cls=NFeEsquemasXMLScraper, *, page=LIST_PAGE, downloader=None):
    browser = MagicMock()
    browser.driver.page_source = page
    tmp = tempfile.TemporaryDirectory()
    scraper = cls(
        settings=Settings(output_dir=Path(tmp.name), headless=True),
        browser=browser,
        downloader=downloader or MagicMock(),
    )
    return scraper, browser, tmp


class TestNFePortalDiscover(unittest.TestCase):
    def setUp(self):
        self.scraper, self.browser, self._tmp = _scraper()
        self.items = list(self.scraper.discover())
        self.by_url = {item.url: item for item in self.items}

    def tearDown(self):
        self._tmp.cleanup()

    def test_opens_the_category_list_page_on_the_portal(self):
        self.browser.driver.get.assert_called_once_with(
            PORTAL_ROOT + NFeEsquemasXMLScraper.list_page
        )

    def test_keeps_only_titled_download_links(self):
        self.assertEqual(
            sorted(self.by_url),
            sorted(
                [
                    PORTAL_ROOT + "exibirArquivo.aspx?conteudo=old",
                    PORTAL_ROOT + "download.aspx?id=new",
                    PORTAL_ROOT + "exibirArquivo.aspx?conteudo=nodate",
                ]
            ),
        )

    def test_newest_first_and_undated_last(self):
        self.assertEqual(
            [item.metadata["published_at"] for item in self.items],
            ["2025-07-15", "2024-03-01", ""],
        )

    def test_title_comes_from_the_span_and_is_whitespace_collapsed(self):
        new = self.by_url[PORTAL_ROOT + "download.aspx?id=new"]
        old = self.by_url[PORTAL_ROOT + "exibirArquivo.aspx?conteudo=old"]

        self.assertEqual(new.metadata["title"], "Schema XML NT 2025.002 (15/07/25)")
        self.assertTrue(old.metadata["title"].startswith("Pacote de Liberação nº 8"))

    def test_metadata_carries_description_and_source(self):
        old = self.by_url[PORTAL_ROOT + "exibirArquivo.aspx?conteudo=old"]

        self.assertEqual(old.metadata["description"], "Pacote de Liberação nº 8")
        self.assertEqual(old.metadata["source"], NFeEsquemasXMLScraper.list_page)
        self.assertEqual(old.kind, "download")

    def test_dated_items_go_to_date_prefixed_folders(self):
        new = self.by_url[PORTAL_ROOT + "download.aspx?id=new"]

        self.assertEqual(self.scraper.subpath_for(new), "2025-07-15_schema-xml-nt-2025.002-150725")

    def test_undated_items_go_to_undated_folders(self):
        item = self.by_url[PORTAL_ROOT + "exibirArquivo.aspx?conteudo=nodate"]

        self.assertEqual(self.scraper.subpath_for(item), "undated_leia-me")

    def test_an_item_without_title_is_unknown(self):
        self.assertEqual(
            self.scraper.subpath_for(ScrapeItem(url="u", kind="download")), "undated_unknown"
        )

    def test_an_empty_page_finds_nothing(self):
        scraper, _, tmp = _scraper(page="<html></html>")
        self.addCleanup(tmp.cleanup)

        self.assertEqual(list(scraper.discover()), [])


class TestNFePortalExtract(unittest.TestCase):
    ITEM = ScrapeItem(
        url=PORTAL_ROOT + "download.aspx?id=new",
        kind="download",
        metadata={"title": "NT 2025.002", "published_at": "2025-07-15"},
    )

    def _extract(self, downloaded):
        downloader = MagicMock()
        downloader.fetch.return_value = downloaded
        scraper, _, tmp = _scraper(downloader=downloader)
        self.addCleanup(tmp.cleanup)
        return list(scraper.extract(self.ITEM)), downloader

    def test_yields_the_downloaded_file(self):
        artifacts, downloader = self._extract(
            DownloadedFile(data=b"PK", filename="nt.zip", content_type="application/zip")
        )

        downloader.fetch.assert_called_once_with(self.ITEM.url, title_hint="NT 2025.002")
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].filename, "nt.zip")
        self.assertEqual(artifacts[0].data, b"PK")
        self.assertEqual(artifacts[0].subpath, "2025-07-15_nt-2025.002")
        self.assertEqual(artifacts[0].metadata, self.ITEM.metadata)

    def test_an_html_page_instead_of_a_file_is_skipped(self):
        """The portal answers an expired link with its HTML error page and a 200."""
        artifacts, _ = self._extract(
            DownloadedFile(data=b"<html>", filename="x.bin", content_type="text/html")
        )

        self.assertEqual(artifacts, [])


class TestNFeCategories(unittest.TestCase):
    def test_nfescraper_is_the_schemas_category(self):
        self.assertIs(NFeScraper, NFeEsquemasXMLScraper)

    def test_each_category_reads_its_own_page(self):
        scraper, browser, tmp = _scraper(NFeManuaisScraper)
        self.addCleanup(tmp.cleanup)
        list(scraper.discover())

        browser.driver.get.assert_called_once_with(PORTAL_ROOT + NFeManuaisScraper.list_page)
        self.assertEqual(scraper.context, "nfe/manuais")


class TestExtractIsoDate(unittest.TestCase):
    def test_four_digit_year(self):
        self.assertEqual(_extract_iso_date("Publicado em 01/03/2024"), "2024-03-01")

    def test_two_digit_year_in_this_century(self):
        self.assertEqual(_extract_iso_date("(15/07/25)"), "2025-07-15")

    def test_two_digit_year_from_eighty_on_is_last_century(self):
        self.assertEqual(_extract_iso_date("10/10/99"), "1999-10-10")

    def test_first_date_wins(self):
        self.assertEqual(_extract_iso_date("01/01/2020 e 02/02/2021"), "2020-01-01")

    def test_no_date(self):
        self.assertIsNone(_extract_iso_date("Leia-me"))


class TestCleanDescription(unittest.TestCase):
    def test_drops_published_on_suffix(self):
        self.assertEqual(
            _clean_description("Manual v7. Publicada em 10/10/2024 - novo"), "Manual v7"
        )

    def test_drops_parenthesised_date(self):
        self.assertEqual(_clean_description("NT 2025.002 (15/07/25) v1.10"), "NT 2025.002")

    def test_drops_zip_tag(self):
        self.assertEqual(_clean_description("Pacote nº 9 (ZIP)"), "Pacote nº 9")

    def test_leaves_a_plain_title(self):
        self.assertEqual(_clean_description("Leia-me"), "Leia-me")


if __name__ == "__main__":
    unittest.main()
