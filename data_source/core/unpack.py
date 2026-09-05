from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any


def maybe_unpack_zip(archive_path: str, *, logger: Any | None = None) -> list[str]:
    """If `archive_path` is a valid ZIP, extract next to it and return the list of
    extracted file paths. Returns [] for non-zip files or corrupted archives.

    Extraction target: `<archive_dir>/<archive_stem>/`. Idempotent — if the target
    folder already exists and is non-empty, we skip.
    """
    p = Path(archive_path)
    if not p.exists() or p.suffix.lower() != ".zip":
        return []

    if not zipfile.is_zipfile(p):
        if logger is not None:
            logger.warning("unpack.not_a_zip", path=str(p))
        return []

    target = p.with_suffix("")
    target.mkdir(parents=True, exist_ok=True)
    already = [c for c in target.iterdir() if c.name != ".gitkeep"]
    if already:
        if logger is not None:
            logger.info("unpack.skip_existing", target=str(target), files=len(already))
        return [str(c) for c in already]

    extracted: list[str] = []
    try:
        with zipfile.ZipFile(p) as zf:
            for member in zf.infolist():
                dest = _safe_extract_path(target, member.filename)
                if dest is None:
                    if logger is not None:
                        logger.warning("unpack.zip_slip_blocked", entry=member.filename)
                    continue
                if member.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                extracted.append(str(dest))
    except zipfile.BadZipFile as exc:
        if logger is not None:
            logger.warning("unpack.bad_zip", path=str(p), error=str(exc))
        return []

    if logger is not None:
        logger.info("unpack.done", zip=str(p), target=str(target), extracted=len(extracted))
    return extracted


def _safe_extract_path(base: Path, member_name: str) -> Path | None:
    """Prevent zip-slip: resolve member and ensure it stays under base."""
    dest = (base / member_name).resolve()
    try:
        dest.relative_to(base.resolve())
    except ValueError:
        return None
    return dest
