"""Rebuilds the published indexes — every context feed plus the two root files.

Kept apart from the scrapers because a parallel run needs to regenerate them
after the fact: each matrix job only ever sees its own context, and the root
sitemap is an aggregate of all of them.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from data_source.config import Settings
from data_source.core.feed import build_atom
from data_source.core.logger import get_logger

CONTEXT_FEED_LIMIT = 50
ROOT_FEED_LIMIT = 100

log = get_logger("index")


def context_manifests(root: Path) -> list[Path]:
    return [p for p in sorted(root.rglob("manifest.json")) if p.parent != root]


def read_manifest(path: Path) -> dict | None:
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        log.warning("index.manifest_unreadable", path=str(path))
        return None
    return data if isinstance(data, dict) else None


def entry_updated(item: dict, fallback: str) -> str:
    updated = item.get("published_at") or ""
    if updated and len(updated) == 10:
        updated = f"{updated}T00:00:00+00:00"
    return updated or item.get("downloaded_at") or fallback


def build_context_feed(settings: Settings, manifest: dict) -> str:
    base_url = settings.public_base_url.rstrip("/")
    browse_url = settings.browse_base_url.rstrip("/")
    context = manifest["context"]
    generated_at = manifest.get("generated_at", "")
    items = sorted(
        manifest.get("items", []),
        key=lambda i: (i.get("published_at", ""), i.get("downloaded_at", "")),
        reverse=True,
    )
    entries = [
        {
            "id": f"{browse_url}/{context}/{item.get('slug', '')}",
            "title": item.get("title", ""),
            "summary": item.get("description", ""),
            "link": item.get("folder_url")
            or f"{browse_url}/{context}/{item.get('slug', '')}",
            "updated": entry_updated(item, generated_at),
        }
        for item in items[:CONTEXT_FEED_LIMIT]
    ]
    return build_atom(
        feed_id=f"{base_url}/{context}/feed.xml",
        title=f"Stackin data-source — {context}",
        subtitle=(
            f"Automated updates from the {context.upper()} scraper — "
            "official docs, XSDs, technical notes."
        ),
        self_url=f"{base_url}/{context}/feed.xml",
        site_url=f"{browse_url}/{context}",
        updated=generated_at,
        entries=entries,
    )


def rebuild(settings: Settings, *, feeds: bool = True) -> list[str]:
    """Regenerate every context feed and the two root files. Returns the contexts."""
    root = Path(settings.output_dir)
    base_url = settings.public_base_url.rstrip("/")
    browse_url = settings.browse_base_url.rstrip("/")

    contexts: list[dict] = []
    aggregated: list[dict] = []
    newest = ""

    for path in context_manifests(root):
        manifest = read_manifest(path)
        if manifest is None:
            continue
        rel = path.parent.relative_to(root).as_posix()
        context = manifest.get("context", rel)
        generated_at = manifest.get("generated_at", "")
        newest = max(newest, generated_at)

        if feeds:
            (path.parent / "feed.xml").write_text(
                build_context_feed(settings, manifest), encoding="utf-8"
            )

        contexts.append(
            {
                "context": context,
                "manifest_url": f"{base_url}/{rel}/manifest.json",
                "feed_url": f"{base_url}/{rel}/feed.xml",
                "browse_url": f"{browse_url}/{rel}",
                "generated_at": generated_at,
                "totals": manifest.get("totals", {}),
            }
        )
        for item in manifest.get("items", []):
            aggregated.append(
                {
                    "id": f"{browse_url}/{context}/{item.get('slug', '')}",
                    "title": f"[{context.upper()}] {item.get('title', '')}",
                    "summary": item.get("description", ""),
                    "link": item.get("folder_url", ""),
                    "updated": entry_updated(item, generated_at),
                }
            )

    generated_at = newest or datetime.now(tz=UTC).isoformat(timespec="seconds")
    root.mkdir(parents=True, exist_ok=True)
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "public_base_url": base_url,
                "browse_base_url": browse_url,
                "feed_url": f"{base_url}/feed.xml",
                "contexts": contexts,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    aggregated.sort(key=lambda e: e.get("updated", ""), reverse=True)
    (root / "feed.xml").write_text(
        build_atom(
            feed_id=f"{base_url}/feed.xml",
            title="Stackin data-source — todas as fontes",
            subtitle="Todas as atualizações fiscais oficiais indexadas pelo Stackin.",
            self_url=f"{base_url}/feed.xml",
            site_url=browse_url,
            updated=generated_at,
            entries=aggregated[:ROOT_FEED_LIMIT],
        ),
        encoding="utf-8",
    )
    log.info("index.rebuilt", contexts=len(contexts), items=len(aggregated))
    return [c["context"] for c in contexts]
