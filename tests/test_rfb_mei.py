import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from data_source.config import Settings
from data_source.core.downloader import DownloadedFile
from data_source.core.storage import LocalStorage
from data_source.exceptions import DiscoveryError, ExtractionError
from data_source.scrapers import REGISTRY, rfb_mei
from data_source.scrapers.rfb_mei import (
    ANEXO_XI_URL,
    RfbMeiOcupacoesScraper,
    parse_anexo_xi,
)

PDF = (Path(__file__).parent / "fixtures" / "anexo_xi.pdf").read_bytes()
LAST_MODIFIED = "Fri, 06 Mar 2026 20:58:44 GMT"
ROWS = parse_anexo_xi(PDF)


def _by_occupation(name):
    return next(r for r in ROWS if r["occupation"] == name)


class TestParseRealPdf(unittest.TestCase):
    def test_row_count_and_tables(self):
        self.assertEqual(len(ROWS), 471)
        self.assertEqual(sum(r["table"] == "A" for r in ROWS), 467)
        self.assertEqual(sum(r["table"] == "B" for r in ROWS), 4)

    def test_every_row_is_well_formed(self):
        for row in ROWS:
            self.assertEqual(
                set(row), {"occupation", "cnae", "cnae_description", "iss", "icms", "table"}
            )
            self.assertRegex(row["cnae"], r"^\d{7}$")
            self.assertIsInstance(row["iss"], bool)
            self.assertIsInstance(row["icms"], bool)
            self.assertTrue(row["occupation"])
            self.assertTrue(row["cnae_description"])
            self.assertNotIn("\n", row["occupation"] + row["cnae_description"])

    def test_first_row(self):
        self.assertEqual(
            ROWS[0],
            {
                "occupation": "ABATEDOR(A) DE AVES COM COMERCIALIZAÇÃO DO PRODUTO INDEPENDENTE",
                "cnae": "4724500",
                "cnae_description": "COMÉRCIO VAREJISTA DE HORTIFRUTIGRANJEIROS",
                "iss": False,
                "icms": True,
                "table": "A",
            },
        )

    def test_multi_line_cells_are_joined(self):
        row = _by_occupation("ACABADOR(A) DE CALÇADOS INDEPENDENTE")

        self.assertEqual(row["cnae_description"], "ACABAMENTO DE CALÇADOS DE COURO SOB CONTRATO")
        self.assertEqual(row["iss"], True)

    def test_a_row_cut_by_the_page_break_is_folded_back(self):
        row = _by_occupation("POCEIRO/CISTERNEIRO/CACIMBEIRO INDEPENDENTE")

        self.assertEqual(row["cnae"], "4399105")
        self.assertEqual(row["cnae_description"], "PERFURAÇÃO E CONSTRUÇÃO DE POÇOS DE ÁGUA")
        self.assertFalse(any(r["occupation"].startswith("CACIMBEIRO") for r in ROWS))

    def test_a_hyphenated_word_runs_on(self):
        rows = [r for r in ROWS if r["cnae"] == "8712300"]

        self.assertTrue(rows)
        self.assertIn("INFRA-ESTRUTURA", rows[0]["cnae_description"])

    def test_the_description_that_spills_into_the_iss_column(self):
        row = _by_occupation("CHURRASQUEIRO(A) EM DOMICÍLIO INDEPENDENTE")

        self.assertEqual(
            row["cnae_description"], "SERVIÇOS DE ALIMENTAÇÃO PARA EVENTOS E RECEPÇÕES - BUFÊ"
        )
        self.assertTrue(row["iss"])
        self.assertTrue(row["icms"])

    def test_known_occupations(self):
        self.assertTrue(any(r["cnae"] == "8599603" and r["iss"] and not r["icms"] for r in ROWS))
        self.assertTrue(any(r["cnae"] == "9511800" and r["iss"] for r in ROWS))
        self.assertFalse(any(r["cnae"] == "6204000" for r in ROWS))

    def test_tabela_b_is_the_autonomous_cargo_carrier(self):
        table_b = [r for r in ROWS if r["table"] == "B"]

        self.assertEqual([r["cnae"] for r in table_b], ["4930201", "4930202", "4930203", "4930204"])
        self.assertTrue(all(r["occupation"].startswith("TRANSPORTADOR") for r in table_b))


class TestParseErrors(unittest.TestCase):
    def test_not_a_pdf(self):
        with self.assertRaises(ExtractionError):
            parse_anexo_xi(b"<html>blocked</html>")

    def _parse(self, table):
        page = MagicMock()
        page.extract_tables.return_value = [table]
        pdf = MagicMock()
        pdf.__enter__.return_value.pages = [page]
        with patch.object(rfb_mei.pdfplumber, "open", return_value=pdf):
            return parse_anexo_xi(b"%PDF")

    def test_blank_rows_are_ignored(self):
        rows = self._parse(
            [
                ["TABELA A", "", "", "", ""],
                [None, None, None, None, None],
                ["X INDEPENDENTE", "4724-5/00", "COMÉRCIO", "N", "S"],
                ["", "", "", "", ""],
            ]
        )

        self.assertEqual([r["cnae"] for r in rows], ["4724500"])

    def test_a_row_that_does_not_parse_is_an_error(self):
        table = [
            ["TABELA A", "", "", "", ""],
            ["OCUPAÇÃO", "CNAE", "DESCRIÇÃO SUBCLASSE CNAE", "ISS", "ICMS"],
            ["X INDEPENDENTE", "4724-5/00", "COMÉRCIO", "X", "S"],
        ]
        page = MagicMock()
        page.extract_tables.return_value = [table]
        pdf = MagicMock()
        pdf.__enter__.return_value.pages = [page]

        with (
            patch.object(rfb_mei.pdfplumber, "open", return_value=pdf),
            self.assertRaises(ExtractionError),
        ):
            parse_anexo_xi(b"%PDF")


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.pdf = PDF
        self.last_modified = LAST_MODIFIED
        downloader = MagicMock()
        downloader.__enter__.return_value = downloader
        downloader.fetch.side_effect = self._serve
        parse = patch.object(rfb_mei, "parse_anexo_xi", return_value=ROWS)
        parse.start()
        self.addCleanup(parse.stop)
        self.scraper = RfbMeiOcupacoesScraper(
            settings=Settings(output_dir=self.root, max_retries=1),
            storage=LocalStorage(self.root),
            browser=MagicMock(),
            downloader=downloader,
        )

    def _serve(self, url):
        if url != ANEXO_XI_URL:
            raise AssertionError(url)
        return DownloadedFile(
            data=self.pdf,
            filename="Anexo_XI.pdf",
            content_type="application/pdf",
            last_modified=self.last_modified,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def _folders(self):
        return sorted(p.name for p in (self.root / "rfb/mei-ocupacoes").glob("*_anexo-xi-*"))


class TestRun(_Base):
    def test_registered(self):
        self.assertIs(REGISTRY["rfb/mei-ocupacoes"], RfbMeiOcupacoesScraper)

    def test_writes_the_pdf_and_the_json(self):
        result = self.scraper.run()

        self.assertEqual(result.persisted, 2)
        folder = self.root / "rfb/mei-ocupacoes/2026-03-06_anexo-xi-cgsn-140"
        self.assertEqual((folder / "Anexo_XI.pdf").read_bytes(), PDF)
        payload = json.loads((folder / "anexo-xi.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["source"], ANEXO_XI_URL)
        self.assertEqual(payload["last_modified"], LAST_MODIFIED)
        self.assertEqual(payload["sha256"], hashlib.sha256(PDF).hexdigest())
        self.assertEqual(len(payload["rows"]), 471)

    def test_same_pdf_is_skipped(self):
        self.scraper.run()
        self.last_modified = "Sat, 07 Mar 2026 10:00:00 GMT"
        result = self.scraper.run()

        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.persisted, 0)
        self.assertEqual(self._folders(), ["2026-03-06_anexo-xi-cgsn-140"])

    def test_changed_pdf_with_the_same_date_gets_its_own_folder(self):
        self.scraper.run()
        self.pdf = PDF + b"\n"
        result = self.scraper.run()

        self.assertEqual(result.persisted, 2)
        digest = hashlib.sha256(self.pdf).hexdigest()[:8]
        self.assertEqual(
            self._folders(),
            ["2026-03-06_anexo-xi-cgsn-140", f"2026-03-06_anexo-xi-cgsn-140-{digest}"],
        )

    def test_a_folder_without_its_json_is_not_reused(self):
        partial = self.root / "rfb/mei-ocupacoes/2026-03-06_anexo-xi-cgsn-140"
        partial.mkdir(parents=True)
        (partial / "Anexo_XI.pdf").write_bytes(PDF)

        result = self.scraper.run()

        self.assertEqual(result.persisted, 2)
        digest = hashlib.sha256(PDF).hexdigest()[:8]
        self.assertTrue(
            (
                self.root / f"rfb/mei-ocupacoes/2026-03-06_anexo-xi-cgsn-140-{digest}/anexo-xi.json"
            ).is_file()
        )

    def test_latest_snapshot_is_the_newest_generated_at(self):
        folder = self.root / "rfb/mei-ocupacoes"
        for name, generated_at, digest in (
            ("2026-03-06_anexo-xi-cgsn-140", "2026-03-06T10:00:00+00:00", "old"),
            (
                "2026-03-06_anexo-xi-cgsn-140-0000aaaa",
                "2026-03-08T10:00:00+00:00",
                hashlib.sha256(PDF).hexdigest(),
            ),
            ("2026-03-06_anexo-xi-cgsn-140-ffffffff", "2026-03-07T10:00:00+00:00", "older"),
        ):
            (folder / name).mkdir(parents=True)
            (folder / name / "Anexo_XI.pdf").write_bytes(b"%PDF")
            (folder / name / "anexo-xi.json").write_text(
                json.dumps({"generated_at": generated_at, "sha256": digest}), encoding="utf-8"
            )

        result = self.scraper.run()

        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.persisted, 0)

    def test_no_last_modified_uses_today(self):
        self.last_modified = ""
        [item] = list(self.scraper.discover())

        self.assertRegex(item.metadata["subpath"], r"^\d{4}-\d{2}-\d{2}_anexo-xi-cgsn-140$")

    def test_too_few_rows_fails_discovery_and_writes_nothing(self):
        with patch.object(rfb_mei, "MIN_ROWS", 1000), self.assertRaises(DiscoveryError):
            self.scraper.run()

        self.assertEqual(self._folders(), [])


if __name__ == "__main__":
    unittest.main()
