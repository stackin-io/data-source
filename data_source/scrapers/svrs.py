from __future__ import annotations

import html
import re
from collections.abc import Iterable
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from data_source.core.downloader import slugify
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem

PORTAL_ROOT = "https://dfe-portal.svrs.rs.gov.br"

_DOWNLOAD_RE = re.compile(
    r"download_arquivo_estatico\(\s*'(?P<sistema>[^']+)'\s*,\s*"
    r"(?P<tipo>\d+)\s*,\s*'(?P<nome>[^']+)'\s*\)"
)
_DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")


class _SVRSPortalScraper(BaseScraper):
    """Shared logic for the SVRS DF-e portal — subclasses set `context` and `doc_slug`.

    Every document family is served by the same ASP.NET listing at
    `/{doc_slug}/{section}`, fully server-rendered, so no browser is needed.
    """

    uses_browser = False

    doc_slug: str = ""
    section: str = "Documentos"

    def list_url(self) -> str:
        return f"{PORTAL_ROOT}/{self.doc_slug}/{self.section}"

    def discover(self) -> Iterable[ScrapeItem]:
        page = self.download(self.list_url()).decode("utf-8", errors="replace")
        soup = BeautifulSoup(page, "lxml")
        items: list[ScrapeItem] = []
        for article in soup.select("article.conteudo-lista__item"):
            anchor = article.find("a", onclick=True)
            if anchor is None:
                continue
            match = _DOWNLOAD_RE.search(str(anchor["onclick"]))
            if match is None:
                continue
            title = " ".join(anchor.get_text(" ", strip=True).split())
            if not title:
                continue
            filename = html.unescape(match.group("nome"))
            items.append(
                ScrapeItem(
                    url=_download_url(
                        match.group("sistema"), match.group("tipo"), filename
                    ),
                    kind="download",
                    metadata={
                        "title": title,
                        "description": _description(article) or title,
                        "source": self.list_url(),
                        "filename": filename,
                        "published_at": _published_at(article) or "",
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
            filename=_safe_filename(
                item.metadata.get("filename") or downloaded.filename
            ),
            data=downloaded.data,
            content_type=downloaded.content_type,
            subpath=self.subpath_for(item),
            metadata=item.metadata,
        )


class SVRSNFeDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NF-e publicados pela SEFAZ Virtual RS (22 UFs)."""

    context = "svrs/nfe/documentos"
    doc_slug = "Nfe"


class SVRSNFCeDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NFC-e publicados pela SEFAZ Virtual RS."""

    context = "svrs/nfce/documentos"
    doc_slug = "Nfce"


class SVRSCTeDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais do CT-e publicados pela SEFAZ Virtual RS."""

    context = "svrs/cte/documentos"
    doc_slug = "Cte"


class SVRSMDFeDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais do MDF-e publicados pela SEFAZ Virtual RS."""

    context = "svrs/mdfe/documentos"
    doc_slug = "Mdfe"


class SVRSBPeDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais do BP-e publicados pela SEFAZ Virtual RS."""

    context = "svrs/bpe/documentos"
    doc_slug = "Bpe"


class SVRSNF3eDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NF3e (energia elétrica)."""

    context = "svrs/nf3e/documentos"
    doc_slug = "Nf3e"


class SVRSNFComDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NFCom (comunicação)."""

    context = "svrs/nfcom/documentos"
    doc_slug = "Nfcom"


class SVRSNFAgDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NFAg (agropecuária)."""

    context = "svrs/nfag/documentos"
    doc_slug = "Nfag"


class SVRSNFGasDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NFGas (gás canalizado)."""

    context = "svrs/nfgas/documentos"
    doc_slug = "Nfgas"


class SVRSDCeDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da DC-e (declaração de conteúdo)."""

    context = "svrs/dce/documentos"
    doc_slug = "Dce"


class SVRSNFABIDocumentosScraper(_SVRSPortalScraper):
    """Documentos oficiais da NFABI (abastecimento)."""

    context = "svrs/nfabi/documentos"
    doc_slug = "Nfabi"


class SVRSDIFALDocumentosScraper(_SVRSPortalScraper):
    """Documentos do DIFAL — tributário, não é documento fiscal."""

    context = "svrs/difal/documentos"
    doc_slug = "Difal"


class SVRSNFFDocumentosScraper(_SVRSPortalScraper):
    """Documentos da NFF — meta-documento de infraestrutura."""

    context = "svrs/nff/documentos"
    doc_slug = "Nff"


class SVRSPESDocumentosScraper(_SVRSPortalScraper):
    """Documentos do PES — meta-documento de infraestrutura."""

    context = "svrs/pes/documentos"
    doc_slug = "Pes"


class SVRSONEDocumentosScraper(_SVRSPortalScraper):
    """Documentos do ONE — meta-documento de infraestrutura."""

    context = "svrs/one/documentos"
    doc_slug = "One"


def _download_url(sistema: str, tipo: str, filename: str) -> str:
    query = urlencode(
        {"sistema": sistema, "tipoArquivo": tipo, "nomeArquivo": filename}
    )
    return f"{PORTAL_ROOT}/{sistema}/DownloadArquivoEstatico/?{query}"


def _description(article) -> str:  # type: ignore[no-untyped-def]
    paragraph = article.find("p")
    if paragraph is None:
        return ""
    return " ".join(paragraph.get_text(" ", strip=True).split())[:500]


def _published_at(article) -> str | None:  # type: ignore[no-untyped-def]
    time_tag = article.find("time")
    if time_tag is None:
        return None
    raw = str(time_tag.get("datetime") or time_tag.get_text(" ", strip=True))
    match = _DATE_RE.search(raw)
    if match is None:
        return None
    dd, mm, yyyy = match.group(1), match.group(2), match.group(3)
    return f"{yyyy}-{mm}-{dd}"


def _safe_filename(filename: str) -> str:
    """Portal filenames carry spaces and underscores; both become dashes so the
    raw.githubusercontent URL for the stored file needs no escaping."""
    stem, dot, ext = filename.rpartition(".")
    if not dot:
        return slugify(_dashed(filename))
    return f"{slugify(_dashed(stem))}.{slugify(ext)}"


def _dashed(text: str) -> str:
    return re.sub(r"[_\s]+", "-", text)
