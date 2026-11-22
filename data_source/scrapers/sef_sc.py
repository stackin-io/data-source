from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from datetime import UTC, datetime
from urllib.parse import urlencode

from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem
from data_source.exceptions import DiscoveryError, ExtractionError

SPED_TABLES_ROOT = "https://www.sped.fazenda.gov.br/spedtabelas"
VERSIONS_URL = (
    f"{SPED_TABLES_ROOT}/WsConsulta/WsConsulta.asmx/consultarVersoesTabelasExternas"
    "?codigoSistema=SpedFiscal"
)
DOWNLOAD_URL = f"{SPED_TABLES_ROOT}/wsconsulta/obterTabela.ashx"
SEF_SC_PAGE = "https://www.sef.sc.gov.br/saiba-mais/sped-fiscal"

PACKAGE = "SPEDFISCAL_SC"
TABLE_TYPE = "INF_ADIC_APUR"
RAW_FILENAME = "tabela-5.2.txt"
TABLE_FILENAME = "tabela-5.2.json"
ENCODING = "latin-1"

MIN_ROWS = 300

_WS_NS = "{http://www.sped.fazenda.gov.br/sped/tabelas/ConsultaVersoes}"
_META_NS = "{http://www.sped.fazenda.gov.br/sped/tabelas/metadados}"


class SefScCBenefScraper(BaseScraper):
    """Santa Catarina's cBenef table (EFD Tabela 5.2), the one SEFAZ/SC checks
    cBenef, cBenefRBC and cCredPresumido against.

    SEF/SC publishes it as a PDF on its SPED Fiscal page and, machine-readable,
    through the SPED external tables service. A new folder is written only when
    the service lists a new version.
    """

    context = "sef/sc/cbenef"
    uses_browser = False
    min_items = 1

    def discover(self) -> Iterable[ScrapeItem]:
        table = _find_table(self.download(VERSIONS_URL))
        query = urlencode({"idTabela": table["id"], "versao": table["versao"]})
        yield ScrapeItem(
            url=f"{DOWNLOAD_URL}?{query}",
            kind="download",
            metadata={
                "title": f"SEF/SC — Tabela 5.2 (cBenef) v{table['versao']}",
                "description": (
                    f"{table['desc']}, Santa Catarina. Códigos de benefício fiscal "
                    "(cBenef, cBenefRBC, cCredPresumido) com vigência. "
                    f"Publicada pela SEF/SC em {SEF_SC_PAGE}."
                ),
                "published_at": table["dtVersao"],
                "source": SEF_SC_PAGE,
                "table_id": table["id"],
                "version": table["versao"],
                "sha1": table["hash"].lower(),
            },
        )

    def subpath_for(self, item: ScrapeItem) -> str:
        meta = item.metadata
        return f"{meta['published_at']}_tabela-5.2-cbenef-v{meta['version']}"

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        raw = self.download(item.url)
        expected = item.metadata.get("sha1", "")
        actual = hashlib.sha1(raw, usedforsecurity=False).hexdigest()
        if expected and actual != expected:
            raise ExtractionError(
                f"{item.url} hashes to {actual}, the version list says {expected}"
            )

        rows = parse_table(raw)
        self._log.info("sef_sc.cbenef.parsed", rows=len(rows))
        if len(rows) < MIN_ROWS:
            raise ExtractionError(
                f"parsed {len(rows)} cBenef rows from {item.url}, expected at least {MIN_ROWS}"
            )

        payload = {
            "source": item.url,
            "published_by": SEF_SC_PAGE,
            "uf": "SC",
            "table": {
                "id": item.metadata["table_id"],
                "type": TABLE_TYPE,
                "version": int(item.metadata["version"]),
                "published_at": item.metadata["published_at"],
                "sha1": actual,
            },
            "generated_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
            "rows": rows,
        }
        subpath = self.subpath_for(item)
        yield Artifact(
            filename=RAW_FILENAME,
            data=raw,
            content_type="text/plain",
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


def _find_table(response: bytes) -> dict[str, str]:
    root = ET.fromstring(response)
    embedded = root.findtext(f"{_WS_NS}metadadosXml")
    if not embedded:
        raise DiscoveryError("SPED version list carries no metadadosXml")
    metadata = ET.fromstring(embedded.lstrip("\ufeff").encode("utf-8"))
    for package in metadata.iter(f"{_META_NS}pacote"):
        if package.get("cod") != PACKAGE:
            continue
        for table in package.iter(f"{_META_NS}tabela"):
            if table.get("tipo") == TABLE_TYPE:
                return {
                    key: table.get(key, "") for key in ("id", "versao", "desc", "dtVersao", "hash")
                }
    raise DiscoveryError(f"no {TABLE_TYPE} table in package {PACKAGE}")


def parse_table(raw: bytes) -> list[dict[str, str | None]]:
    """Rows of the pipe-delimited table: `code|description|DDMMYYYY|DDMMYYYY`.

    The first line is the header (`versão=N INF_ADIC, DESC_INF, DT_INI, DT_FIM`).
    A code listed twice carries two vigências; both rows are kept. The
    description reads `<benefit> - <legal basis>` for most codes; the
    benefit is split out so a consumer can pick the crédito presumido ones.
    """
    rows: list[dict[str, str | None]] = []
    for line in raw.decode(ENCODING).splitlines()[1:]:
        cells = line.split("|")
        if len(cells) != 4:
            continue
        code, description, start, end = (cell.strip() for cell in cells)
        if not code or not description:
            continue
        benefit, _, legal_basis = description.partition(" - ")
        rows.append(
            {
                "code": code,
                "description": description,
                "benefit": benefit.strip() if legal_basis else None,
                "legal_basis": legal_basis.strip() or None,
                "valid_from": _iso(start),
                "valid_to": _iso(end),
            }
        )
    return rows


def _iso(value: str) -> str | None:
    """`01012023` → `2023-01-01`; anything else is kept as published."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d%m%Y").date().isoformat()
    except ValueError:
        return value
