import unittest
from unittest.mock import patch

import httpx

from data_source.core.downloader import Downloader, _parse_content_disposition, slugify
from data_source.exceptions import DownloadError


def _downloader(handler, *, max_retries=3):
    """A Downloader whose HTTP client answers from `handler` instead of the network."""
    d = Downloader(max_retries=max_retries, throttle_ms=0)
    d._client.close()
    d._client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    return d


class _Calls:
    """Answers each request with the next response in turn and counts the calls."""

    def __init__(self, *responses):
        self._responses = list(responses)
        self.count = 0

    def __call__(self, _request):
        self.count += 1
        answer = self._responses.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


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


@patch("time.sleep")  # tenacity's backoff and the throttle both sleep through time.sleep
class TestFetchRetries(unittest.TestCase):
    def test_returns_body_and_content_type_on_success(self, _sleep):
        calls = _Calls(
            httpx.Response(200, content=b"%PDF-1.7", headers={"content-type": "application/pdf"})
        )

        with _downloader(calls) as d:
            got = d.fetch("https://x/docs/nt-2025.pdf")

        self.assertEqual(got.data, b"%PDF-1.7")
        self.assertEqual(got.content_type, "application/pdf")
        self.assertEqual(got.filename, "nt-2025.pdf")
        self.assertEqual(calls.count, 1)
        self.assertEqual(got.last_modified, "")

    def test_keeps_the_last_modified_header(self, _sleep):
        stamp = "Fri, 06 Mar 2026 20:58:44 GMT"
        calls = _Calls(httpx.Response(200, content=b"%PDF", headers={"last-modified": stamp}))

        with _downloader(calls) as d:
            got = d.fetch("https://x/Anexo_XI.pdf")

        self.assertEqual(got.last_modified, stamp)

    def test_retries_a_server_error_then_succeeds(self, sleep):
        calls = _Calls(httpx.Response(503), httpx.Response(502), httpx.Response(200, content=b"ok"))

        with _downloader(calls) as d:
            got = d.fetch("https://x/a.zip")

        self.assertEqual(got.data, b"ok")
        self.assertEqual(calls.count, 3)
        self.assertGreaterEqual(sleep.call_count, 2)  # backed off between attempts

    def test_retries_a_dropped_connection(self, _sleep):
        calls = _Calls(httpx.ConnectError("reset"), httpx.Response(200, content=b"ok"))

        with _downloader(calls) as d:
            self.assertEqual(d.get("https://x/a.zip"), b"ok")
        self.assertEqual(calls.count, 2)

    def test_retries_a_body_cut_short(self, _sleep):
        """A partial download surfaces as a protocol error and is fetched again in full."""
        calls = _Calls(
            httpx.RemoteProtocolError(
                "peer closed connection without sending complete message body"
            ),
            httpx.Response(200, content=b"complete"),
        )

        with _downloader(calls) as d:
            self.assertEqual(d.get("https://x/a.zip"), b"complete")
        self.assertEqual(calls.count, 2)

    def test_retries_a_timeout(self, _sleep):
        calls = _Calls(httpx.ReadTimeout("slow"), httpx.Response(200, content=b"ok"))

        with _downloader(calls) as d:
            self.assertEqual(d.get("https://x/a.zip"), b"ok")

    def test_gives_up_after_max_retries_with_download_error(self, _sleep):
        calls = _Calls(*[httpx.Response(500)] * 5)

        with _downloader(calls, max_retries=3) as d, self.assertRaises(DownloadError) as ctx:
            d.fetch("https://x/a.zip")

        self.assertEqual(calls.count, 3)
        self.assertIn("https://x/a.zip", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, httpx.HTTPStatusError)

    def test_a_missing_file_is_a_download_error(self, _sleep):
        calls = _Calls(*[httpx.Response(404)] * 3)

        with _downloader(calls) as d, self.assertRaises(DownloadError):
            d.fetch("https://x/gone.pdf")

    def test_transport_failure_on_every_attempt_is_a_download_error(self, _sleep):
        calls = _Calls(*[httpx.ConnectError("down")] * 2)

        with _downloader(calls, max_retries=2) as d, self.assertRaises(DownloadError) as ctx:
            d.fetch("https://x/a.zip")

        self.assertIsInstance(ctx.exception.__cause__, httpx.ConnectError)

    def test_follows_redirects(self, _sleep):
        def handler(request):
            if request.url.path == "/old":
                return httpx.Response(302, headers={"location": "https://x/new.xml"})
            return httpx.Response(200, content=b"<x/>", headers={"content-type": "text/xml"})

        with _downloader(handler) as d:
            got = d.fetch("https://x/old")

        self.assertEqual(got.data, b"<x/>")


class TestThrottle(unittest.TestCase):
    def test_waits_out_the_courtesy_gap_between_requests(self):
        d = Downloader(throttle_ms=500)
        d._last_request_at = 100.0
        with patch("time.monotonic", return_value=100.2), patch("time.sleep") as sleep:
            d._throttle()
        d._client.close()

        self.assertAlmostEqual(sleep.call_args.args[0], 0.3)

    def test_does_not_wait_once_the_gap_has_passed(self):
        d = Downloader(throttle_ms=500)
        d._last_request_at = 100.0
        with patch("time.monotonic", return_value=101.0), patch("time.sleep") as sleep:
            d._throttle()
        d._client.close()

        sleep.assert_not_called()


@patch("time.sleep")
class TestResolveFilename(unittest.TestCase):
    def _fetch(self, url, headers=None, title_hint=None):
        calls = _Calls(httpx.Response(200, content=b"x", headers=headers or {}))
        with _downloader(calls) as d:
            return d.fetch(url, title_hint=title_hint)

    def test_content_disposition_wins(self, _sleep):
        got = self._fetch(
            "https://x/download.aspx?id=1",
            {"content-disposition": 'attachment; filename="NT_2025.001.pdf"'},
        )
        self.assertEqual(got.filename, "NT_2025.001.pdf")

    def test_rfc5987_filename_is_decoded(self, _sleep):
        got = self._fetch(
            "https://x/download.aspx?id=1",
            {"content-disposition": "attachment; filename*=UTF-8''Libera%C3%A7%C3%A3o.zip"},
        )
        self.assertEqual(got.filename, "Liberação.zip")

    def test_title_hint_with_known_content_type(self, _sleep):
        got = self._fetch(
            "https://x/arquivo?conteudo=abc",
            {"content-type": "application/zip; charset=binary"},
            title_hint="Pacote de Liberação nº 9",
        )
        self.assertEqual(got.filename, "pacote-de-liberacao-no-9.zip")  # NFKD: "º" -> "o"
        self.assertEqual(got.content_type, "application/zip")

    def test_title_hint_with_unknown_content_type_is_bin(self, _sleep):
        got = self._fetch(
            "https://x/arquivo?conteudo=abc",
            {"content-type": "application/x-unknown"},
            title_hint="Manual",
        )
        self.assertEqual(got.filename, "manual.bin")

    def test_no_hint_falls_back_to_url_hash_with_type_extension(self, _sleep):
        got = self._fetch("https://x/download?id=42", {"content-type": "application/pdf"})
        self.assertRegex(got.filename, r"^[0-9a-f]{16}\.pdf$")

    def test_missing_content_type_is_octet_stream(self, _sleep):
        got = self._fetch("https://x/download?id=42")
        self.assertEqual(got.content_type, "application/octet-stream")
        self.assertTrue(got.filename.endswith(".bin"))


class TestParseContentDisposition(unittest.TestCase):
    def test_empty_header(self):
        self.assertIsNone(_parse_content_disposition(""))

    def test_header_without_filename(self):
        self.assertIsNone(_parse_content_disposition("inline"))

    def test_unquoted_filename(self):
        self.assertEqual(_parse_content_disposition("attachment; filename=a.xsd"), "a.xsd")


if __name__ == "__main__":
    unittest.main()
