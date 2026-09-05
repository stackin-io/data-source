from data_source.core.scraper import BaseScraper
from data_source.scrapers.nfe import (
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
    NFSeScraper.context: NFSeScraper,
}

__all__ = [
    "REGISTRY",
    "NFeEsquemasXMLScraper",
    "NFeInformesTecnicosScraper",
    "NFeNotasTecnicasScraper",
    "NFeScraper",
    "NFSeScraper",
]
