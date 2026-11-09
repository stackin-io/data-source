from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from data_source.core.downloader import slugify
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

_DOCS = "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica"
ADN_ROOT = f"{_DOCS}/documentacao-atual"

# (page, subpath prefix). Production first: a file linked from more than
# one page keeps the production identity it always had. Notes and schemas
# reach produção restrita and the RTC page before production — NT 009 sat
# there for weeks unseen while only `documentacao-atual` was read — so the
# prefix keeps a homologation-only change recognisable as one.
PAGES: tuple[tuple[str, str], ...] = (
    (ADN_ROOT, ""),
    (f"{_DOCS}/producao-restrita", "prodrest-"),
    (f"{_DOCS}/rtc", "rtc-"),
)

DOWNLOADABLE_SUFFIXES = (".xml", ".xsd", ".pdf", ".zip", ".xlsx", ".doc", ".docx")

_DATE_YYYYMMDD_RE = re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)")
_DATE_MONTH_RE = re.compile(
    r"-(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)(20\d{2})(?!\d)",
    flags=re.IGNORECASE,
)
_MONTHS = {
    "jan": "01",
    "fev": "02",
    "mar": "03",
    "abr": "04",
    "mai": "05",
    "jun": "06",
    "jul": "07",
    "ago": "08",
    "set": "09",
    "out": "10",
    "nov": "11",
    "dez": "12",
}


class NFSeScraper(BaseScraper):
    """ADN nacional (gov.br/nfse) — collects the current guides, manuals, XSDs
    and appendix files and stores each under `data/nfse/<YYYY-MM-DD>_<slug>/`.

    The listing is server-rendered, so no browser is needed: Chrome's renderer
    timed out on the page's third-party scripts long before the anchors mattered.
    """

    context = "nfse"
    uses_browser = False

    def discover(self) -> Iterable[ScrapeItem]:
        seen: set[str] = set()
        items: list[ScrapeItem] = []
        for root, prefix in PAGES:
            page = self.download(root).decode("utf-8", errors="replace")
            items.extend(_items_on(page, root, prefix, seen))
        items.sort(key=lambda it: it.metadata.get("published_at", ""), reverse=True)
        yield from items

    def subpath_for(self, item: ScrapeItem) -> str:
        return _subpath(item)

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        title = item.metadata.get("title", "")
        subpath = _subpath(item)
        downloaded = self._downloader.fetch(item.url, title_hint=title)
        yield Artifact(
            filename=downloaded.filename,
            data=downloaded.data,
            content_type=downloaded.content_type,
            subpath=subpath,
            metadata=item.metadata,
        )


def _items_on(page: str, root: str, prefix: str, seen: set[str]) -> list[ScrapeItem]:
    """The downloadable links of one listing page not already seen on another."""
    soup = BeautifulSoup(page, "lxml")
    items: list[ScrapeItem] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        parsed = urlparse(href)
        if not parsed.path.lower().endswith(DOWNLOADABLE_SUFFIXES):
            continue
        full = urljoin(root, href)
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
                    "page": root,
                    "prefix": prefix,
                },
            )
        )
    return items


def _subpath(item: ScrapeItem) -> str:
    """`<date>_<prefix><slug>`; production keeps the bare slug it always had."""
    title = item.metadata.get("title", "")
    slug = item.metadata.get("prefix", "") + (slugify(title) if title else "unknown")
    date_iso = item.metadata.get("published_at") or ""
    return f"{date_iso}_{slug}" if date_iso else f"undated_{slug}"


def _nearest_section(anchor) -> str | None:
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
