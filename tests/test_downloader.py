import unittest

from data_source.core.downloader import Downloader


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

    def test_infers_extension_from_url_suffix(self):
        self.assertTrue(
            Downloader.suggest_filename("https://x/report?p=1&f=.pdf").endswith(".pdf")
        )

    def test_deterministic_for_same_url(self):
        self.assertEqual(
            Downloader.suggest_filename("https://x/y"),
            Downloader.suggest_filename("https://x/y"),
        )


if __name__ == "__main__":
    unittest.main()
