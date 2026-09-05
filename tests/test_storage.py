import tempfile
import unittest
from pathlib import Path

from data_source.core.storage import LocalStorage


class TestLocalStorage(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.storage = LocalStorage(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_write_bytes_creates_context_folder(self):
        path = self.storage.write_bytes("nfe", "example.xml", b"<xml/>")

        written = Path(path)
        self.assertTrue(written.exists())
        self.assertEqual(written.read_bytes(), b"<xml/>")
        self.assertEqual(written.parent.name, "nfe")

    def test_write_bytes_supports_nested_context(self):
        path = self.storage.write_bytes("nfe/some-slug", "a.xsd", b"x")

        written = Path(path)
        self.assertEqual(written.parent.name, "some-slug")
        self.assertEqual(written.parent.parent.name, "nfe")

    def test_write_text_encodes_utf8(self):
        path = self.storage.write_text("nfse", "readme.txt", "olá")

        self.assertEqual(Path(path).read_bytes(), "olá".encode())

    def test_exists_after_write(self):
        self.storage.write_bytes("nfe", "a.xsd", b"x")

        self.assertTrue(self.storage.exists("nfe", "a.xsd"))
        self.assertFalse(self.storage.exists("nfe", "missing.xsd"))

    def test_write_overwrites_same_filename_same_day(self):
        first = self.storage.write_bytes("nfe", "same.xml", b"1")
        second = self.storage.write_bytes("nfe", "same.xml", b"2")

        self.assertEqual(first, second)
        self.assertEqual(Path(first).read_bytes(), b"2")


if __name__ == "__main__":
    unittest.main()
