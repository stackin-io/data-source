<div align="center">

<img src="https://raw.githubusercontent.com/stackin-io/stackin-python-sdk/master/docs/assets/stackin.png" width="120" />

**A base fiscal brasileira, sempre atualizada — sem clicar em nada.**

[![Scrape NF-e](https://github.com/stackin-io/data-source/actions/workflows/scrape-nfe.yml/badge.svg)](https://github.com/stackin-io/data-source/actions/workflows/scrape-nfe.yml)
[![Scrape NFS-e](https://github.com/stackin-io/data-source/actions/workflows/scrape-nfse.yml/badge.svg)](https://github.com/stackin-io/data-source/actions/workflows/scrape-nfse.yml)
[![Scrape SVRS](https://github.com/stackin-io/data-source/actions/workflows/scrape-svrs.yml/badge.svg)](https://github.com/stackin-io/data-source/actions/workflows/scrape-svrs.yml)

[![Feed](https://img.shields.io/badge/feed-atom-orange?style=flat-square)](https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml)
[![Manifest](https://img.shields.io/badge/manifest-json-blue?style=flat-square)](https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json)
[![Updates](https://img.shields.io/badge/updates-diário%2009%3A00%20UTC-success?style=flat-square)](.github/workflows)
[![License](https://img.shields.io/badge/license-AGPL--3.0-informational?style=flat-square)](LICENSE)

[Assinar newsletter](https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml) · [Manifest JSON](https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json) · [app.stackin.io](https://app.stackin.io)

</div>

---

# data-source

Publicações oficiais da **NF-e** (portal SEFAZ), **NFS-e** (ADN nacional gov.br) e SVRS (22 UFs) sempre atualizadas e organizadas. Nunca mais entra num portal fiscal pra ver se saiu XSD novo, MOC novo, Nota Técnica nova, anexo novo. A gente monitora, baixa, versiona e avisa.

**Sumário:** [Quickstart](#quickstart) · [Como funciona](#como-funciona) · [Assinar](#como-se-inscrever) · [Formato](#o-que-você-recebe) · [Fontes](#fontes-cobertas) · [Por que existe](#por-que-existe) · [Licença](#licença)

## Quickstart

Última publicação em qualquer fonte, via `curl` + `jq`:

```bash
curl -s https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json \
  | jq '.entries[0] | {title, published_at, section, source_url}'
```

Consumir e detectar mudança:

```python
import httpx

MANIFEST = "https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json"

data = httpx.get(MANIFEST).json()
print(data["generated_at"], "→", len(data["entries"]), "docs")
```

## Como funciona

**Uma vez por dia, às 09:00 UTC**, um robô varre os portais oficiais, identifica o que é novidade em relação à última passagem, baixa os arquivos, descompacta os ZIPs, e organiza tudo por data de publicação. Cada documento fica numa pasta própria com título completo, data e todos os arquivos que compõem o pacote.

Duas coisas são publicadas todo ciclo:

- Um **feed Atom (XML)** — a lista das últimas publicações, no mesmo formato usado por blogs e sites de notícia. Leitores de RSS entendem, serviços de e-mail marketing entendem, integrações via webhook entendem.
- Um **manifest JSON** — um catálogo estruturado com título, descrição, data de publicação, seção (Guia / Manual / XSD / Anexo etc), link do arquivo original no portal e link direto pro arquivo já espelhado aqui.

Nada muda quando não há novidade: o feed e o manifest continuam válidos, só sem entrada nova. Quando muda, aparece em ambos no mesmo minuto.

### Exemplo de entrada no `manifest.json`

```json
{
  "generated_at": "2026-09-07T09:12:44Z",
  "entries": [
    {
      "title": "Nota Técnica 2024.001 v1.20",
      "description": "Nota Técnica 2024.001",
      "published_at": "2026-09-05",
      "section": "Nota Técnica",
      "source_url": "https://www.nfe.fazenda.gov.br/portal/...",
      "mirror_url": "https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/notas-tecnicas/2026-09-05-nt-2024-001/NT2024_001_v1.20.pdf",
      "files": ["NT2024_001_v1.20.pdf"]
    }
  ]
}
```

## Como se inscrever

### Newsletter (feed Atom)

Cola a URL do feed em qualquer leitor de RSS/Atom — Feedly, Inoreader, NetNewsWire, Slack, Discord, Notion. Novidade nova = notificação nova.

- **Todas as fontes:** `https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml`

<details>
<summary><b>Feeds por fonte</b> (22 URLs)</summary>

Base: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/`

| Fonte | Path |
|---|---|
| NF-e — Esquemas XML | `nfe/esquemas-xml/feed.xml` |
| NF-e — Notas Técnicas | `nfe/notas-tecnicas/feed.xml` |
| NF-e — Informes Técnicos | `nfe/informes-tecnicos/feed.xml` |
| NF-e — Diversos | `nfe/diversos/feed.xml` |
| NF-e — Manuais | `nfe/manuais/feed.xml` |
| NFS-e | `nfse/feed.xml` |
| SVRS — NF-e | `svrs/nfe/documentos/feed.xml` |
| SVRS — NFC-e | `svrs/nfce/documentos/feed.xml` |
| SVRS — CT-e | `svrs/cte/documentos/feed.xml` |
| SVRS — MDF-e | `svrs/mdfe/documentos/feed.xml` |
| SVRS — BP-e | `svrs/bpe/documentos/feed.xml` |
| SVRS — NF3e | `svrs/nf3e/documentos/feed.xml` |
| SVRS — NFCom | `svrs/nfcom/documentos/feed.xml` |
| SVRS — NFAg | `svrs/nfag/documentos/feed.xml` |
| SVRS — NFGas | `svrs/nfgas/documentos/feed.xml` |
| SVRS — DC-e | `svrs/dce/documentos/feed.xml` |
| SVRS — NFABI | `svrs/nfabi/documentos/feed.xml` |
| SVRS — DIFAL | `svrs/difal/documentos/feed.xml` |
| SVRS — NFF | `svrs/nff/documentos/feed.xml` |
| SVRS — PES | `svrs/pes/documentos/feed.xml` |
| SVRS — ONE | `svrs/one/documentos/feed.xml` |

</details>

**Newsletter por e-mail:** apontar Mailchimp, Buttondown ou Kill the Newsletter pra qualquer URL de feed. Cada publicação nova vira e-mail automático pra sua lista, sem trabalho manual.

### Manifest JSON (integração via código)

Sua aplicação consome o manifest diretamente e reage a mudanças. Recomendado consultar uma vez por dia após 09:15 UTC e comparar `generated_at` com a última leitura.

- **Sitemap geral:** `https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json`
- **Histórico por fonte:** `.../data/<fonte>/history.json`

<details>
<summary><b>Manifests por fonte</b> (22 URLs)</summary>

Base: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/`

| Fonte | Path |
|---|---|
| NF-e — Esquemas XML | `nfe/esquemas-xml/manifest.json` |
| NF-e — Notas Técnicas | `nfe/notas-tecnicas/manifest.json` |
| NF-e — Informes Técnicos | `nfe/informes-tecnicos/manifest.json` |
| NF-e — Diversos | `nfe/diversos/manifest.json` |
| NF-e — Manuais | `nfe/manuais/manifest.json` |
| NFS-e | `nfse/manifest.json` |
| SVRS — NF-e | `svrs/nfe/documentos/manifest.json` |
| SVRS — NFC-e | `svrs/nfce/documentos/manifest.json` |
| SVRS — CT-e | `svrs/cte/documentos/manifest.json` |
| SVRS — MDF-e | `svrs/mdfe/documentos/manifest.json` |
| SVRS — BP-e | `svrs/bpe/documentos/manifest.json` |
| SVRS — NF3e | `svrs/nf3e/documentos/manifest.json` |
| SVRS — NFCom | `svrs/nfcom/documentos/manifest.json` |
| SVRS — NFAg | `svrs/nfag/documentos/manifest.json` |
| SVRS — NFGas | `svrs/nfgas/documentos/manifest.json` |
| SVRS — DC-e | `svrs/dce/documentos/manifest.json` |
| SVRS — NFABI | `svrs/nfabi/documentos/manifest.json` |
| SVRS — DIFAL | `svrs/difal/documentos/manifest.json` |
| SVRS — NFF | `svrs/nff/documentos/manifest.json` |
| SVRS — PES | `svrs/pes/documentos/manifest.json` |
| SVRS — ONE | `svrs/one/documentos/manifest.json` |

</details>

## O que você recebe

Cada item aparece com estrutura completa em ambos os canais:

- **Título** — nome oficial do documento como publicado.
- **Descrição** — versão limpa do título, sem sufixos de data ou formato.
- **Data de publicação** — normalizada em `YYYY-MM-DD`, extraída da própria fonte oficial.
- **Seção** — Guia, Manual, Esquema XSD, Anexo, Nota Técnica etc.
- **URL original** — link direto pro portal SEFAZ, ADN ou SVRS.
- **Arquivos** — PDF, ZIP, XSD, XML, XLSX espelhados aqui, mais o conteúdo já descompactado quando é ZIP.

## Fontes cobertas

Legenda de origem: **SEFAZ** = portal SEFAZ homologação (base normativa nacional). **ADN** = ADN nacional gov.br. **SVRS** = portal DF-e da SEFAZ Virtual RS (22 UFs).

| Fonte | Origem | Tipo | O que traz | Formatos |
|---|---|---|---|---|
| NF-e — Esquemas XML | SEFAZ | fiscal | Pacotes de Liberação, XSDs, eventos, cartas de correção | ZIP, XSD, XML |
| NF-e — Notas Técnicas | SEFAZ | fiscal | Notas Técnicas oficiais vigentes e anteriores | PDF, DOC, DOCX |
| NF-e — Informes Técnicos | SEFAZ | fiscal | Informes Técnicos oficiais vigentes | PDF, DOC, DOCX |
| NF-e — Diversos | SEFAZ | fiscal | Publicações avulsas e complementares | PDF, ZIP, DOC |
| NF-e — Manuais | SEFAZ | fiscal | MOC, Manual do Emissor e demais manuais oficiais | PDF, ZIP, DOC |
| NFS-e | ADN | fiscal | Guias, manuais, esquemas XSD, anexos de domínio e layout | PDF, ZIP, XSD, XLSX |
| NF-e | SVRS | fiscal | Publicação da SEFAZ Virtual RS, atende 22 UFs | PDF, ZIP, XLSX |
| NFC-e | SVRS | fiscal | Manuais, notas técnicas e schemas da Nota Fiscal de Consumidor | PDF, ZIP, XLSX |
| CT-e | SVRS | fiscal | Manuais, notas técnicas e schemas do Conhecimento de Transporte | PDF, ZIP, XLSX |
| MDF-e | SVRS | fiscal | Manuais, notas técnicas e schemas do Manifesto de Documentos Fiscais | PDF, ZIP, XLSX |
| BP-e | SVRS | fiscal | Manuais, notas técnicas e schemas do Bilhete de Passagem | PDF, ZIP, XLSX |
| NF3e | SVRS | fiscal | Nota Fiscal de Energia Elétrica | PDF, ZIP, XLSX |
| NFCom | SVRS | fiscal | Nota Fiscal de Serviço de Comunicação | PDF, ZIP, XLSX |
| NFAg | SVRS | fiscal | Nota Fiscal de Produtor Agropecuário | PDF, ZIP, XLSX |
| NFGas | SVRS | fiscal | Nota Fiscal de Gás Canalizado | PDF, ZIP, XLSX |
| DC-e | SVRS | fiscal | Declaração de Conteúdo eletrônica | PDF, ZIP, XLSX |
| NFABI | SVRS | fiscal | Nota Fiscal de Abastecimento | PDF, ZIP, XLSX |
| DIFAL | SVRS | tributário | Diferencial de alíquota — não é documento fiscal emitível | PDF, ZIP, XLSX |
| NFF | SVRS | infra | Nota Fiscal Fácil — meta-documento de infraestrutura | PDF, ZIP, XLSX |
| PES | SVRS | infra | Portal de Entrega Simplificada — meta-documento | PDF, ZIP, XLSX |
| ONE | SVRS | infra | Operador Nacional do Estacionamento — meta-documento | PDF, ZIP, XLSX |

A NF-e tem **duas origens oficiais** aqui, e as duas ficam: SEFAZ é a base normativa nacional, SVRS é o que 22 UFs publicam. As duas podem divulgar o mesmo documento em datas diferentes, então nada é deduplicado entre elas — o contexto `svrs/` existe justamente pra você escolher qual segue.

Linhas marcadas como `tributário` ou `infra` não são documentos fiscais emitíveis: DIFAL é tributário e NFF/PES/ONE são meta-documentos de infraestrutura da SVRS. Estão aqui porque a fonte é a mesma e a documentação importa para quem integra, mas não têm equivalente na API do Stackin.

Portais estaduais próprios (SP, MG, PR, MT, MS) entram sob demanda.

## Por que existe

Todo integrador fiscal brasileiro repete o mesmo trabalho: monitorar dois portais, baixar zip, descompactar, comparar, guardar, avisar o time. Manualmente. Todo mês, todo trimestre, toda Nota Técnica.

Isso não é diferencial de produto. É custo compartilhado que ninguém precisa pagar duas vezes. O `data-source` resolve uma vez pra todo mundo, em código aberto.

Feito pela [Stackin](https://app.stackin.io). Precisa SLA, mirror privado ou webhook direto? [support@stackin.io](mailto:support@stackin.io).

## Licença

- **Código** (scrapers, geração de feed/manifest, workflows): [AGPL-3.0](LICENSE). Rehost como serviço, mesmo sem redistribuir binário, exige publicar código-fonte de qualquer modificação (§13 — cláusula "SaaS").
- **Feed Atom e Manifest JSON** (estruturas geradas por este projeto): [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Exige atribuição visível a `stackin-io/data-source` em qualquer app que consuma.
- **Arquivos oficiais em `data/**`** (PDFs, ZIPs, XSDs, XMLs): domínio público, mantêm autoria dos órgãos originais (SEFAZ, ADN gov.br, SVRS). Este projeto apenas espelha.

Para uso comercial fora da AGPL, contatar [support@stackin.io](mailto:support@stackin.io) — exceções comerciais podem ser negociadas.

---

<sub>**Keywords:** NF-e, NFe, NFS-e, NFSe, NFC-e, CT-e, MDF-e, BP-e, NF3e, NFCom, SEFAZ, ADN, gov.br, SVRS, Brasil, Nota Fiscal Eletrônica, Nota Fiscal de Serviços, MOC, Manual de Orientação do Contribuinte, Nota Técnica, XSD, XML schema, Pacote de Liberação, fiscal, tax, invoicing, stackin, atom, RSS feed, newsletter fiscal.</sub>
