import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from data_source.core.unpack import maybe_unpack_zip


def _make_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)


class TestMaybeUnpackZip(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_ignores_non_zip_suffix(self):
        f = self.root / "readme.pdf"
        f.write_bytes(b"%PDF")

        self.assertEqual(maybe_unpack_zip(str(f)), [])

    def test_ignores_missing_file(self):
        self.assertEqual(maybe_unpack_zip(str(self.root / "missing.zip")), [])

    def test_extracts_flat_zip_next_to_archive(self):
        zip_path = self.root / "pack.zip"
        _make_zip(zip_path, {"a.xsd": b"<a/>", "b.xsd": b"<b/>"})

        extracted = maybe_unpack_zip(str(zip_path))

        target = self.root / "pack"
        self.assertTrue((target / "a.xsd").exists())
        self.assertTrue((target / "b.xsd").exists())
        self.assertEqual(len(extracted), 2)

    def test_blocks_zip_slip(self):
        zip_path = self.root / "evil.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../../pwned.txt", b"nope")
        zip_path.write_bytes(buf.getvalue())

        extracted = maybe_unpack_zip(str(zip_path))

        self.assertEqual(extracted, [])
        self.assertFalse((self.root.parent / "pwned.txt").exists())

    def test_skips_when_target_already_populated(self):
        zip_path = self.root / "pack.zip"
        _make_zip(zip_path, {"a.xsd": b"<a/>"})
        target = self.root / "pack"
        target.mkdir()
        (target / "prev.xsd").write_bytes(b"old")

        extracted = maybe_unpack_zip(str(zip_path))

        # existing file preserved, no new extraction
        self.assertEqual(len(extracted), 1)
        self.assertTrue((target / "prev.xsd").exists())
        self.assertFalse((target / "a.xsd").exists())


if __name__ == "__main__":
    unittest.main()
