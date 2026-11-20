class DataSourceError(Exception):
    """Base exception for the data-source framework."""


class ScraperError(DataSourceError):
    """Raised when a scraper fails to complete a run."""


class DiscoveryError(ScraperError):
    """Raised while discovering pages/items to scrape."""


class TooFewItemsError(ScraperError):
    """Raised when discovery finds fewer items than the scraper's sane minimum.

    A portal that changed its markup, or a WAF answering with a block page,
    yields zero links rather than an error. Without this the run is green.
    """

    def __init__(self, context: str, found: int, minimum: int) -> None:
        self.context = context
        self.found = found
        self.minimum = minimum
        super().__init__(
            f"[{context}] discovered {found} item(s), expected at least {minimum}. "
            "The source likely changed or blocked the request; "
            "the previous manifest was left untouched."
        )


class ExtractionError(ScraperError):
    """Raised while extracting artifacts from a discovered item."""


class BrowserError(DataSourceError):
    """Raised for Selenium/browser-level failures."""


class DownloadError(DataSourceError):
    """Raised when a file download fails after retries."""


class StorageError(DataSourceError):
    """Raised when persisting an artifact fails."""


class UnknownScraperError(DataSourceError):
    """Raised when a scraper name is not registered."""
