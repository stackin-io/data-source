from __future__ import annotations

import hashlib
import io
import json
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import pdfplumber

from data_source.core.downloader import DownloadedFile
from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem
from data_source.exceptions import DiscoveryError, ExtractionError

ANEXO_XI_URL = "https://www8.receita.fazenda.gov.br/SimplesNacional/Arquivos/manual/Anexo_XI.pdf"
ACT = "Resolução CGSN nº 140, de 22 de maio de 2018, Anexo XI"

FOLDER_SUFFIX = "anexo-xi-cgsn-140"
PDF_FILENAME = "Anexo_XI.pdf"
TABLE_FILENAME = "anexo-xi.json"

MIN_ROWS = 450

_CNAE = re.compile(r"^(\d{4})-(\d)/(\d{2})$")
_TABLE = re.compile(r"^TABELA\s+([A-Z])$")
_FLAGS = {"S": True, "N": False}


class RfbMeiOcupacoesScraper(BaseScraper):
    """The occupations allowed to a MEI, Anexo XI of Resolução CGSN 140/2018.

    Keeps the PDF the Receita publishes and one JSON row per occupation with
    its CNAE subclass and whether it pays ISS and ICMS. A new folder is
    written only when the PDF bytes change.
    """

    context = "rfb/mei-ocupacoes"
    uses_browser = False
    min_items = 1

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._pdf: DownloadedFile | None = None
        self._rows: list[dict[str, Any]] = []

    def discover(self) -> Iterable[ScrapeItem]:
        pdf = self._downloader.fetch(ANEXO_XI_URL)
        rows = parse_anexo_xi(pdf.data)
        self._log.info("rfb.mei_ocupacoes.parsed", rows=len(rows))
        if len(rows) < MIN_ROWS:
            raise DiscoveryError(
                f"parsed {len(rows)} occupations from {ANEXO_XI_URL}, expected at least {MIN_ROWS}"
            )
        self._pdf, self._rows = pdf, rows
        digest = hashlib.sha256(pdf.data).hexdigest()
        published = _http_date(pdf.last_modified) or datetime.now(tz=UTC).date().isoformat()
        subpath = _subpath(Path(self._settings.output_dir) / self.context, published, digest)
        yield ScrapeItem(
            url=ANEXO_XI_URL,
            kind="download",
            metadata={
                "title": "Receita — Anexo XI da Resolução CGSN 140/2018 (ocupações do MEI)",
                "description": (
                    "Ocupações permitidas ao MEI, Tabelas A e B, com a subclasse CNAE e se "
                    "a ocupação recolhe ISS e ICMS."
                ),
                "published_at": subpath.split("_", 1)[0],
                "source": ANEXO_XI_URL,
                "last_modified": pdf.last_modified,
                "sha256": digest,
                "subpath": subpath,
            },
        )

    def subpath_for(self, item: ScrapeItem) -> str:
        return item.metadata["subpath"]

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        if self._pdf is None:
            raise ExtractionError("extract ran before discover fetched the PDF")
        payload = {
            "source": item.url,
            "act": ACT,
            "last_modified": item.metadata["last_modified"],
            "sha256": item.metadata["sha256"],
            "generated_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
            "rows": self._rows,
        }
        subpath = self.subpath_for(item)
        yield Artifact(
            filename=PDF_FILENAME,
            data=self._pdf.data,
            content_type="application/pdf",
            subpath=subpath,
            metadata=item.metadata,
        )
        yield Artifact(
            filename=TABLE_FILENAME,
            data=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
            content_type="application/json",
            subpath=subpath,
            metadata=item.metadata,
        )


def parse_anexo_xi(raw: bytes) -> list[dict[str, Any]]:
    """One row per occupation of Tabelas A and B.

    A row the page break cut in two comes back as a trailing row with only
    the occupation (or description) text; it is folded into the row above.
    Any other row that does not read as `occupation | 0000-0/00 | description
    | S/N | S/N` is an error, so a layout change never drops rows silently.
    """
    rows: list[dict[str, Any]] = []
    table = ""
    try:
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            cells_by_row = [
                [_cell(cell) for cell in row]
                for page in pdf.pages
                for found in page.extract_tables()
                for row in found
            ]
    except Exception as exc:
        raise ExtractionError(f"could not read the Anexo XI PDF: {exc}") from exc

    for cells in cells_by_row:
        if len(cells) != 5:
            raise ExtractionError(f"Anexo XI row with {len(cells)} cells: {cells}")
        occupation, cnae, description, iss, icms = cells
        heading = _TABLE.match(_flat(occupation))
        if heading and not any((cnae, description, iss, icms)):
            table = heading.group(1)
            continue
        if _flat(occupation) == "OCUPAÇÃO" and _flat(cnae) == "CNAE":
            continue
        match = _CNAE.match(cnae)
        if match and iss in _FLAGS and icms in _FLAGS and occupation and table:
            rows.append(
                {
                    "occupation": _flat(occupation),
                    "cnae": "".join(match.groups()),
                    "cnae_description": _flat(description),
                    "iss": _FLAGS[iss],
                    "icms": _FLAGS[icms],
                    "table": table,
                }
            )
            continue
        if rows and not any((cnae, iss, icms)) and (occupation or description):
            previous = rows[-1]
            previous["occupation"] = _join(previous["occupation"], occupation)
            previous["cnae_description"] = _join(previous["cnae_description"], description)
            continue
        raise ExtractionError(f"Anexo XI row does not parse: {cells}")
    return rows


def _cell(value: str | None) -> str:
    return (value or "").strip()


def _flat(value: str) -> str:
    """Joins a cell's lines; a line ending in `/` or a hyphenated word runs on."""
    text = ""
    for line in value.splitlines():
        text = _join(text, line)
    return text


def _join(head: str, tail: str) -> str:
    tail = " ".join(tail.split())
    head = head.rstrip()
    if not tail:
        return head
    if not head:
        return tail
    if head.endswith("/") or (head.endswith("-") and not head.endswith(" -")):
        return head + tail
    return f"{head} {tail}"


def _http_date(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError):
        return ""


def _subpath(root: Path, published: str, digest: str) -> str:
    """The latest folder when its PDF has the same bytes, else a new one."""
    folders = sorted(p for p in root.glob(f"*_{FOLDER_SUFFIX}*") if p.is_dir())
    if folders:
        stored = folders[-1] / PDF_FILENAME
        if stored.is_file() and hashlib.sha256(stored.read_bytes()).hexdigest() == digest:
            return folders[-1].name
    name = f"{published}_{FOLDER_SUFFIX}"
    if (root / name).exists():
        name = f"{name}-{digest[:8]}"
    return name
