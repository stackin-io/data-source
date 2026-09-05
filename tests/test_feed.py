import unittest
from xml.etree import ElementTree as ET

from data_source.core.feed import build_atom


class TestBuildAtom(unittest.TestCase):

    def _parse(self, xml: str) -> ET.Element:
        return ET.fromstring(xml.encode("utf-8"))

    def test_produces_valid_atom_with_required_fields(self):
        xml = build_atom(
            feed_id="urn:test",
            title="Stackin — nfe",
            subtitle="s",
            self_url="https://x/nfe/feed.xml",
            site_url="https://x/nfe/",
            updated="2026-09-05T00:00:00+00:00",
            entries=[],
        )
        root = self._parse(xml)

        ns = "{http://www.w3.org/2005/Atom}"
        self.assertEqual(root.tag, f"{ns}feed")
        self.assertIsNotNone(root.find(f"{ns}id"))
        self.assertIsNotNone(root.find(f"{ns}title"))
        self.assertIsNotNone(root.find(f"{ns}updated"))

    def test_serializes_each_entry(self):
        xml = build_atom(
            feed_id="urn:test",
            title="t",
            subtitle="",
            self_url="https://x/feed.xml",
            site_url="https://x/",
            updated="2026-09-05T00:00:00+00:00",
            entries=[
                {
                    "id": "urn:a",
                    "title": "A",
                    "summary": "sa",
                    "link": "https://x/a",
                    "updated": "2026-08-01T00:00:00+00:00",
                },
                {
                    "id": "urn:b",
                    "title": "B",
                    "summary": "sb",
                    "link": "https://x/b",
                    "updated": "2026-07-01T00:00:00+00:00",
                },
            ],
        )

        ns = "{http://www.w3.org/2005/Atom}"
        entries = self._parse(xml).findall(f"{ns}entry")
        self.assertEqual(len(entries), 2)
        titles = [e.findtext(f"{ns}title") for e in entries]
        self.assertEqual(titles, ["A", "B"])

    def test_starts_with_xml_prolog(self):
        xml = build_atom(
            feed_id="urn:x",
            title="t",
            subtitle="",
            self_url="https://x/f.xml",
            site_url="https://x/",
            updated="",
            entries=[],
        )
        self.assertTrue(xml.startswith('<?xml version="1.0" encoding="utf-8"?>'))


if __name__ == "__main__":
    unittest.main()
