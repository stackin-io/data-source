#!/usr/bin/env python3
"""Valida estrutura do evento NF-e ABI, correspondencia codigo/tag e detalhe.
Uso: python validar_eventos.py caminho/evento.xml
Depende de: pip install lxml
Nao substitui a verificacao de assinatura XMLDSig ou regras de negocio.
"""
from pathlib import Path
import argparse
import sys
from lxml import etree

BASE = Path(__file__).resolve().parent
NS = "http://www.portalfiscal.inf.br/nfeabi"
MAPPING = {
    "110111": ("evCancNFeABI", "evCancNFeABI_v1.00.xsd"),
    "112310": ("evPagParcelaNFeABI", "evPagParcelaNFeABI_v1.00.xsd"),
    "112320": ("evDesfazimAlienac", "evDesfazimAlienacNFeABI_v1.00.xsd"),
    "211310": ("evApropCredIndNFeABI", "evApropCredIndNFeABI_v1.00.xsd"),
}

def check_event(file_path):
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    tree = etree.parse(str(file_path), parser)
    envelope_xsd = etree.XMLSchema(etree.parse(str(BASE / "eventoNFeABI_v1.00.xsd")))
    if not envelope_xsd.validate(tree):
        raise ValueError("Envelope de evento invalido: " + str(envelope_xsd.error_log.last_error))
    root = tree.getroot()
    if root.tag != f"{{{NS}}}evento":
        raise ValueError("Elemento raiz nao e evento")
    inf = root.find(f"{{{NS}}}infEvento")
    tp = inf.findtext(f"{{{NS}}}tpEvento")
    if tp not in MAPPING:
        raise ValueError("tpEvento nao reconhecido: " + str(tp))
    expected_tag, xsd_file = MAPPING[tp]
    detail_container = inf.find(f"{{{NS}}}detEvento")
    children = list(detail_container)
    if len(children) != 1:
        raise ValueError("detEvento deve conter exatamente um elemento especifico")
    detail = children[0]
    if detail.tag != f"{{{NS}}}{expected_tag}":
        raise ValueError(f"tpEvento={tp} exige elemento {expected_tag}, recebido {etree.QName(detail).localname}")
    declared_ver = inf.findtext(f"{{{NS}}}verEvento")
    detail_ver = detail_container.get("versaoEvento")
    local_ver = detail.get("versao")
    if declared_ver != detail_ver or declared_ver != local_ver:
        raise ValueError("Versoes de evento divergentes (verEvento/versaoEvento/versao)")
    detail_xsd = etree.XMLSchema(etree.parse(str(BASE / xsd_file)))
    if not detail_xsd.validate(etree.ElementTree(detail)):
        raise ValueError("Detalhe invalido: " + str(detail_xsd.error_log.last_error))
    return f"OK: {tp} / {expected_tag} / envelope e detalhe validos"

if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("arquivo", type=Path)
    args = cli.parse_args()
    try:
        print(check_event(args.arquivo))
    except (ValueError, etree.XMLSyntaxError, OSError) as exc:
        print("ERRO: " + str(exc), file=sys.stderr)
        sys.exit(1)
