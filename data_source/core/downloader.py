from __future__ import annotations

import hashlib
import re
import time
import unicodedata
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from data_source.core.logger import get_logger
from data_source.exceptions import DownloadError

_CONTENT_TYPE_EXT = {
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/octet-stream": ".bin",
}


@dataclass(frozen=True)
class DownloadedFile:
    data: bytes
    filename: str
    content_type: str


class Downloader:
    """HTTP downloader with retry + exponential backoff and courtesy throttling."""

    def __init__(
        self,
        *,
        timeout_s: int = 30,
        max_retries: int = 3,
        user_agent: str | None = None,
        throttle_ms: int = 750,
    ) -> None:
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._throttle_s = throttle_ms / 1000.0
        headers = {"User-Agent": user_agent} if user_agent else {}
        self._client = httpx.Client(timeout=timeout_s, follow_redirects=True, headers=headers)
        self._log = get_logger(__name__)
        self._last_request_at = 0.0

    def __enter__(self) -> "Downloader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self._client.close()

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._throttle_s:
            time.sleep(self._throttle_s - elapsed)
        self._last_request_at = time.monotonic()

    def fetch(self, url: str, *, title_hint: str | None = None) -> DownloadedFile:
        @retry(
            reraise=True,
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPError,)),
        )
        def _do() -> httpx.Response:
            self._throttle()
            self._log.info("download.start", url=url)
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp

        try:
            resp = _do()
        except httpx.HTTPError as exc:
            raise DownloadError(f"failed to download {url}: {exc}") from exc

        content_type = resp.headers.get("content-type", "application/octet-stream").split(";")[0]
        filename = self._resolve_filename(url, resp.headers, title_hint, content_type)
        return DownloadedFile(data=resp.content, filename=filename, content_type=content_type)

    def get(self, url: str) -> bytes:
        return self.fetch(url).data

    def _resolve_filename(
        self,
        url: str,
        headers: httpx.Headers,
        title_hint: str | None,
        content_type: str,
    ) -> str:
        cd = headers.get("content-disposition", "")
        name = _parse_content_disposition(cd)
        if name:
            return name

        path = urlparse(url).path
        tail = path.rsplit("/", 1)[-1] if path else ""
        if tail and "." in tail:
            return tail

        ext = _CONTENT_TYPE_EXT.get(content_type, "")
        if title_hint:
            slug = _slugify(title_hint)
            if not ext and tail:
                ext = ""  # unknown
            return f"{slug}{ext or '.bin'}"

        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        return f"{digest}{ext or '.bin'}"

    @staticmethod
    def suggest_filename(url: str) -> str:
        path = urlparse(url).path
        name = path.rsplit("/", 1)[-1] if path else ""
        if name and "." in name:
            return name
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        return f"{digest}.bin"


_CD_STAR_RE = re.compile(r"filename\*\s*=\s*[^']*'[^']*'(?P<v>[^;]+)", re.IGNORECASE)
_CD_RE = re.compile(r'filename\s*=\s*"?(?P<v>[^";]+)"?', re.IGNORECASE)


def _parse_content_disposition(header: str) -> str | None:
    if not header:
        return None
    m = _CD_STAR_RE.search(header)
    if m:
        return unquote(m.group("v").strip())
    m = _CD_RE.search(header)
    if m:
        return m.group("v").strip()
    return None


def slugify(text: str, *, max_len: int = 120) -> str:
    """Lowercase ASCII slug from link text. Accents stripped (`ç`→`c`, `ã`→`a`),
    spaces→dashes, punctuation dropped, dashes collapsed."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.strip().lower()
    ascii_text = re.sub(r"\s+", "-", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9.\-]+", "", ascii_text)
    ascii_text = re.sub(r"-{2,}", "-", ascii_text)
    ascii_text = ascii_text.strip(".-")
    return ascii_text[:max_len] or "file"


_slugify = slugify
