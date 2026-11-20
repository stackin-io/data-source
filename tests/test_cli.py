import runpy
import sys
import unittest
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

from typer.testing import CliRunner

from data_source import cli
from data_source.core.scraper import ScrapeResult
from data_source.exceptions import UnknownScraperError


class _FakeScraper:
    """Stands in for a registered scraper: records how the CLI built and ran it."""

    result = ScrapeResult(context="fake", discovered=2, persisted=2)
    instances: ClassVar[list["_FakeScraper"]] = []

    def __init__(self, *, settings):
        self.settings = settings
        self.force = None
        _FakeScraper.instances.append(self)

    def run(self, *, force):
        self.force = force
        return self.result


class _CliTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        _FakeScraper.instances = []
        _FakeScraper.result = ScrapeResult(context="fake", discovered=2, persisted=2)
        registry = patch.dict(cli.REGISTRY, {"fake": _FakeScraper}, clear=True)
        registry.start()
        self.addCleanup(registry.stop)

    def invoke(self, *args):
        return self.runner.invoke(cli.app, list(args))


class TestList(_CliTest):
    def test_prints_registered_scrapers_sorted(self):
        with patch.dict(cli.REGISTRY, {"another": _FakeScraper}):
            result = self.invoke("list")

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.split(), ["another", "fake"])


class TestScrape(_CliTest):
    def test_runs_the_scraper_and_prints_the_counts(self):
        result = self.invoke("scrape", "fake")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("[fake] discovered=2 persisted=2 skipped=0 failed=0", result.output)
        (scraper,) = _FakeScraper.instances
        self.assertFalse(scraper.force)
        self.assertTrue(scraper.settings.headless)

    def test_passes_out_headless_and_force_through(self):
        result = self.invoke(
            "scrape", "fake", "--out", "/tmp/elsewhere", "--no-headless", "--force"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        (scraper,) = _FakeScraper.instances
        self.assertEqual(scraper.settings.output_dir, Path("/tmp/elsewhere"))
        self.assertFalse(scraper.settings.headless)
        self.assertTrue(scraper.force)

    def test_unknown_scraper_raises(self):
        result = self.invoke("scrape", "nope")

        self.assertIsInstance(result.exception, UnknownScraperError)
        self.assertIn("available: ['fake']", str(result.exception))

    def test_exits_2_when_everything_failed(self):
        _FakeScraper.result = ScrapeResult(context="fake", discovered=3, failed=3)

        result = self.invoke("scrape", "fake")

        self.assertEqual(result.exit_code, 2)

    def test_partial_failure_still_exits_0(self):
        _FakeScraper.result = ScrapeResult(context="fake", discovered=3, persisted=1, failed=2)

        result = self.invoke("scrape", "fake")

        self.assertEqual(result.exit_code, 0)

    def test_requires_a_name(self):
        result = self.invoke("scrape")

        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(_FakeScraper.instances, [])


class TestRebuildIndex(_CliTest):
    def test_rebuilds_and_reports_the_contexts(self):
        with patch.object(cli, "rebuild", return_value=["nfe/manuais", "nfse"]) as rebuild:
            result = self.invoke("rebuild-index", "--out", "/tmp/out")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("rebuilt 2 contexts: nfe/manuais, nfse", result.output)
        self.assertEqual(rebuild.call_args.args[0].output_dir, Path("/tmp/out"))

    def test_uses_the_configured_output_dir_by_default(self):
        with patch.object(cli, "rebuild", return_value=[]) as rebuild:
            result = self.invoke("rebuild-index")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(rebuild.call_args.args[0].output_dir, cli.get_settings().output_dir)


class TestNoArgs(_CliTest):
    def test_shows_help(self):
        result = self.invoke()

        self.assertIn("scrape", result.output)
        self.assertIn("rebuild-index", result.output)


class TestModuleEntryPoint(unittest.TestCase):
    def test_python_dash_m_runs_the_app(self):
        with (
            patch.object(sys, "argv", ["data-source", "list"]),
            patch.dict(cli.REGISTRY, {"only": _FakeScraper}, clear=True),
            patch("typer.echo") as echo,
            self.assertRaises(SystemExit) as ctx,
        ):
            runpy.run_module("data_source", run_name="__main__")

        self.assertEqual(ctx.exception.code, 0)
        echo.assert_called_once_with("only")


if __name__ == "__main__":
    unittest.main()
