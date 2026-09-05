from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from data_source.core.downloader import slugify
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

PORTAL_ROOT = "https://hom.nfe.fazenda.gov.br/portal/"
LIST_PAGES = (
    "listaConteudo.aspx?tipoConteudo=BMPFMBoln3w=",  # Downloads (Pacote de Liberação)
)

# The portal renders each download as `<a href="exibirArquivo.aspx?conteudo=...">`
# or `<a href="download.aspx?tipoConteudo=...">`. Title lives in an inner
# `<span class="tituloConteudo">…</span>` (falls back to link text).
DOWNLOAD_PREFIXES = ("exibirArquivo.aspx", "download.aspx")


class NFeScraper(BaseScraper):
    """NFe homologation portal — collects every download link and stores each file
    under `data/nfe/<slug-of-link-text>/<real-filename>`."""

    context = "nfe"

    def discover(self) -> Iterable[ScrapeItem]:
        driver = self.browser.driver
        for rel in LIST_PAGES:
            url = urljoin(PORTAL_ROOT, rel)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "lxml")
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"].strip()
                if not href.startswith(DOWNLOAD_PREFIXES):
                    continue
                title = _link_title(anchor)
                if not title:
                    continue
                yield ScrapeItem(
                    url=urljoin(url, href),
                    kind="download",
                    metadata={"title": title, "source": rel},
                )

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        title = item.metadata.get("title", "")
        slug = slugify(title) if title else "unknown"
        downloaded = self._downloader.fetch(item.url, title_hint=title)
        yield Artifact(
            filename=downloaded.filename,
            data=downloaded.data,
            content_type=downloaded.content_type,
            subpath=slug,
            metadata=item.metadata,
        )


def _link_title(anchor) -> str:  # type: ignore[no-untyped-def]
    span = anchor.find("span", class_="tituloConteudo")
    text = (span.get_text(" ", strip=True) if span else anchor.get_text(" ", strip=True)) or ""
    return " ".join(text.split())
