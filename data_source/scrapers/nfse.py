from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from data_source.core.downloader import slugify
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

ADN_ROOT = "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual"

DOWNLOADABLE_SUFFIXES = (".xml", ".xsd", ".pdf", ".zip", ".xlsx", ".doc", ".docx")

_DATE_YYYYMMDD_RE = re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)")
_DATE_MONTH_RE = re.compile(
    r"-(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)(20\d{2})(?!\d)",
    flags=re.IGNORECASE,
)
_MONTHS = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06",
    "jul": "07", "ago": "08", "set": "09", "out": "10", "nov": "11", "dez": "12",
}


class NFSeScraper(BaseScraper):
    """ADN nacional (gov.br/nfse) — collects the current guides, manuals, XSDs
    and appendix files and stores each under `data/nfse/<YYYY-MM-DD>_<slug>/`."""

    context = "nfse"

    def discover(self) -> Iterable[ScrapeItem]:
        driver = self.browser.driver
        driver.get(ADN_ROOT)
        soup = BeautifulSoup(driver.page_source, "lxml")

        seen: set[str] = set()
        items: list[ScrapeItem] = []
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"]).strip()
            parsed = urlparse(href)
            if not parsed.path.lower().endswith(DOWNLOADABLE_SUFFIXES):
                continue
            full = urljoin(ADN_ROOT, href)
            if full in seen:
                continue
            seen.add(full)
            title = " ".join(anchor.get_text(" ", strip=True).split())
            if not title:
                continue
            section = _nearest_section(anchor) or ""
            date_iso = _extract_iso_date(full) or ""
            items.append(
                ScrapeItem(
                    url=full,
                    kind="download",
                    metadata={
                        "title": title,
                        "description": title,
                        "section": section,
                        "published_at": date_iso,
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
        slug = slugify(title) if title else "unknown"
        date_iso = item.metadata.get("published_at") or ""
        subpath = f"{date_iso}_{slug}" if date_iso else f"undated_{slug}"
        downloaded = self._downloader.fetch(item.url, title_hint=title)
        yield Artifact(
            filename=downloaded.filename,
            data=downloaded.data,
            content_type=downloaded.content_type,
            subpath=subpath,
            metadata=item.metadata,
        )


def _nearest_section(anchor) -> str | None:  # type: ignore[no-untyped-def]
    """Walk up siblings to find the section label (`<strong>Guias</strong>` etc)."""
    row = anchor.find_parent("tr")
    if row is None:
        return None
    strong = row.find("strong")
    if strong is None:
        return None
    return " ".join(strong.get_text(" ", strip=True).split())


def _extract_iso_date(text: str) -> str | None:
    """Extract publication date embedded in NFSe filename URLs.
    Handles `-YYYYMMDD` and `-mmm2025` (Portuguese abbreviated month) suffixes."""
    m = _DATE_YYYYMMDD_RE.search(text)
    if m:
        yyyy, mm, dd = m.group(1), m.group(2), m.group(3)
        return f"{yyyy}-{mm}-{dd}"
    m = _DATE_MONTH_RE.search(text)
    if m:
        month_key = m.group(1).lower()[:3]
        month = _MONTHS.get(month_key)
        year = m.group(2)
        if month and len(year) == 4:
            return f"{year}-{month}-01"
    return None
