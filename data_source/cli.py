from __future__ import annotations

from pathlib import Path

import typer

from data_source.config import get_settings
from data_source.core.index import rebuild
from data_source.core.logger import configure as configure_logging
from data_source.core.logger import get_logger
from data_source.exceptions import UnknownScraperError
from data_source.scrapers import REGISTRY

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Stackin data-source scraper")
log = get_logger("cli")


@app.command()
def scrape(
    name: str = typer.Argument(..., help="Scraper id (e.g. nfe, nfse)"),
    out: Path | None = typer.Option(None, "--out", help="Output dir"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
    force: bool = typer.Option(False, "--force", help="Re-download items even if target folder has files"),
) -> None:
    """Run a registered scraper end-to-end. Skips items whose folder already has files (use --force to override)."""
    settings = get_settings()
    if out is not None:
        settings = settings.model_copy(update={"output_dir": out})
    settings = settings.model_copy(update={"headless": headless})
    configure_logging(settings.log_level)

    scraper_cls = REGISTRY.get(name)
    if scraper_cls is None:
        raise UnknownScraperError(f"unknown scraper: {name!r}. available: {sorted(REGISTRY)}")

    result = scraper_cls(settings=settings).run(force=force)
    typer.echo(
        f"[{result.context}] discovered={result.discovered} "
        f"persisted={result.persisted} skipped={result.skipped} failed={result.failed}"
    )
    if result.failed and not result.persisted:
        raise typer.Exit(code=2)


@app.command("rebuild-index")
def rebuild_index(
    out: Path | None = typer.Option(None, "--out", help="Output dir"),
) -> None:
    """Regenerate every feed and the root sitemap from the manifests on disk.

    Scrapes nothing. A parallel run needs this: each job only sees its own
    context, so the root sitemap has to be aggregated afterwards.
    """
    settings = get_settings()
    if out is not None:
        settings = settings.model_copy(update={"output_dir": out})
    configure_logging(settings.log_level)

    contexts = rebuild(settings)
    typer.echo(f"rebuilt {len(contexts)} contexts: {', '.join(contexts)}")


@app.command("list")
def list_scrapers() -> None:
    """List registered scrapers."""
    for name in sorted(REGISTRY):
        typer.echo(name)


if __name__ == "__main__":
    app()
