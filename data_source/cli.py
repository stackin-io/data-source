from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from data_source.config import get_settings
from data_source.core.logger import configure as configure_logging
from data_source.core.logger import get_logger
from data_source.exceptions import UnknownScraperError
from data_source.scrapers import REGISTRY

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Stackin data-source scraper")
log = get_logger("cli")


@app.command()
def scrape(
    name: Annotated[str, typer.Argument(help="Scraper id (e.g. nfe, nfse)")],
    out: Annotated[Path | None, typer.Option("--out", help="Output dir")] = None,
    headless: Annotated[bool, typer.Option("--headless/--headed")] = True,
) -> None:
    """Run a registered scraper end-to-end."""
    settings = get_settings()
    if out is not None:
        settings = settings.model_copy(update={"output_dir": out})
    settings = settings.model_copy(update={"headless": headless})
    configure_logging(settings.log_level)

    scraper_cls = REGISTRY.get(name)
    if scraper_cls is None:
        raise UnknownScraperError(f"unknown scraper: {name!r}. available: {sorted(REGISTRY)}")

    result = scraper_cls(settings=settings).run()
    typer.echo(
        f"[{result.context}] discovered={result.discovered} "
        f"persisted={result.persisted} failed={result.failed}"
    )
    if result.failed and not result.persisted:
        raise typer.Exit(code=2)


@app.command("list")
def list_scrapers() -> None:
    """List registered scrapers."""
    for name in sorted(REGISTRY):
        typer.echo(name)


if __name__ == "__main__":
    app()
