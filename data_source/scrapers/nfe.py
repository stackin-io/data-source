from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from data_source.core.downloader import slugify
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

PORTAL_ROOT = "https://hom.nfe.fazenda.gov.br/portal/"
LIST_PAGES = (
    "listaConteudo.aspx?tipoConteudo=BMPFMBoln3w=",  # Downloads (Pacote de Liberação)
)

DOWNLOAD_PREFIXES = ("exibirArquivo.aspx", "download.aspx")

# Matches "27/07/2026", "17/05/11", "01/10/10", "(28/09/2011)", etc.
_DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{2,4})")


class NFeScraper(BaseScraper):
    """NFe homologation portal — collects every download link and stores each file
    under `data/nfe/<slug-of-link-text>/<real-filename>`."""

    context = "nfe"

    def discover(self) -> Iterable[ScrapeItem]:
        driver = self.browser.driver
        items: list[ScrapeItem] = []
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
                date_iso = _extract_iso_date(title)
                items.append(
                    ScrapeItem(
                        url=urljoin(url, href),
                        kind="download",
                        metadata={
                            "title": title,
                            "source": rel,
                            "published_at": date_iso or "",
                        },
                    )
                )
        # newest first — subpath prefix `YYYY-MM-DD_` keeps this order on disk too
        items.sort(key=lambda it: it.metadata.get("published_at", ""), reverse=True)
        yield from items

    def subpath_for(self, item: ScrapeItem) -> str:
        title = item.metadata.get("title", "")
        slug = slugify(title) if title else "unknown"
        date_iso = item.metadata.get("published_at") or ""
        return f"{date_iso}_{slug}" if date_iso else f"undated_{slug}"

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


def _extract_iso_date(text: str) -> str | None:
    """Return the first dd/mm/yy(yy) found in text as ISO YYYY-MM-DD, or None."""
    m = _DATE_RE.search(text)
    if not m:
        return None
    dd, mm, yy = m.group(1), m.group(2), m.group(3)
    year = int(yy)
    if len(yy) == 2:
        year += 2000 if year < 80 else 1900
    try:
        # sanity check
        _ = (int(dd), int(mm), year)
    except ValueError:
        return None
    return f"{year:04d}-{int(mm):02d}-{int(dd):02d}"
