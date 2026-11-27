from __future__ import annotations

import json
from pathlib import Path

import typer

from data_source.config import get_settings
from data_source.core.index import rebuild
from data_source.core.logger import configure as configure_logging
from data_source.core.logger import get_logger
from data_source.core.publications import new_publications
from data_source.exceptions import TooFewItemsError, UnknownScraperError
from data_source.scrapers import REGISTRY

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Stackin data-source scraper")
log = get_logger("cli")


@app.command()
def scrape(
    name: str = typer.Argument(..., help="Scraper id (e.g. nfe, nfse)"),
    out: Path | None = typer.Option(None, "--out", help="Output dir"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
    force: bool = typer.Option(
        False, "--force", help="Re-download items even if target folder has files"
    ),
    min_items: int | None = typer.Option(
        None,
        "--min-items",
        min=0,
        help="Fail when discovery finds fewer items than this. "
        "Defaults to the scraper's own floor; 0 disables the check.",
    ),
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

    try:
        result = scraper_cls(settings=settings).run(force=force, min_items=min_items)
    except TooFewItemsError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=3) from exc
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


@app.command("new-publications")
def new_publications_cmd(
    context: str = typer.Argument(..., help="Data folder to read (e.g. nfe, nfse)"),
    out: Path | None = typer.Option(None, "--out", help="Output dir"),
    to: Path = typer.Option(..., "--to", help="JSON file to write the publications to"),
) -> None:
    """Write, as JSON, the NF-e/NFS-e publications the last scrape of CONTEXT persisted."""
    settings = get_settings()
    root = out if out is not None else settings.output_dir
    found = new_publications(root, context)
    to.write_text(json.dumps(found, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"[{context}] new publications: {len(found)}")


@app.command("list")
def list_scrapers() -> None:
    """List registered scrapers."""
    for name in sorted(REGISTRY):
        typer.echo(name)


if __name__ == "__main__":
    app()
