"""Atom 1.0 feed builder — turns a manifest into a subscribable newsletter feed."""

from __future__ import annotations

from datetime import UTC, datetime
from xml.etree import ElementTree as ET

ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", ATOM_NS)


def build_atom(
    *,
    feed_id: str,
    title: str,
    subtitle: str,
    self_url: str,
    site_url: str,
    updated: str,
    entries: list[dict],
    author_name: str = "Stackin",
    author_email: str = "bot@stackin.io",
) -> str:
    """Render an Atom 1.0 document from a list of entry dicts.

    Each entry dict must expose: id, title, summary, link, updated. Missing keys
    are tolerated — the feed still validates, just with fewer fields.
    """
    root = ET.Element(f"{{{ATOM_NS}}}feed")
    _text(root, "id", feed_id)
    _text(root, "title", title)
    if subtitle:
        _text(root, "subtitle", subtitle)
    _text(root, "updated", updated or _iso_now())
    ET.SubElement(root, f"{{{ATOM_NS}}}link", rel="self", href=self_url)
    ET.SubElement(root, f"{{{ATOM_NS}}}link", rel="alternate", href=site_url)
    author = ET.SubElement(root, f"{{{ATOM_NS}}}author")
    _text(author, "name", author_name)
    _text(author, "email", author_email)

    for entry in entries:
        e = ET.SubElement(root, f"{{{ATOM_NS}}}entry")
        _text(e, "id", entry.get("id", ""))
        _text(e, "title", entry.get("title", ""))
        _text(e, "updated", entry.get("updated") or _iso_now())
        link = entry.get("link", "")
        if link:
            ET.SubElement(e, f"{{{ATOM_NS}}}link", rel="alternate", href=link)
        summary = entry.get("summary", "")
        if summary:
            _text(e, "summary", summary)

    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")


def _text(parent: ET.Element, tag: str, value: str) -> None:
    node = ET.SubElement(parent, f"{{{ATOM_NS}}}{tag}")
    node.text = value or ""


def _iso_now() -> str:
    return datetime.now(tz=UTC).isoformat(timespec="seconds")
