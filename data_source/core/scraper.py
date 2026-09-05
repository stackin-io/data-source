from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field

from data_source.config import Settings, get_settings
from data_source.core.browser import Browser
from data_source.core.downloader import Downloader
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
class ScrapeResult:
    context: str
    discovered: int = 0
    persisted: int = 0
    skipped: int = 0
    failed: int = 0
    paths: list[str] = field(default_factory=list)


class BaseScraper(ABC):
    """Template Method — subclasses override discover() and extract().

    Base owns: browser lifecycle, retry, storage, logging, error containment.
    Subclasses own: what pages exist for this source, how each page turns into files.
    """

    context: str = ""

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
        result = ScrapeResult(context=self.context)
        self._log.info("scrape.start", context=self.context, force=force)
        with self._browser, self._downloader:
            try:
                items = list(self._safe_discover())
            except DiscoveryError as exc:
                self._log.error("scrape.discovery_failed", error=str(exc))
                raise
            result.discovered = len(items)
            for item in items:
                if not force:
                    sub = self.subpath_for(item)
                    if sub:
                        probe = f"{self.context}/{sub.strip('/')}"
                        if self._storage.has_files(probe):
                            result.skipped += 1
                            self._log.info("scrape.skip_existing", url=item.url, subpath=sub)
                            continue
                try:
                    artifacts = list(self.extract(item))
                except Exception as exc:
                    result.failed += 1
                    self.on_item_error(item, exc)
                    continue
                for art in artifacts:
                    try:
                        target_context = self.context
                        if art.subpath:
                            target_context = f"{self.context}/{art.subpath.strip('/')}"
                        path = self._storage.write_bytes(target_context, art.filename, art.data)
                        result.persisted += 1
                        result.paths.append(path)
                        extracted = maybe_unpack_zip(path, logger=self._log)
                        if extracted:
                            result.paths.extend(extracted)
                    except Exception as exc:
                        result.failed += 1
                        self._log.warning(
                            "scrape.persist_failed",
                            filename=art.filename,
                            error=str(exc),
                        )
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

    def download(self, url: str) -> bytes:
        """Convenience: use the shared Downloader (retry+backoff)."""
        return self._downloader.get(url)

    @property
    def browser(self) -> Browser:
        return self._browser

    @property
    def settings(self) -> Settings:
        return self._settings
