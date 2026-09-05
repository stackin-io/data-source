from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from data_source.core.downloader import Downloader
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

PORTAL_ROOT = "https://hom.nfe.fazenda.gov.br/portal/"
DOWNLOAD_PATHS = (
    "listaConteudo.aspx?tipoConteudo=BMPFMBoln3w=",  # Pacote de Liberação (XSDs)
)

DOWNLOADABLE_SUFFIXES = (".xml", ".xsd", ".pdf", ".zip", ".doc", ".docx")


class NFeScraper(BaseScraper):
    """NFe portal — grabs XSD packages, MOC and technical notes into `data/nfe/<date>/`."""

    context = "nfe"

    def discover(self) -> Iterable[ScrapeItem]:
        driver = self.browser.driver
        for rel in DOWNLOAD_PATHS:
            url = urljoin(PORTAL_ROOT, rel)
            driver.get(url)
            html = driver.page_source
            for link in _extract_downloadable_links(html, base=url):
                yield ScrapeItem(url=link, kind="file", metadata={"section": rel})

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        data = self.download(item.url)
        yield Artifact(
            filename=Downloader.suggest_filename(item.url),
            data=data,
            content_type=_guess_content_type(item.url),
            metadata=item.metadata,
        )


def _extract_downloadable_links(html: str, *, base: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    hrefs: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        full = urljoin(base, href)
        parsed = urlparse(full)
        if parsed.path.lower().endswith(DOWNLOADABLE_SUFFIXES):
            hrefs.append(full)
    # dedupe preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for h in hrefs:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique


def _guess_content_type(url: str) -> str:
    low = url.lower()
    if low.endswith(".xml") or low.endswith(".xsd"):
        return "application/xml"
    if low.endswith(".pdf"):
        return "application/pdf"
    if low.endswith(".zip"):
        return "application/zip"
    return "application/octet-stream"
