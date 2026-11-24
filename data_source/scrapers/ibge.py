from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from data_source.core.scraper import Artifact, BaseScraper, ScrapeItem
from data_source.exceptions import DiscoveryError, ExtractionError

SUBCLASSES_URL = "https://servicodados.ibge.gov.br/api/v2/cnae/subclasses"
CONCLA_PAGE = "https://cnae.ibge.gov.br/"

FOLDER_SUFFIX = "cnae-2.3-subclasses"
TABLE_FILENAME = "cnae-subclasses.json"

MIN_ROWS = 1300


class IbgeCnaeScraper(BaseScraper):
    """The CNAE 2.3 subclasses, from the IBGE data service API.

    One JSON with every subclass and its class, group, division and section.
    A new folder is written only when the content hash moves; an unchanged
    day points at the latest folder and is skipped.
    """

    context = "ibge/cnae"
    uses_browser = False
    min_items = 1

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._rows: list[dict[str, Any]] = []

    def discover(self) -> Iterable[ScrapeItem]:
        self._rows = parse_subclasses(self.download(SUBCLASSES_URL))
        digest = rows_sha256(self._rows)
        today = datetime.now(tz=UTC).date().isoformat()
        latest = _latest_folder(Path(self._settings.output_dir) / self.context)
        subpath = f"{today}_{FOLDER_SUFFIX}"
        if latest is not None and _stored_sha256(latest / TABLE_FILENAME) == digest:
            subpath = latest.name
        yield ScrapeItem(
            url=SUBCLASSES_URL,
            kind="download",
            metadata={
                "title": "IBGE — CNAE 2.3, subclasses",
                "description": (
                    "As subclasses da CNAE 2.3 com descrição, classe, grupo, divisão e "
                    f"seção, publicadas pelo IBGE ({CONCLA_PAGE})."
                ),
                "published_at": subpath.split("_", 1)[0],
                "source": SUBCLASSES_URL,
                "sha256": digest,
                "subpath": subpath,
            },
        )

    def subpath_for(self, item: ScrapeItem) -> str:
        return item.metadata["subpath"]

    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        rows = self._rows
        self._log.info("ibge.cnae.parsed", rows=len(rows))
        if len(rows) < MIN_ROWS:
            raise ExtractionError(
                f"parsed {len(rows)} CNAE subclasses from {item.url}, expected at least {MIN_ROWS}"
            )
        payload = {
            "source": item.url,
            "published_by": CONCLA_PAGE,
            "classification": "CNAE 2.3",
            "sha256": item.metadata["sha256"],
            "generated_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
            "rows": rows,
        }
        yield Artifact(
            filename=TABLE_FILENAME,
            data=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
            content_type="application/json",
            subpath=self.subpath_for(item),
            metadata=item.metadata,
        )


def parse_subclasses(raw: bytes) -> list[dict[str, Any]]:
    """One row per subclass, sorted by code, from the API's nested JSON."""
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise DiscoveryError(f"IBGE answered something that is not JSON: {exc}") from exc
    if not isinstance(data, list):
        raise DiscoveryError("IBGE answered JSON that is not a list of subclasses")
    rows: list[dict[str, Any]] = []
    for entry in data:
        code = str(entry.get("id", ""))
        if len(code) != 7 or not code.isdigit():
            continue
        klass = entry.get("classe") or {}
        group = klass.get("grupo") or {}
        division = group.get("divisao") or {}
        section = division.get("secao") or {}
        rows.append(
            {
                "code": code,
                "formatted": format_cnae(code),
                "description": _clean(entry.get("descricao")),
                "class": _node(klass),
                "group": _node(group),
                "division": _node(division),
                "section": _node(section),
            }
        )
    rows.sort(key=lambda row: row["code"])
    return rows


def format_cnae(code: str) -> str:
    """`8599603` → `8599-6/03`."""
    return f"{code[:4]}-{code[4]}/{code[5:]}"


def rows_sha256(rows: list[dict[str, Any]]) -> str:
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _node(node: dict[str, Any]) -> dict[str, str]:
    return {"code": str(node.get("id", "")), "description": _clean(node.get("descricao"))}


def _clean(value: object) -> str:
    return " ".join(str(value or "").split())


def _latest_folder(root: Path) -> Path | None:
    folders = sorted(p for p in root.glob(f"*_{FOLDER_SUFFIX}") if p.is_dir())
    return folders[-1] if folders else None


def _stored_sha256(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("sha256", ""))
    except (OSError, ValueError):
        return ""
