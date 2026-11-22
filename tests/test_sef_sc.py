import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from xml.sax.saxutils import escape

from data_source.config import Settings
from data_source.core.storage import LocalStorage
from data_source.exceptions import DiscoveryError
from data_source.scrapers import REGISTRY, sef_sc
from data_source.scrapers.sef_sc import (
    VERSIONS_URL,
    SefScCBenefScraper,
    parse_table,
)

TABLE = (
    "versão=31 INF_ADIC, DESC_INF, DT_INI, DT_FIM\r\n"
    "SC850001|Crédito Presumido - RICMS/SC-01, Anexo 2, Art. 15, III|01012023|\r\n"
    "SC850019|Crédito Presumido - RICMS/SC-01, Anexo 2, Art. 15, XXXVI|01012023|30062023\r\n"
    "SC810001|Isenção - RICMS/SC-01, Anexo 2, Art. 1º, I|01012023|\r\n"
    "SC830141|Diferimento - RICMS/SC-01, Anexo 3, Arts. 3º a 10-K|01102024|31102026\r\n"
    "SC999999|Benefício fiscal cujo cBenef não foi contemplado na lista. Informar "
    "capitulação legal nas informações complementares.|01102024|\r\n"
    "SC830141|Diferimento - RICMS/SC-01, Anexo 3|01112026|\r\n"
).encode("latin-1")


def _versions(table: bytes = TABLE, version: str = "31") -> bytes:
    digest = hashlib.sha1(table, usedforsecurity=False).hexdigest().upper()
    metadata = (
        '\ufeff<?xml version="1.0" encoding="utf-8"?>'
        '<sistema xmlns="http://www.sped.fazenda.gov.br/sped/tabelas/metadados" cod="SpedFiscal">'
        '<tabelas dthc="2026-11-16" versao="1964"><pacote cod="SPEDFISCAL_PR" desc="Tabelas do Paraná">'
        '<tabelas><tabela id="999" tipo="INF_ADIC_APUR" desc="5.2 - PR" versao="9" '
        'dtCriacao="2022-01-01" dtVersao="2026-01-01" hash="00" /></tabelas></pacote>'
        '<pacote cod="SPEDFISCAL_SC" desc="Tabelas de Santa Catarina"><tabelas>'
        '<tabela id="54" tipo="AJ_APUR_DED" desc="5.1.1- Tabela de Códigos de Ajustes da Apuração do ICMS" '
        'versao="55" dtCriacao="2008-12-23" dtVersao="2026-10-09" hash="8601A9FA486E417D28067812394CE6B107035540" />'
        '<tabela id="1634" tipo="INF_ADIC_APUR" desc="5.2 - Tabela de informações Adicionais da '
        f'Apuração - Valores Declaratórios" versao="{version}" dtCriacao="2022-12-28" '
        f'dtVersao="2026-10-09" hash="{digest}" />'
        "</tabelas></pacote></tabelas></sistema>"
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<RetornoVersoesTabelasExternas xmlns="http://www.sped.fazenda.gov.br/sped/tabelas/ConsultaVersoes">'
        "<codigoRetorno>101</codigoRetorno>"
        "<urlDownloadArquivo>http://www.sped.fazenda.gov.br/spedtabelas/wsconsulta/obterTabela.ashx</urlDownloadArquivo>"
        f"<metadadosXml>{escape(metadata)}</metadadosXml>"
        "</RetornoVersoesTabelasExternas>"
    ).encode()


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        downloader = MagicMock()
        downloader.__enter__.return_value = downloader
        self.responses = {VERSIONS_URL: _versions()}
        downloader.get.side_effect = self._serve
        self.downloader = downloader
        self.scraper = SefScCBenefScraper(
            settings=Settings(output_dir=self.root, max_retries=1),
            storage=LocalStorage(self.root),
            browser=MagicMock(),
            downloader=downloader,
        )

    def _serve(self, url):
        if url in self.responses:
            return self.responses[url]
        if "obterTabela.ashx" in url:
            return TABLE
        raise AssertionError(url)

    def tearDown(self):
        self._tmp.cleanup()


class TestDiscover(_Base):
    def test_picks_the_sc_inf_adic_apur_table(self):
        [item] = list(self.scraper.discover())

        self.assertEqual(
            item.url,
            "https://www.sped.fazenda.gov.br/spedtabelas/wsconsulta/obterTabela.ashx"
            "?idTabela=1634&versao=31",
        )
        self.assertEqual(item.metadata["published_at"], "2026-10-09")
        self.assertEqual(item.metadata["version"], "31")
        self.assertEqual(self.scraper.subpath_for(item), "2026-10-09_tabela-5.2-cbenef-v31")

    def test_missing_table_is_a_discovery_error(self):
        self.responses[VERSIONS_URL] = _versions().replace(b"SPEDFISCAL_SC", b"SPEDFISCAL_XX")

        with self.assertRaises(DiscoveryError):
            list(self.scraper.discover())

    def test_registered(self):
        self.assertIs(REGISTRY["sef/sc/cbenef"], SefScCBenefScraper)


class TestParse(unittest.TestCase):
    def test_rows_split_benefit_legal_basis_and_vigencia(self):
        rows = parse_table(TABLE)

        self.assertEqual(len(rows), 6)
        self.assertEqual(
            rows[0],
            {
                "code": "SC850001",
                "description": "Crédito Presumido - RICMS/SC-01, Anexo 2, Art. 15, III",
                "benefit": "Crédito Presumido",
                "legal_basis": "RICMS/SC-01, Anexo 2, Art. 15, III",
                "valid_from": "2023-01-01",
                "valid_to": None,
            },
        )
        self.assertEqual(rows[1]["valid_to"], "2023-06-30")

    def test_description_without_a_dash_has_no_benefit(self):
        row = parse_table(TABLE)[4]

        self.assertEqual(row["code"], "SC999999")
        self.assertIsNone(row["benefit"])
        self.assertIsNone(row["legal_basis"])

    def test_a_code_with_two_vigencias_keeps_both(self):
        rows = [r for r in parse_table(TABLE) if r["code"] == "SC830141"]

        self.assertEqual(
            [(r["valid_from"], r["valid_to"]) for r in rows],
            [("2024-10-01", "2026-10-31"), ("2026-11-01", None)],
        )

    def test_unreadable_date_is_kept_as_published(self):
        raw = "h\nSC850001|Crédito Presumido - X|1/1/2023|\n".encode("latin-1")

        self.assertEqual(parse_table(raw)[0]["valid_from"], "1/1/2023")


class TestRun(_Base):
    def test_writes_the_raw_table_and_the_parsed_json(self):
        with patch.object(sef_sc, "MIN_ROWS", 1):
            result = self.scraper.run()

        self.assertEqual(result.persisted, 2)
        folder = self.root / "sef/sc/cbenef/2026-10-09_tabela-5.2-cbenef-v31"
        self.assertEqual((folder / "tabela-5.2.txt").read_bytes(), TABLE)
        payload = json.loads((folder / "tabela-5.2.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["uf"], "SC")
        self.assertEqual(payload["table"]["version"], 31)
        self.assertEqual(len(payload["rows"]), 6)

    def test_same_version_is_skipped(self):
        with patch.object(sef_sc, "MIN_ROWS", 1):
            self.scraper.run()
            result = self.scraper.run()

        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.persisted, 0)

    def test_hash_mismatch_writes_nothing(self):
        self.responses[VERSIONS_URL] = _versions(table=b"other")

        with patch.object(sef_sc, "MIN_ROWS", 1):
            result = self.scraper.run()

        self.assertEqual(result.failed, 1)
        self.assertEqual(list(self.root.glob("sef/sc/cbenef/*/tabela-5.2.*")), [])

    def test_too_few_rows_writes_nothing(self):
        result = self.scraper.run()

        self.assertEqual(result.failed, 1)
        self.assertEqual(list(self.root.glob("sef/sc/cbenef/*/tabela-5.2.*")), [])


if __name__ == "__main__":
    unittest.main()
