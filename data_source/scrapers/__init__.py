from data_source.core.scraper import BaseScraper
from data_source.scrapers.nfe import NFeScraper
from data_source.scrapers.nfse import NFSeScraper

REGISTRY: dict[str, type[BaseScraper]] = {
    NFeScraper.context: NFeScraper,
    NFSeScraper.context: NFSeScraper,
}

__all__ = ["REGISTRY", "NFeScraper", "NFSeScraper"]
