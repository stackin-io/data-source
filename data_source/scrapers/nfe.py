from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from data_source.core.downloader import slugify
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

PORTAL_ROOT = "https://hom.nfe.fazenda.gov.br/portal/"
DOWNLOAD_PREFIXES = ("exibirArquivo.aspx", "download.aspx")
_DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{2,4})")


class _NFePortalScraper(BaseScraper):
    """Shared logic for NFe portal categories — subclasses set `context` and `list_page`."""

    list_page: str = ""

    def discover(self) -> Iterable[ScrapeItem]:
        driver = self.browser.driver
        url = urljoin(PORTAL_ROOT, self.list_page)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        items: list[ScrapeItem] = []
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"]).strip()
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
                        "description": _clean_description(title),
                        "source": self.list_page,
                        "published_at": date_iso or "",
                    },
                )
            )
        items.sort(key=lambda it: it.metadata.get("published_at", ""), reverse=True)
        yield from items

    def subpath_for(self, item: ScrapeItem) -> str:
        title = item.metadata.get("title", "")
        slug = slugify(title) if title else "unknown"
        date_iso = item.metadata.get("published_at") or ""
        return f"{date_iso}_{slug}" if date_iso else f"undated_{slug}"

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        title = item.metadata.get("title", "")
        downloaded = self._downloader.fetch(item.url, title_hint=title)
        yield Artifact(
            filename=downloaded.filename,
            data=downloaded.data,
            content_type=downloaded.content_type,
            subpath=self.subpath_for(item),
            metadata=item.metadata,
        )


class NFeEsquemasXMLScraper(_NFePortalScraper):
    """Pacotes de Liberação, XSDs e Esquemas XML da NF-e."""

    context = "nfe/esquemas-xml"
    list_page = "listaConteudo.aspx?tipoConteudo=BMPFMBoln3w="


class NFeNotasTecnicasScraper(_NFePortalScraper):
    """Notas Técnicas oficiais da NF-e (documentos vigentes e anteriores)."""

    context = "nfe/notas-tecnicas"
    list_page = "listaConteudo.aspx?tipoConteudo=04BIflQt1aY="


class NFeInformesTecnicosScraper(_NFePortalScraper):
    """Informes Técnicos oficiais da NF-e (documentos vigentes)."""

    context = "nfe/informes-tecnicos"
    list_page = "listaConteudo.aspx?tipoConteudo=hXzemuyNHW4="


# Backwards-compat alias — existing callers importing `NFeScraper` keep working.
NFeScraper = NFeEsquemasXMLScraper


def _link_title(anchor) -> str:  # type: ignore[no-untyped-def]
    span = anchor.find("span", class_="tituloConteudo")
    text = (span.get_text(" ", strip=True) if span else anchor.get_text(" ", strip=True)) or ""
    return " ".join(text.split())


def _clean_description(title: str) -> str:
    """Trim trailing date/format tags from the raw title for a friendlier description."""
    cleaned = re.sub(
        r"\.?\s*Publicad[oa] em\s*\d{2}/\d{2}/\d{2,4}.*$", "", title, flags=re.IGNORECASE
    )
    cleaned = re.sub(r"\(\s*\d{2}/\d{2}/\d{2,4}\s*\).*$", "", cleaned)
    cleaned = re.sub(r"\s*\(ZIP\)\s*$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" -.")


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
        _ = (int(dd), int(mm), year)
    except ValueError:
        return None
    return f"{year:04d}-{int(mm):02d}-{int(dd):02d}"
