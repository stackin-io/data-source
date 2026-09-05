from data_source.core.scraper import BaseScraper
from data_source.scrapers.nfe import (
    NFeDiversosScraper,
    NFeEsquemasXMLScraper,
    NFeInformesTecnicosScraper,
    NFeNotasTecnicasScraper,
    NFeScraper,
)
from data_source.scrapers.nfse import NFSeScraper

REGISTRY: dict[str, type[BaseScraper]] = {
    NFeEsquemasXMLScraper.context: NFeEsquemasXMLScraper,
    NFeNotasTecnicasScraper.context: NFeNotasTecnicasScraper,
    NFeInformesTecnicosScraper.context: NFeInformesTecnicosScraper,
    NFeDiversosScraper.context: NFeDiversosScraper,
    NFSeScraper.context: NFSeScraper,
}

__all__ = [
    "REGISTRY",
    "NFeDiversosScraper",
    "NFeEsquemasXMLScraper",
    "NFeInformesTecnicosScraper",
    "NFeNotasTecnicasScraper",
    "NFeScraper",
    "NFSeScraper",
]
