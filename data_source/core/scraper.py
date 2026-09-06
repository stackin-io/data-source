from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable
from contextlib import nullcontext
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from data_source.config import Settings, get_settings
from data_source.core.browser import Browser
from data_source.core.downloader import Downloader
from data_source.core.feed import build_atom
from data_source.core.logger import configure as configure_logging
from data_source.core.logger import get_logger
from data_source.core.storage import LocalStorage, Storage
from data_source.core.unpack import maybe_unpack_zip
from data_source.exceptions import DiscoveryError, ScraperError


@dataclass(frozen=True)
class ScrapeItem:
    """A discovered page/link the scraper wants to visit or download."""

    url: str
    kind: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Artifact:
    """A file the scraper decided to persist. Storage handles the actual write."""

    filename: str
    data: bytes
    content_type: str = "application/octet-stream"
    subpath: str = ""  # extra folder(s) under the context, e.g. "esquemas-xml-nfe-v4"
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class ItemRecord:
    """A row in the manifest.json — one per discovered item. Both local paths and
    public URLs are recorded so the manifest doubles as a sitemap."""

    slug: str
    title: str
    description: str
    published_at: str
    source_url: str
    folder: str
    folder_url: str = ""
    files: list[str] = field(default_factory=list)
    file_urls: list[str] = field(default_factory=list)
    downloaded_at: str = ""
    status: str = "pending"


@dataclass
class ScrapeResult:
    context: str
    discovered: int = 0
    persisted: int = 0
    skipped: int = 0
    failed: int = 0
    paths: list[str] = field(default_factory=list)
    items: list[ItemRecord] = field(default_factory=list)


class BaseScraper(ABC):
    """Template Method — subclasses override discover() and extract().

    Base owns: browser lifecycle, retry, storage, logging, error containment.
    Subclasses own: what pages exist for this source, how each page turns into files.

    Set `uses_browser = False` on sources whose listing is server-rendered — the run
    then never starts Chrome and needs no driver in CI.
    """

    context: str = ""
    uses_browser: bool = True

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        storage: Storage | None = None,
        browser: Browser | None = None,
        downloader: Downloader | None = None,
    ) -> None:
        if not self.context:
            raise ScraperError(f"{type(self).__name__}.context must be set")
        self._settings = settings or get_settings()
        self._storage = storage or LocalStorage(self._settings.output_dir)
        self._browser = browser or Browser(
            headless=self._settings.headless,
            timeout_s=self._settings.timeout_s,
            user_agent=self._settings.user_agent,
        )
        self._downloader = downloader or Downloader(
            timeout_s=self._settings.timeout_s,
            max_retries=self._settings.max_retries,
            user_agent=self._settings.user_agent,
        )
        configure_logging(self._settings.log_level)
        self._log = get_logger(f"scraper.{self.context}")

    @abstractmethod
    def discover(self) -> Iterable[ScrapeItem]:
        """Return items to be extracted. Uses self._browser when the source is JS-heavy."""

    @abstractmethod
    def extract(self, item: ScrapeItem) -> Iterable[Artifact]:
        """Turn a discovered item into 0..N artifacts."""

    def on_item_error(self, item: ScrapeItem, exc: Exception) -> None:
        """Override to change per-item error behavior (retry, skip, abort)."""
        self._log.warning("scrape.item_failed", url=item.url, error=str(exc))

    def subpath_for(self, item: ScrapeItem) -> str:  # noqa: ARG002
        """Return the subpath under `context/` this item will populate.

        Used to skip work when the target folder is already populated. Default is
        empty (no skip). Subclasses that persist to slug-based folders should override
        this so skip-if-exists works before the network hit.
        """
        return ""

    def run(self, *, force: bool = False) -> ScrapeResult:
        started_at = datetime.now(tz=UTC)
        result = ScrapeResult(context=self.context)
        self._log.info("scrape.start", context=self.context, force=force)
        browser_ctx = self._browser if self.uses_browser else nullcontext()
        with browser_ctx, self._downloader:
            try:
                items = list(self._safe_discover())
            except DiscoveryError as exc:
                self._log.error("scrape.discovery_failed", error=str(exc))
                raise
            result.discovered = len(items)
            for item in items:
                record = self._new_record(item)
                sub = self.subpath_for(item)
                if not force and sub:
                    probe = f"{self.context}/{sub.strip('/')}"
                    if self._storage.has_files(probe):
                        result.skipped += 1
                        record.status = "skipped"
                        record.files = self._list_existing_files(probe)
                        record.folder = str(Path(self._settings.output_dir) / probe)
                        result.items.append(record)
                        self._log.info("scrape.skip_existing", url=item.url, subpath=sub)
                        continue
                try:
                    artifacts = list(self.extract(item))
                except Exception as exc:
                    result.failed += 1
                    record.status = "failed"
                    result.items.append(record)
                    self.on_item_error(item, exc)
                    continue
                item_files: list[str] = []
                item_folder: str = ""
                item_ok = True
                for art in artifacts:
                    if not art.data:
                        self._log.warning(
                            "scrape.empty_file", url=item.url, filename=art.filename
                        )
                        continue
                    try:
                        target_context = self.context
                        if art.subpath:
                            target_context = f"{self.context}/{art.subpath.strip('/')}"
                        path = self._storage.write_bytes(target_context, art.filename, art.data)
                        result.persisted += 1
                        result.paths.append(path)
                        item_files.append(path)
                        item_folder = str(Path(path).parent)
                        extracted = maybe_unpack_zip(path, logger=self._log)
                        if extracted:
                            result.paths.extend(extracted)
                            item_files.extend(extracted)
                    except Exception as exc:
                        result.failed += 1
                        item_ok = False
                        self._log.warning(
                            "scrape.persist_failed",
                            filename=art.filename,
                            error=str(exc),
                        )
                record.files = item_files
                record.folder = item_folder
                record.downloaded_at = datetime.now(tz=UTC).isoformat(timespec="seconds")
                record.status = "ok" if item_ok else "partial"
                result.items.append(record)
        finished_at = datetime.now(tz=UTC)
        self._write_manifest(result, started_at=started_at, finished_at=finished_at)
        self._log.info(
            "scrape.done",
            context=self.context,
            discovered=result.discovered,
            persisted=result.persisted,
            skipped=result.skipped,
            failed=result.failed,
        )
        return result

    def _safe_discover(self) -> Iterable[ScrapeItem]:
        try:
            yield from self.discover()
        except Exception as exc:
            raise DiscoveryError(str(exc)) from exc

    def _new_record(self, item: ScrapeItem) -> ItemRecord:
        title = item.metadata.get("title", "")
        return ItemRecord(
            slug=self.subpath_for(item),
            title=title,
            description=item.metadata.get("description", title),
            published_at=item.metadata.get("published_at", ""),
            source_url=item.url,
            folder="",
        )

    def _list_existing_files(self, context: str) -> list[str]:
        settings_root = Path(self._settings.output_dir)
        folder = settings_root / context
        if not folder.exists():
            return []
        return sorted(str(p) for p in folder.rglob("*") if p.is_file() and p.name != ".gitkeep")

    def _write_manifest(
        self,
        result: ScrapeResult,
        *,
        started_at: datetime,
        finished_at: datetime,
    ) -> None:
        base_url = self._settings.public_base_url.rstrip("/")
        browse_url = self._settings.browse_base_url.rstrip("/")
        for r in result.items:
            r.file_urls = [self._to_public_url(base_url, p) for p in r.files]
            r.folder_url = self._to_public_url(browse_url, r.folder) if r.folder else ""

        manifest = {
            "context": result.context,
            "public_base_url": f"{base_url}/{result.context}",
            "browse_url": f"{browse_url}/{result.context}",
            "generated_at": finished_at.isoformat(timespec="seconds"),
            "started_at": started_at.isoformat(timespec="seconds"),
            "duration_s": round((finished_at - started_at).total_seconds(), 2),
            "totals": {
                "discovered": result.discovered,
                "persisted": result.persisted,
                "skipped": result.skipped,
                "failed": result.failed,
            },
            "items": [asdict(r) for r in result.items],
        }
        try:
            self._storage.write_text(
                result.context,
                "manifest.json",
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            )
        except Exception as exc:
            self._log.warning("manifest.write_failed", error=str(exc))
            return

        history_context = result.context
        history_root = Path(self._settings.output_dir) / history_context
        history_path = history_root / "history.json"
        entry = {
            "started_at": manifest["started_at"],
            "generated_at": manifest["generated_at"],
            "duration_s": manifest["duration_s"],
            "totals": manifest["totals"],
        }
        history: list[dict] = []
        if history_path.exists():
            try:
                with history_path.open(encoding="utf-8") as fh:
                    history = json.load(fh)
                    if not isinstance(history, list):
                        history = []
            except (OSError, json.JSONDecodeError):
                history = []
        history.append(entry)
        try:
            self._storage.write_text(
                history_context,
                "history.json",
                json.dumps(history, ensure_ascii=False, indent=2) + "\n",
            )
        except Exception as exc:
            self._log.warning("history.write_failed", error=str(exc))

        generated_at = str(manifest["generated_at"])
        self._write_context_feed(
            result, base_url, browse_url=browse_url, generated_at=generated_at
        )
        self._write_root_sitemap(base_url, generated_at=generated_at)
        self._write_root_feed(base_url, generated_at=generated_at)

    def _to_public_url(self, base_url: str, local_path: str) -> str:
        try:
            rel = Path(local_path).resolve().relative_to(Path(self._settings.output_dir).resolve())
        except ValueError:
            return ""
        return f"{base_url}/{rel.as_posix()}"

    def _write_context_feed(
        self,
        result: ScrapeResult,
        base_url: str,
        *,
        browse_url: str,
        generated_at: str,
    ) -> None:
        """Atom feed with one entry per item — newest published_at first, capped at 50."""
        entries: list[dict] = []
        sorted_items = sorted(
            result.items,
            key=lambda r: (r.published_at, r.downloaded_at),
            reverse=True,
        )
        for r in sorted_items[:50]:
            updated = r.published_at
            if updated and len(updated) == 10:
                updated = f"{updated}T00:00:00+00:00"
            entries.append(
                {
                    "id": f"{base_url}/{result.context}/{r.slug}",
                    "title": r.title,
                    "summary": r.description,
                    "link": r.folder_url or f"{browse_url}/{result.context}/{r.slug}",
                    "updated": updated or r.downloaded_at or generated_at,
                }
            )
        feed_xml = build_atom(
            feed_id=f"{base_url}/{result.context}/feed.xml",
            title=f"Stackin data-source — {result.context}",
            subtitle=(
                f"Automated updates from the {result.context.upper()} scraper — "
                "official docs, XSDs, technical notes."
            ),
            self_url=f"{base_url}/{result.context}/feed.xml",
            site_url=f"{browse_url}/{result.context}",
            updated=generated_at,
            entries=entries,
        )
        try:
            self._storage.write_text(result.context, "feed.xml", feed_xml)
        except Exception as exc:
            self._log.warning("feed.write_failed", error=str(exc))

    def _write_root_feed(self, base_url: str, *, generated_at: str) -> None:
        """Root Atom feed aggregating the top-N most recent items across every context.
        Subscribers who want everything follow this one URL."""
        root = Path(self._settings.output_dir)
        aggregated: list[dict] = []
        for m in sorted(root.rglob("manifest.json")):
            if m.parent == root:
                continue
            try:
                with m.open(encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue
            ctx = data.get("context", str(m.parent.relative_to(root)))
            for it in data.get("items", []):
                updated = it.get("published_at") or ""
                if updated and len(updated) == 10:
                    updated = f"{updated}T00:00:00+00:00"
                aggregated.append(
                    {
                        "id": f"{base_url}/{ctx}/{it.get('slug', '')}",
                        "title": f"[{ctx.upper()}] {it.get('title', '')}",
                        "summary": it.get("description", ""),
                        "link": it.get("folder_url", ""),
                        "updated": updated or it.get("downloaded_at") or generated_at,
                    }
                )
        aggregated.sort(key=lambda e: e.get("updated", ""), reverse=True)
        feed_xml = build_atom(
            feed_id=f"{base_url}/feed.xml",
            title="Stackin data-source — todas as fontes",
            subtitle="Todas as atualizações fiscais oficiais indexadas pelo Stackin.",
            self_url=f"{base_url}/feed.xml",
            site_url=self._settings.browse_base_url.rstrip("/"),
            updated=generated_at,
            entries=aggregated[:100],
        )
        try:
            (root / "feed.xml").write_text(feed_xml, encoding="utf-8")
        except OSError as exc:
            self._log.warning("root_feed.write_failed", error=str(exc))

    def _write_root_sitemap(self, base_url: str, *, generated_at: str) -> None:
        """Aggregate every context's manifest under `data/manifest.json` — the
        top-level sitemap consumers can hit to discover which datasets exist."""
        root = Path(self._settings.output_dir)
        entries: list[dict] = []
        browse_url = self._settings.browse_base_url.rstrip("/")
        for m in sorted(root.rglob("manifest.json")):
            if m.parent == root:
                continue
            try:
                with m.open(encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue
            rel = m.parent.relative_to(root).as_posix()
            entries.append(
                {
                    "context": data.get("context", rel),
                    "manifest_url": f"{base_url}/{rel}/manifest.json",
                    "feed_url": f"{base_url}/{rel}/feed.xml",
                    "browse_url": f"{browse_url}/{rel}",
                    "generated_at": data.get("generated_at", ""),
                    "totals": data.get("totals", {}),
                }
            )
        root_manifest = {
            "generated_at": generated_at,
            "public_base_url": base_url,
            "browse_base_url": browse_url,
            "feed_url": f"{base_url}/feed.xml",
            "contexts": entries,
        }
        try:
            (root / "manifest.json").write_text(
                json.dumps(root_manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            self._log.warning("root_manifest.write_failed", error=str(exc))

    def download(self, url: str) -> bytes:
        """Convenience: use the shared Downloader (retry+backoff)."""
        return self._downloader.get(url)

    @property
    def browser(self) -> Browser:
        return self._browser

    @property
    def settings(self) -> Settings:
        return self._settings
