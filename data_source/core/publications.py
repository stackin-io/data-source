"""Picks the NF-e and NFS-e publications a scrape run has just persisted."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from data_source.core.index import read_manifest

NEW_STATUSES = frozenset({"ok", "partial"})

NFE_KINDS = {
    "nfe/esquemas-xml": "Esquema XSD",
    "nfe/notas-tecnicas": "Nota técnica",
    "nfe/informes-tecnicos": "Informe técnico",
    "nfe/manuais": "Manual",
}

NFSE_KINDS = (
    (re.compile(r"esquema|xsd"), "Esquema XSD"),
    (re.compile(r"nota tecnica"), "Nota técnica"),
    (re.compile(r"informe tecnico"), "Informe técnico"),
    (re.compile(r"anexo"), "Anexo"),
    (re.compile(r"manual|guia"), "Manual"),
)


def _plain(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[\s_\-]+", " ", folded.lower())


def kind_of(context: str, title: str) -> str | None:
    if context in NFE_KINDS:
        return NFE_KINDS[context]
    if context == "nfse":
        plain = _plain(title)
        for pattern, kind in NFSE_KINDS:
            if pattern.search(plain):
                return kind
    return None


def environment_of(slug: str, title: str) -> str | None:
    plain = _plain(f"{slug} {title}")
    if re.search(r"prodrest|prod restrita|producao restrita", plain):
        return "produção restrita"
    if re.search(r"\bproducao\b", plain):
        return "produção"
    return None


def new_publications(root: Path, context: str) -> list[dict]:
    """Items of `data/<context>` manifests persisted by the last run, oldest first."""
    folder = Path(root) / context
    manifests = sorted(folder.rglob("manifest.json")) if folder.is_dir() else []
    found: list[dict] = []
    for path in manifests:
        manifest = read_manifest(path)
        if manifest is None:
            continue
        item_context = manifest.get("context", path.parent.relative_to(root).as_posix())
        for item in manifest.get("items", []):
            if item.get("status") not in NEW_STATUSES:
                continue
            title = item.get("title", "")
            kind = kind_of(item_context, title)
            if kind is None:
                continue
            found.append(
                {
                    "context": item_context,
                    "kind": kind,
                    "title": title,
                    "published_at": item.get("published_at", ""),
                    "environment": environment_of(item.get("slug", ""), title),
                    "source_url": item.get("source_url", ""),
                    "folder_url": item.get("folder_url", ""),
                }
            )
    found.sort(key=lambda p: (p["published_at"], p["context"], p["title"]))
    return found
