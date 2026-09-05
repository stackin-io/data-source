from __future__ import annotations

import hashlib
from urllib.parse import urlparse

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from data_source.core.logger import get_logger
from data_source.exceptions import DownloadError


class Downloader:
    """HTTP downloader with retry + exponential backoff. Streams to memory (files ≤ 50 MB)."""

    def __init__(
        self,
        *,
        timeout_s: int = 30,
        max_retries: int = 3,
        user_agent: str | None = None,
    ) -> None:
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        headers = {"User-Agent": user_agent} if user_agent else {}
        self._client = httpx.Client(timeout=timeout_s, follow_redirects=True, headers=headers)
        self._log = get_logger(__name__)

    def __enter__(self) -> "Downloader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self._client.close()

    def _fetch(self, url: str) -> bytes:
        @retry(
            reraise=True,
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPError,)),
        )
        def _do() -> bytes:
            self._log.info("download.start", url=url)
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp.content

        try:
            return _do()
        except httpx.HTTPError as exc:
            raise DownloadError(f"failed to download {url}: {exc}") from exc

    def get(self, url: str) -> bytes:
        return self._fetch(url)

    @staticmethod
    def suggest_filename(url: str) -> str:
        """Deterministic filename from URL — original name if present, hash otherwise."""
        path = urlparse(url).path
        name = path.rsplit("/", 1)[-1] if path else ""
        if name and "." in name:
            return name
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        ext = _guess_ext(url)
        return f"{digest}{ext}"


def _guess_ext(url: str) -> str:
    low = url.lower()
    for ext in (".xml", ".xsd", ".pdf", ".zip", ".html"):
        if low.endswith(ext):
            return ext
    return ".bin"
