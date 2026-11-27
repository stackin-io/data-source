import json
import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from data_source import cli
from data_source.core.publications import environment_of, kind_of, new_publications


def _item(slug, title, status, published_at="2026-11-24"):
    return {
        "slug": slug,
        "title": title,
        "published_at": published_at,
        "source_url": f"https://example.gov.br/{slug}.zip",
        "folder_url": f"https://github.com/stackin-io/data-source/tree/master/data/x/{slug}",
        "status": status,
    }


def _write(root: Path, context: str, items: list[dict]) -> None:
    folder = root / context
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(
        json.dumps({"context": context, "items": items}), encoding="utf-8"
    )


class NewPublicationsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_picks_only_items_persisted_by_the_run(self):
        _write(
            self.root,
            "nfse",
            [
                _item(
                    "2026-11-24_prodrest-esquemas-xsd-producao-restrita-20261124",
                    "Esquemas XSD Produção Restrita 20261124",
                    "ok",
                ),
                _item(
                    "2026-10-20_prodrest-nfse-esquemasxsd-prodrest-v1.01-20261020",
                    "NFSe-ESQUEMAS_XSD-PRODREST-v1.01",
                    "skipped",
                ),
                _item(
                    "2026-07-14_rtc-nota-tecnica-secgnfs-e-no-008", "Nota Técnica nº 008", "failed"
                ),
            ],
        )
        found = new_publications(self.root, "nfse")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["kind"], "Esquema XSD")
        self.assertEqual(found[0]["environment"], "produção restrita")
        self.assertEqual(found[0]["published_at"], "2026-11-24")
        self.assertTrue(found[0]["folder_url"].endswith("producao-restrita-20261124"))

    def test_reads_every_nfe_subcontext_and_skips_diversos(self):
        _write(
            self.root, "nfe/notas-tecnicas", [_item("nt-2026-009", "Nota Técnica 2026.009", "ok")]
        )
        _write(
            self.root, "nfe/esquemas-xml", [_item("pl-010i", "Pacote de Liberação 010i", "partial")]
        )
        _write(self.root, "nfe/diversos", [_item("tabela", "Tabela cClassTrib", "ok")])
        found = new_publications(self.root, "nfe")
        self.assertEqual(
            sorted((p["context"], p["kind"]) for p in found),
            [("nfe/esquemas-xml", "Esquema XSD"), ("nfe/notas-tecnicas", "Nota técnica")],
        )

    def test_nothing_new_and_missing_context(self):
        _write(self.root, "nfse", [_item("a", "Anexo I", "skipped")])
        self.assertEqual(new_publications(self.root, "nfse"), [])
        self.assertEqual(new_publications(self.root, "svrs"), [])

    def test_kind_and_environment_from_names(self):
        self.assertEqual(kind_of("nfse", "ANEXO_I-SEFIN_ADN-DPS_NFSe-SNNFSe-v1.01"), "Anexo")
        self.assertEqual(kind_of("nfse", "Guia do Emissor Público Nacional Web"), "Manual")
        self.assertEqual(
            kind_of("nfse", "Esquemas XSD - AnexoVI-LeiautesRN_RTC_IBSCBS-V1.01.03"), "Esquema XSD"
        )
        self.assertIsNone(kind_of("svrs/nfe/documentos", "Nota Técnica"))
        self.assertEqual(environment_of("x", "Anexo B Produção Restrita"), "produção restrita")
        self.assertEqual(environment_of("x", "Manual Produção"), "produção")
        self.assertIsNone(
            environment_of("2026-02-09_nfse-esquemasxsd-v1.01", "NFSe-ESQUEMAS_XSD-v1.01")
        )

    def test_cli_writes_the_list(self):
        _write(self.root, "nfse", [_item("b", "Nota Técnica SE/CGNFS-e nº 010", "ok")])
        target = self.root / "new.json"
        result = CliRunner().invoke(
            cli.app, ["new-publications", "nfse", "--out", str(self.root), "--to", str(target)]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("new publications: 1", result.output)
        self.assertEqual(json.loads(target.read_text())[0]["kind"], "Nota técnica")


if __name__ == "__main__":
    unittest.main()
