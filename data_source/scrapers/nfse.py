from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from data_source.core.downloader import Downloader
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

ADN_ROOT = "https://www.gov.br/nfse/pt-br/"
SECTIONS = (
    "documentacao-tecnica",
    "biblioteca",
)

DOWNLOADABLE_SUFFIXES = (".xml", ".xsd", ".pdf", ".zip", ".yaml", ".json")


class NFSeScraper(BaseScraper):
    """NFSe / ADN — public technical library, downloads XSDs, manuals and OpenAPI specs."""

    context = "nfse"

    def discover(self) -> Iterable[ScrapeItem]:
        driver = self.browser.driver
        for section in SECTIONS:
            url = urljoin(ADN_ROOT, section)
            driver.get(url)
            html = driver.page_source
            for link in _extract_downloadable_links(html, base=url):
                yield ScrapeItem(url=link, kind="file", metadata={"section": section})

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
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        full = urljoin(base, href)
        parsed = urlparse(full)
        if parsed.path.lower().endswith(DOWNLOADABLE_SUFFIXES):
            hrefs.append(full)
    seen: set[str] = set()
    unique: list[str] = []
    for h in hrefs:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique


def _guess_content_type(url: str) -> str:
    low = url.lower()
    if low.endswith((".xml", ".xsd")):
        return "application/xml"
    if low.endswith(".pdf"):
        return "application/pdf"
    if low.endswith(".zip"):
        return "application/zip"
    if low.endswith((".yaml", ".yml")):
        return "application/yaml"
    if low.endswith(".json"):
        return "application/json"
    return "application/octet-stream"
