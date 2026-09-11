from __future__ import annotations

import json
import re
from collections.abc import Iterable
from datetime import UTC, datetime

from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

CONFAZ_CV142_URL = "https://www.confaz.fazenda.gov.br/legislacao/convenios/2018/CV142_18"

_CEST_RE = re.compile(r"^\d{2}\.\d{3}\.\d{2}$")

_NCM_RE = re.compile(r"^\d{4}[\d./ ,-]{2,}$")


class ConfazCestScraper(BaseScraper):

    context = "confaz/cest"
    uses_browser = True

    def discover(self) -> Iterable[ScrapeItem]:
        yield ScrapeItem(
            url=CONFAZ_CV142_URL,
            kind="download",
            metadata={
                "title": "Convênio ICMS 142/2018 — Tabela CEST",
                "description": (
                    "Tabela consolidada do CEST extraída dos anexos do "
                    "Convênio ICMS 142/2018 do CONFAZ."
                ),
                "source": CONFAZ_CV142_URL,
                "published_at": "",
            },
        )

    def subpath_for(self, item: ScrapeItem) -> str:  # noqa: ARG002
        today = datetime.now(tz=UTC).date().isoformat()
        return f"{today}_convenio-icms-142-2018"

    def _load(self, url: str) -> str:
        """The page source, retried like the downloader would retry it.

        The browser is used here instead of httpx, and the retry that
        came free with the downloader does not. Without this the scrape
        gets one attempt where it used to get max_retries.
        """

        @retry(
            reraise=True,
            stop=stop_after_attempt(self._settings.max_retries),
            wait=wait_exponential(
                multiplier=1, min=1, max=self._settings.retry_max_wait_s
            ),
            retry=retry_if_exception_type((WebDriverException,)),
        )
        def _do() -> str:
            self._log.info("confaz.page.start", url=url)
            self.browser.driver.get(url)
            return str(self.browser.driver.page_source)

        return _do()

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        soup = BeautifulSoup(self._load(item.url), "lxml")

        rows = list(self._extract_rows(soup))
        self._log.info("confaz.cest.parsed", rows=len(rows))

        payload = {
            "source": item.url,
            "generated_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
            "rows": rows,
        }
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

        yield Artifact(
            filename="tabela-cest.json",
            data=data,
            content_type="application/json",
            subpath=self.subpath_for(item),
            metadata=item.metadata,
        )

    def _extract_rows(self, soup: BeautifulSoup) -> Iterable[dict[str, str]]:
        anexo: str | None = None
        seen: set[str] = set()

        for element in soup.find_all(["h3", "h4", "p", "tr"]):
            text = element.get_text(" ", strip=True)
            if not text:
                continue

            if text.upper().startswith("ANEXO "):
                anexo = _clean_anexo(text)
                continue

            if element.name != "tr":
                continue

            cells = [c.get_text(" ", strip=True) for c in element.find_all(["td", "th"])]
            if len(cells) < 3:
                continue

            cest = _find_cest(cells)
            if not cest or cest in seen:
                continue
            seen.add(cest)

            ncm = _find_ncm(cells, cest)
            description = _find_description(cells, cest, ncm)

            if not description:
                continue

            yield {
                "anexo": anexo or "",
                "cest": cest,
                "ncm": ncm,
                "description": description,
            }


def _clean_anexo(text: str) -> str:
    return " ".join(text.split())[:200]


def _find_cest(cells: list[str]) -> str:
    for cell in cells:
        candidate = cell.strip()
        if _CEST_RE.match(candidate):
            return candidate
    return ""


def _find_ncm(cells: list[str], cest: str) -> str:
    for cell in cells:
        text = cell.strip()
        if not text or text == cest:
            continue
        if _NCM_RE.match(text.replace(" ", "")):
            return text
    return ""


def _find_description(cells: list[str], cest: str, ncm: str) -> str:
    candidates = [c for c in cells if c and c.strip() not in {cest, ncm}]
    if not candidates:
        return ""
    return max(candidates, key=len).strip()
