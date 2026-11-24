import hashlib
import json
import unittest
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _latest(pattern):
    found = sorted(DATA.glob(pattern))
    if not found:
        raise AssertionError(f"nothing matches data/{pattern}")
    return found[-1]


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


CURATED_PATH = _latest("curated/mei-ctribnac/*/mei-ctribnac.json")
CURATED = _json(CURATED_PATH)
SOURCES = {Path(s["path"]).parts[1]: ROOT / s["path"] for s in CURATED["sources"]}


def _anexo_b():
    sheet = openpyxl.load_workbook(SOURCES["nfse"], read_only=True)["LISTA.SERV.NAC."]
    return {
        str(row[0]).zfill(6): " ".join(str(row[4]).split())
        for row in list(sheet.iter_rows(values_only=True))[1:]
        if row[0] is not None
    }


ANEXO_B = _anexo_b()
ANEXO_XI = _json(SOURCES["rfb"])["rows"]
IBGE = {row["code"] for row in _json(SOURCES["ibge"])["rows"]}


class TestHeader(unittest.TestCase):
    def test_says_curated_and_not_official(self):
        self.assertIs(CURATED["curated"], True)
        self.assertIs(CURATED["official"], False)
        self.assertIn("not official", CURATED["notes"])
        self.assertRegex(CURATED["reviewed_at"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(CURATED_PATH.parent.name, CURATED["reviewed_at"])

    def test_sources_are_mirrored_here(self):
        self.assertEqual(set(SOURCES), {"rfb", "ibge", "nfse"})
        for source in CURATED["sources"]:
            path = ROOT / source["path"]
            self.assertTrue(path.is_file(), source["path"])
            self.assertEqual(
                source["sha256"], hashlib.sha256(path.read_bytes()).hexdigest(), source["path"]
            )


class TestEntries(unittest.TestCase):
    def test_one_entry_per_anexo_xi_cnae_with_iss(self):
        with_iss = {row["cnae"] for row in ANEXO_XI if row["iss"]}

        self.assertEqual(set(CURATED["entries"]), with_iss)

    def test_every_cnae_is_an_ibge_subclass(self):
        self.assertLessEqual(set(CURATED["entries"]), IBGE)

    def test_occupations_are_the_anexo_xi_ones(self):
        for cnae, entry in CURATED["entries"].items():
            expected = [row["occupation"] for row in ANEXO_XI if row["cnae"] == cnae and row["iss"]]
            self.assertEqual(entry["occupations"], expected, cnae)

    def test_every_ctribnac_is_in_anexo_b(self):
        for cnae, entry in CURATED["entries"].items():
            for code in entry["ctribnac"]:
                self.assertIn(code, ANEXO_B, f"{cnae} → {code}")

    def test_the_code_index_matches_anexo_b(self):
        used = {code for entry in CURATED["entries"].values() for code in entry["ctribnac"]}

        self.assertEqual(set(CURATED["ctribnac"]), used)
        for code, description in CURATED["ctribnac"].items():
            self.assertEqual(description, ANEXO_B[code], code)

    def test_every_entry_has_a_reason(self):
        for cnae, entry in CURATED["entries"].items():
            self.assertTrue(entry["reason"].strip(), cnae)
            self.assertIsInstance(entry["needs_review"], bool)
            self.assertEqual(entry["ctribnac"], sorted(set(entry["ctribnac"])), cnae)

    def test_it_consulting_and_software_are_linked_to_no_cnae(self):
        used = {code for entry in CURATED["entries"].values() for code in entry["ctribnac"]}

        self.assertNotIn("010601", used)
        self.assertFalse([code for code in used if code.startswith(("0101", "0102"))])

    def test_known_occupations(self):
        entries = CURATED["entries"]

        self.assertEqual(entries["8599603"]["ctribnac"], ["080201"])
        self.assertEqual(entries["9511800"]["ctribnac"], ["140101", "140201"])
        self.assertNotIn("6204000", entries)


if __name__ == "__main__":
    unittest.main()
