import unittest

from data_source.core.downloader import Downloader, slugify


class TestSuggestFilename(unittest.TestCase):

    def test_uses_original_name_when_url_has_filename(self):
        self.assertEqual(
            Downloader.suggest_filename("https://x/schemas/leiauteNFe_v4.00.xsd"),
            "leiauteNFe_v4.00.xsd",
        )

    def test_falls_back_to_hash_when_no_filename(self):
        name = Downloader.suggest_filename("https://x/download?id=42")

        self.assertTrue(name.endswith(".bin"))
        self.assertEqual(len(name), 20)  # 16 hex + ".bin"

    def test_deterministic_for_same_url(self):
        self.assertEqual(
            Downloader.suggest_filename("https://x/y"),
            Downloader.suggest_filename("https://x/y"),
        )


class TestSlugify(unittest.TestCase):

    def test_replaces_spaces_with_dashes_and_lowercases(self):
        self.assertEqual(
            slugify("Esquemas XML NF-e - Pacote de Liberação"),
            "esquemas-xml-nf-e-pacote-de-liberacao",
        )

    def test_drops_symbols_and_collapses_dashes(self):
        self.assertEqual(
            slugify("Schemas XML NF-e -010e_v.1.02 - NT 2025.002 v.1.40"),
            "schemas-xml-nf-e-010ev.1.02-nt-2025.002-v.1.40",
        )

    def test_returns_fallback_for_empty_input(self):
        self.assertEqual(slugify(""), "file")
        self.assertEqual(slugify("   ---   "), "file")

    def test_strips_accented_and_punctuation(self):
        self.assertEqual(slugify("Liberação (ZIP)"), "liberacao-zip")

    def test_truncates_to_max_len(self):
        self.assertLessEqual(len(slugify("a " * 200, max_len=32)), 32)


if __name__ == "__main__":
    unittest.main()
