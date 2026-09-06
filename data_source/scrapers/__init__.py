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
from data_source.scrapers.svrs import (
    SVRSBPeDocumentosScraper,
    SVRSCTeDocumentosScraper,
    SVRSMDFeDocumentosScraper,
    SVRSNFCeDocumentosScraper,
    SVRSNFeDocumentosScraper,
)

REGISTRY: dict[str, type[BaseScraper]] = {
    NFeEsquemasXMLScraper.context: NFeEsquemasXMLScraper,
    NFeNotasTecnicasScraper.context: NFeNotasTecnicasScraper,
    NFeInformesTecnicosScraper.context: NFeInformesTecnicosScraper,
    NFeDiversosScraper.context: NFeDiversosScraper,
    NFeManuaisScraper.context: NFeManuaisScraper,
    NFSeScraper.context: NFSeScraper,
    SVRSNFeDocumentosScraper.context: SVRSNFeDocumentosScraper,
    SVRSNFCeDocumentosScraper.context: SVRSNFCeDocumentosScraper,
    SVRSCTeDocumentosScraper.context: SVRSCTeDocumentosScraper,
    SVRSMDFeDocumentosScraper.context: SVRSMDFeDocumentosScraper,
    SVRSBPeDocumentosScraper.context: SVRSBPeDocumentosScraper,
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
    "SVRSBPeDocumentosScraper",
    "SVRSCTeDocumentosScraper",
    "SVRSMDFeDocumentosScraper",
    "SVRSNFCeDocumentosScraper",
    "SVRSNFeDocumentosScraper",
]
