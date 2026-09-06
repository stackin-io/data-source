from data_source.core.scraper import BaseScraper
from data_source.scrapers.nfe import (
    NFeDiversosScraper,
    NFeEsquemasXMLScraper,
    NFeInformesTecnicosScraper,
    NFeManuaisScraper,
    NFeNotasTecnicasScraper,
    NFeScraper,
)
from data_source.scrapers.nfse import NFSeScraper

REGISTRY: dict[str, type[BaseScraper]] = {
    NFeEsquemasXMLScraper.context: NFeEsquemasXMLScraper,
    NFeNotasTecnicasScraper.context: NFeNotasTecnicasScraper,
    NFeInformesTecnicosScraper.context: NFeInformesTecnicosScraper,
    NFeDiversosScraper.context: NFeDiversosScraper,
    NFeManuaisScraper.context: NFeManuaisScraper,
    NFSeScraper.context: NFSeScraper,
}

__all__ = [
    "REGISTRY",
    "NFeDiversosScraper",
    "NFeEsquemasXMLScraper",
    "NFeInformesTecnicosScraper",
    "NFeManuaisScraper",
    "NFeNotasTecnicasScraper",
    "NFeScraper",
    "NFSeScraper",
]
