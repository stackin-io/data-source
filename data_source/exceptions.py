class DataSourceError(Exception):
    """Base exception for the data-source framework."""


class ScraperError(DataSourceError):
    """Raised when a scraper fails to complete a run."""


class DiscoveryError(ScraperError):
    """Raised while discovering pages/items to scrape."""


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
