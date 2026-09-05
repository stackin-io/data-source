from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from data_source.core.logger import get_logger
from data_source.exceptions import StorageError


class Storage(Protocol):
    """Persistence boundary. Any backend (local FS, S3, GCS) implements this."""

    def write_bytes(self, context: str, filename: str, data: bytes) -> str: ...

    def write_text(self, context: str, filename: str, text: str) -> str: ...

    def exists(self, context: str, filename: str) -> bool: ...

    def has_files(self, context: str) -> bool: ...


class LocalStorage:
    """Writes into `<root>/<context>/<yyyy-mm-dd>/<filename>`. Idempotent per day."""

    def __init__(self, root: Path, *, dated: bool = False) -> None:
        self._root = Path(root)
        self._dated = dated
        self._log = get_logger(__name__)
        self._root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, context: str, filename: str) -> Path:
        parts: list[str] = [context]
        if self._dated:
            parts.append(datetime.now(tz=UTC).strftime("%Y-%m-%d"))
        target = self._root.joinpath(*parts, filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write_bytes(self, context: str, filename: str, data: bytes) -> str:
        target = self._resolve(context, filename)
        try:
            target.write_bytes(data)
        except OSError as exc:
            raise StorageError(f"failed to write {target}: {exc}") from exc
        self._log.info("storage.wrote", path=str(target), bytes=len(data))
        return str(target)

    def write_text(self, context: str, filename: str, text: str) -> str:
        return self.write_bytes(context, filename, text.encode("utf-8"))

    def exists(self, context: str, filename: str) -> bool:
        return self._resolve(context, filename).exists()

    def has_files(self, context: str) -> bool:
        """True if the context folder already contains at least one real file.
        Used to skip re-downloading items whose target folder is already populated."""
        parts: list[str] = [context]
        if self._dated:
            parts.append(datetime.now(tz=UTC).strftime("%Y-%m-%d"))
        folder = self._root.joinpath(*parts)
        if not folder.exists():
            return False
        return any(
            entry.is_file() and entry.name != ".gitkeep"
            for entry in folder.iterdir()
        )
