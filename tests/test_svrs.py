import tempfile
import unittest
from pathlib import Path
from typing import ClassVar
from unittest.mock import MagicMock

from data_source.config import Settings
from data_source.core.scraper import ScrapeItem
from data_source.scrapers import REGISTRY
from data_source.scrapers.nfe import NFeDiversosScraper
from data_source.scrapers.svrs import SVRSNFeDocumentosScraper

LISTING = """
<html><body>
  <article class="conteudo-lista__item clearfix">
    <header>
      <time class="conteudo-lista__item__datahora" datetime=" 16/12/2020"> 16/12/2020 </time>
      <h2 class="conteudo-lista__item__titulo">
        <a href="#" onclick="download_arquivo_estatico('NFE', 1, 'moc7-anexo-i.pdf');">
          Manual de Orienta&#231;&#227;o do Contribuinte - vers&#227;o 7.00
        </a>
      </h2>
    </header>
    <p>Leiaute e regras de valida&#231;&#227;o da NF-e.</p>
  </article>
  <article class="conteudo-lista__item clearfix">
    <header>
      <time datetime=" 02/03/2026"> 02/03/2026 </time>
      <h2><a href="#" onclick="download_arquivo_estatico('DFE', 3, 'DFe NTCJ 2025.001 v1.00.pdf');">
        Nota T&#233;cnica Conjunta 2025.001</a></h2>
    </header>
    <p>Split payment.</p>
  </article>
  <article class="conteudo-lista__item clearfix">
    <header><h2><a href="/Nfe/Faq">FAQ</a></h2></header>
  </article>
</body></html>
"""


class TestSVRSDiscovery(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.settings = Settings(output_dir=Path(self._tmp.name))
        self.downloader = MagicMock()
        self.downloader.__enter__.return_value = self.downloader
        self.downloader.get.return_value = LISTING.encode("utf-8")
        self.scraper = SVRSNFeDocumentosScraper(
            settings=self.settings,
            browser=MagicMock(),
            downloader=self.downloader,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_context_and_list_url(self):
        self.assertEqual(self.scraper.context, "svrs/nfe/documentos")
        self.assertEqual(
            self.scraper.list_url(),
            "https://dfe-portal.svrs.rs.gov.br/Nfe/Documentos",
        )

    def test_never_starts_a_browser(self):
        self.assertFalse(self.scraper.uses_browser)

    def test_discovers_only_items_with_a_download_call(self):
        items = list(self.scraper.discover())
        self.assertEqual(len(items), 2)

    def test_orders_newest_first_and_parses_the_date(self):
        items = list(self.scraper.discover())
        self.assertEqual(items[0].metadata["published_at"], "2026-03-02")
        self.assertEqual(items[1].metadata["published_at"], "2020-12-16")

    def test_builds_the_static_download_url_with_encoded_filename(self):
        newest, oldest = list(self.scraper.discover())
        self.assertEqual(
            oldest.url,
            "https://dfe-portal.svrs.rs.gov.br/NFE/DownloadArquivoEstatico/"
            "?sistema=NFE&tipoArquivo=1&nomeArquivo=moc7-anexo-i.pdf",
        )
        self.assertIn("/DFE/DownloadArquivoEstatico/", newest.url)
        self.assertIn("nomeArquivo=DFe+NTCJ+2025.001+v1.00.pdf", newest.url)

    def test_unescapes_entities_in_title_and_description(self):
        oldest = list(self.scraper.discover())[1]
        self.assertEqual(
            oldest.metadata["title"],
            "Manual de Orientação do Contribuinte - versão 7.00",
        )
        self.assertEqual(
            oldest.metadata["description"],
            "Leiaute e regras de validação da NF-e.",
        )

    def test_subpath_is_date_plus_slug(self):
        oldest = list(self.scraper.discover())[1]
        self.assertEqual(
            self.scraper.subpath_for(oldest),
            "2020-12-16_manual-de-orientacao-do-contribuinte-versao-7.00",
        )

    def test_subpath_falls_back_to_undated(self):
        item = ScrapeItem(url="x", kind="download", metadata={"title": "Sem data"})
        self.assertEqual(self.scraper.subpath_for(item), "undated_sem-data")

    def test_extract_turns_spaces_and_underscores_into_dashes(self):
        item = ScrapeItem(
            url="x",
            kind="download",
            metadata={"title": "t", "filename": "NT_2026.006_v1.00_RTC.pdf"},
        )
        self.downloader.fetch.return_value = MagicMock(
            data=b"%PDF-", filename="download.bin", content_type="application/pdf"
        )
        artifact = next(iter(self.scraper.extract(item)))
        self.assertEqual(artifact.filename, "nt-2026.006-v1.00-rtc.pdf")

    def test_extract_names_the_file_from_the_portal_not_the_response(self):
        newest = next(iter(self.scraper.discover()))
        self.downloader.fetch.return_value = MagicMock(
            data=b"%PDF-", filename="download.bin", content_type="application/pdf"
        )
        artifact = next(iter(self.scraper.extract(newest)))
        self.assertEqual(artifact.filename, "dfe-ntcj-2025.001-v1.00.pdf")
        self.assertEqual(artifact.subpath, "2026-03-02_nota-tecnica-conjunta-2025.001")


class TestNFePortalRejectsHtml(unittest.TestCase):
    """The portal answers some sidebar links with a page, not a file."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.downloader = MagicMock()
        self.scraper = NFeDiversosScraper(
            settings=Settings(output_dir=Path(self._tmp.name)),
            browser=MagicMock(),
            downloader=self.downloader,
        )
        self.item = ScrapeItem(
            url="https://hom.nfe.fazenda.gov.br/portal/download.aspx?tipoConteudo=x",
            kind="download",
            metadata={"title": "Visualizador de DF-e"},
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_html_response_yields_no_artifact(self):
        self.downloader.fetch.return_value = MagicMock(
            data=b"<!DOCTYPE html>",
            filename="download.aspx",
            content_type="text/html",
        )
        self.assertEqual(list(self.scraper.extract(self.item)), [])

    def test_real_file_still_yields_an_artifact(self):
        self.downloader.fetch.return_value = MagicMock(
            data=b"%PDF-", filename="a.pdf", content_type="application/pdf"
        )
        self.assertEqual(len(list(self.scraper.extract(self.item))), 1)


class TestEverySVRSPortalIsRegistered(unittest.TestCase):

    EXPECTED: ClassVar[dict[str, str]] = {
        "svrs/nfe/documentos": "https://dfe-portal.svrs.rs.gov.br/Nfe/Documentos",
        "svrs/nfce/documentos": "https://dfe-portal.svrs.rs.gov.br/Nfce/Documentos",
        "svrs/cte/documentos": "https://dfe-portal.svrs.rs.gov.br/Cte/Documentos",
        "svrs/mdfe/documentos": "https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos",
        "svrs/bpe/documentos": "https://dfe-portal.svrs.rs.gov.br/Bpe/Documentos",
        "svrs/nf3e/documentos": "https://dfe-portal.svrs.rs.gov.br/Nf3e/Documentos",
        "svrs/nfcom/documentos": "https://dfe-portal.svrs.rs.gov.br/Nfcom/Documentos",
        "svrs/nfag/documentos": "https://dfe-portal.svrs.rs.gov.br/Nfag/Documentos",
        "svrs/nfgas/documentos": "https://dfe-portal.svrs.rs.gov.br/Nfgas/Documentos",
        "svrs/dce/documentos": "https://dfe-portal.svrs.rs.gov.br/Dce/Documentos",
        "svrs/nfabi/documentos": "https://dfe-portal.svrs.rs.gov.br/Nfabi/Documentos",
        "svrs/difal/documentos": "https://dfe-portal.svrs.rs.gov.br/Difal/Documentos",
        "svrs/nff/documentos": "https://dfe-portal.svrs.rs.gov.br/Nff/Documentos",
        "svrs/pes/documentos": "https://dfe-portal.svrs.rs.gov.br/Pes/Documentos",
        "svrs/one/documentos": "https://dfe-portal.svrs.rs.gov.br/One/Documentos",
    }

    def test_each_context_resolves_to_its_own_portal(self):
        for context, url in self.EXPECTED.items():
            with self.subTest(context=context):
                scraper = REGISTRY[context](
                    settings=Settings(output_dir=Path(tempfile.gettempdir())),
                    browser=MagicMock(),
                    downloader=MagicMock(),
                )
                self.assertEqual(scraper.list_url(), url)
                self.assertFalse(scraper.uses_browser)

    def test_the_registry_carries_every_svrs_portal(self):
        registered = {c for c in REGISTRY if c.startswith("svrs/")}
        self.assertEqual(registered, set(self.EXPECTED))

    def test_contexts_are_distinct(self):
        slugs = {REGISTRY[c].doc_slug for c in self.EXPECTED}
        self.assertEqual(len(slugs), len(self.EXPECTED))
