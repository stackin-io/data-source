# data-source

Scheduled Selenium scraping jobs that collect official Brazilian fiscal documentation and XML schemas (NFe / NFSe) into a versioned data lake, and are designed to extend to any other paginated/authenticated source without rewriting the core.

Runs entirely as GitHub Actions workflows — no server, no cron on a machine. Each job is a `Scraper` subclass invoked via CLI.

## Architecture

```
data_source/
├── core/               # framework — no source-specific logic here
│   ├── scraper.py      # abstract BaseScraper (Template Method + Strategy)
│   ├── browser.py      # Selenium factory (headless Chrome, retries, timeouts)
│   ├── storage.py      # Storage protocol + LocalStorage impl (S3 slot open)
│   ├── downloader.py   # streams files w/ tenacity retry
│   └── logger.py       # structlog JSON logs (CI-friendly)
├── scrapers/
│   ├── nfe.py          # NFe scraper — portal, MOC, XSDs
│   └── nfse.py         # NFSe scraper — ADN, XSDs, manuais
├── cli.py              # typer app: `data-source scrape nfe`, `... nfse`
├── config.py           # pydantic-settings, env-driven
├── exceptions.py
└── __main__.py

.github/workflows/
├── scrape-nfe.yml      # cron weekly + workflow_dispatch
└── scrape-nfse.yml
```

## Design principles

- **BaseScraper is a Template Method** — subclasses override `discover()` (find the pages/links) and `extract(item)` (turn a page into files); base handles browser lifecycle, retry, storage, logging.
- **Storage is a Protocol** — `LocalStorage` today, `S3Storage` tomorrow, no scraper change.
- **Everything retries** with exponential backoff (`tenacity`), max 3 by default, configurable per scraper.
- **Selenium is contained** — only `core/browser.py` touches `webdriver`. Scrapers work against a thin `Browser` wrapper. Swappable to Playwright without changing scrapers.
- **Idempotent output** — writes go to `data/<context>/<yyyy-mm-dd>/...`, filename derived from URL hash. Re-runs overwrite same file.
- **CI-first** — logs JSON, exit codes signal partial success, artifacts uploaded from `data/`.

## Usage

Local dev:

```bash
poetry install
poetry run data-source scrape nfe --out ./data
poetry run data-source scrape nfse --out ./data
poetry run data-source list                   # available scrapers
```

CI: workflows in `.github/workflows/` run each scraper on schedule (weekly Mon 05:00 UTC), commit results to a data branch (or upload as artifact — decide before first prod run).

## Adding a new source

1. Create `data_source/scrapers/<name>.py` with a `class <Name>Scraper(BaseScraper)`.
2. Implement `discover(self) -> Iterable[ScrapeItem]` and `extract(self, item: ScrapeItem) -> Iterable[Artifact]`.
3. Register it in `data_source/scrapers/__init__.py` (`REGISTRY`).
4. Add a workflow file `.github/workflows/scrape-<name>.yml` (copy from existing).

No changes to `core/` should be needed. If they are, promote the pattern back to `core/` instead of duplicating.

## Environment

| Var | Default | Purpose |
|---|---|---|
| `DATA_SOURCE_OUTPUT_DIR` | `./data` | Root output dir |
| `DATA_SOURCE_HEADLESS` | `true` | Run Chrome headless (must be `true` in CI) |
| `DATA_SOURCE_TIMEOUT_S` | `30` | Per-page timeout |
| `DATA_SOURCE_MAX_RETRIES` | `3` | Retry budget per operation |
| `DATA_SOURCE_LOG_LEVEL` | `INFO` | `DEBUG`/`INFO`/`WARNING`/`ERROR` |
