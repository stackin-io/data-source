<div align="center">

<img src="https://raw.githubusercontent.com/stackin-io/stackin-python-sdk/master/docs/assets/stackin.png" width="120" />

**A base fiscal brasileira, sempre atualizada — sem clicar em nada.**

[![Feed](https://img.shields.io/badge/feed-atom-orange?style=flat-square)](https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml)
[![Manifest](https://img.shields.io/badge/manifest-json-blue?style=flat-square)](https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json)
[![Updates](https://img.shields.io/badge/updates-a%20cada%206h-success?style=flat-square)](.github/workflows)
[![License](https://img.shields.io/badge/license-MIT-informational?style=flat-square)](LICENSE)

[Assinar newsletter](https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml) · [Manifest JSON](https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json) · [app.stackin.io](https://app.stackin.io)

</div>

---

# data-source

Publicações oficiais da **NF-e** (portal SEFAZ) e da **NFS-e** (ADN nacional gov.br) sempre atualizadas e organizadas. Nunca mais entra num portal fiscal pra ver se saiu XSD novo, MOC novo, Nota Técnica nova, anexo novo. A gente monitora, baixa, versiona e avisa.

## Como funciona

A cada **6 horas**, um robô varre os portais oficiais, identifica o que é novidade em relação à última passagem, baixa os arquivos, descompacta os ZIPs, e organiza tudo por data de publicação. Cada documento fica numa pasta própria com título completo, data e todos os arquivos que compõem o pacote.

Duas coisas são publicadas todo ciclo:

- Um **feed Atom (XML)** — a lista das últimas publicações, no mesmo formato usado por blogs e sites de notícia. Leitores de RSS entendem, serviços de e-mail marketing entendem, integrações via webhook entendem.
- Um **manifest JSON** — um catálogo estruturado com título, descrição, data de publicação, seção (Guia / Manual / XSD / Anexo etc), link do arquivo original no portal e link direto pro arquivo já espelhado aqui.

Nada muda quando não há novidade: o feed e o manifest continuam válidos, só sem entrada nova. Quando muda, aparece em ambos no mesmo minuto.

## Como se inscrever

### Newsletter (feed Atom)

Cola a URL do feed em qualquer leitor de RSS/Atom — Feedly, Inoreader, NetNewsWire, Slack, Discord, Notion. Novidade nova = notificação nova.

- Todas as fontes: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml`
- Só NF-e — Esquemas XML: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/esquemas-xml/feed.xml`
- Só NF-e — Notas Técnicas: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/notas-tecnicas/feed.xml`
- Só NF-e — Informes Técnicos: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/informes-tecnicos/feed.xml`
- Só NF-e — Diversos: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/diversos/feed.xml`
- Só NF-e — Manuais: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/manuais/feed.xml`
- Só NFS-e: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfse/feed.xml`

**Newsletter por e-mail:** apontar Mailchimp, Buttondown ou Kill the Newsletter pra qualquer uma das URLs acima. Cada publicação nova vira e-mail automático pra sua lista, sem trabalho manual.

### Manifest JSON (integração via código)

Sua aplicação consome o manifest diretamente e reage a mudanças. Recomendado consultar de hora em hora e comparar `generated_at` com a última leitura.

- Sitemap geral: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json`
- NF-e — Esquemas XML: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/esquemas-xml/manifest.json`
- NF-e — Notas Técnicas: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/notas-tecnicas/manifest.json`
- NF-e — Informes Técnicos: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/informes-tecnicos/manifest.json`
- NF-e — Diversos: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/diversos/manifest.json`
- NF-e — Manuais: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/manuais/manifest.json`
- NFS-e: `https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfse/manifest.json`
- Histórico por fonte: `.../data/<fonte>/history.json`

## O que você recebe

Cada item aparece com estrutura completa em ambos os canais:

- **Título** — nome oficial do documento como publicado.
- **Descrição** — versão limpa do título, sem sufixos de data ou formato.
- **Data de publicação** — normalizada em `YYYY-MM-DD`, extraída da própria fonte oficial.
- **Seção** — Guia, Manual, Esquema XSD, Anexo, Nota Técnica etc.
- **URL original** — link direto pro portal SEFAZ ou ADN.
- **Arquivos** — PDF, ZIP, XSD, XML, XLSX espelhados aqui, mais o conteúdo já descompactado quando é ZIP.

## Fontes cobertas

| Fonte | Categoria | O que traz | Formatos |
|---|---|---|---|
| **NF-e** (portal SEFAZ homologação) | **Esquemas XML** | Pacotes de Liberação, XSDs, eventos, cartas de correção | ZIP, XSD, XML |
| **NF-e** (portal SEFAZ homologação) | **Notas Técnicas** | Notas Técnicas oficiais vigentes e anteriores | PDF, DOC, DOCX |
| **NF-e** (portal SEFAZ homologação) | **Informes Técnicos** | Informes Técnicos oficiais vigentes | PDF, DOC, DOCX |
| **NF-e** (portal SEFAZ homologação) | **Diversos** | Publicações avulsas e complementares | PDF, ZIP, DOC |
| **NF-e** (portal SEFAZ homologação) | **Manuais** | MOC, Manual do Emissor e demais manuais oficiais | PDF, ZIP, DOC |
| **NFS-e** (ADN nacional gov.br) | — | Guias, manuais, esquemas XSD, anexos de domínio e layout | PDF, ZIP, XSD, XLSX |

Outras fontes (NFC-e, DF-e, projetos estaduais) entram sob demanda.

## Por que existe

Todo integrador fiscal brasileiro repete o mesmo trabalho: monitorar dois portais, baixar zip, descompactar, comparar, guardar, avisar o time. Manualmente. Todo mês, todo trimestre, toda Nota Técnica.

Isso não é diferencial de produto. É custo compartilhado que ninguém precisa pagar duas vezes. O `data-source` resolve uma vez pra todo mundo, em código aberto.

Feito pela [Stackin](https://app.stackin.io).

<!--
Keywords: NF-e, NFe, NFS-e, NFSe, SEFAZ, ADN, gov.br, Brasil, Nota Fiscal Eletrônica,
Nota Fiscal de Serviços, MOC, Manual de Orientação do Contribuinte, Nota Técnica, XSD,
XML schema, Pacote de Liberação, fiscal, tax, invoicing, stackin, sitemap, atom, RSS
feed, newsletter.
-->
