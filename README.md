<div align="center">

<img src="https://raw.githubusercontent.com/stackin-io/stackin-python-sdk/master/docs/assets/stackin.png" width="120" />

**A base fiscal brasileira, sempre atualizada — sem clicar em nada.**

[![Feed](https://img.shields.io/badge/feed-atom-orange?style=flat-square)](https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml)
[![Manifest](https://img.shields.io/badge/manifest-json-blue?style=flat-square)](https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json)
[![Schedule](https://img.shields.io/badge/updates-a%20cada%206h-success?style=flat-square)](.github/workflows)
[![License](https://img.shields.io/badge/license-MIT-informational?style=flat-square)](LICENSE)

[Assinar feed](https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml) · [Ver manifest](https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json) · [stackin.io](https://stackin.io)

</div>

---

# data-source — Feed oficial de atualizações fiscais brasileiras (NF-e, NFS-e)

> XSDs, MOCs, notas técnicas, esquemas XML, manuais e anexos do **portal oficial da NF-e (SEFAZ)** e do **ADN nacional da NFS-e (gov.br)** — coletados a cada 6 horas, versionados, publicados como feed Atom e sitemap JSON.

Toda vez que a SEFAZ ou o ADN publica um novo XSD, um MOC, uma Nota Técnica ou uma versão de schema, o `data-source` percebe, baixa, descompacta, versiona e avisa. Você não precisa entrar no portal, não precisa checar página, não precisa se lembrar. **Você só assina.**

Feito pra quem constrói produto fiscal e não pode perder uma atualização — ERPs, integradores, contadores, times de compliance e todo mundo que hoje mantém uma planilha de "quando foi a última vez que olhei o portal".

## O que você ganha

- **Nunca mais fica desatualizado.** Portal oficial da NF-e e ADN da NFS-e varridos a cada 6 horas. Novo pacote publicado hoje aparece aqui hoje.
- **Um único lugar pra pegar tudo.** XSDs, MOCs, manuais, notas técnicas, eventos, cartas de correção — organizados por data e assunto, prontos pra baixar.
- **Assinatura via feed** (Atom/RSS). Coloca no Feedly, no Slack, no e-mail, no que quiser — cada versão nova vira uma notificação.
- **Sitemap JSON público.** Sua aplicação consome o manifest, pega só o que mudou, e nunca chama o portal de origem — zero risco de bloqueio, zero fricção com a SEFAZ.
- **ZIP descompactado sozinho.** Cada pacote vem com o arquivo original e a pasta extraída pronta pra consumir.
- **Histórico completo.** Toda execução fica registrada em `history.json`. Auditoria e rastreabilidade em um único arquivo.

## Fontes cobertas hoje

| Fonte | Descrição | Frequência |
|---|---|---|
| **NF-e** — portal oficial | Pacotes de Liberação, MOC, Notas Técnicas, eventos, cartas de correção | 6h |
| **NF-e homologação** | Ambiente de testes SEFAZ | 6h |
| **NFS-e** — ADN nacional | Documentação técnica, biblioteca de XSDs e manuais | 6h |

Outras fontes fiscais (NFC-e, DF-e, projetos estaduais) entram sob demanda — o framework foi feito pra isso.

## Como assinar

### Feed único (todas as fontes)

```
https://raw.githubusercontent.com/stackin-io/data-source/master/data/feed.xml
```

Cola em qualquer leitor de RSS/Atom e pronto. Feedly, Inoreader, NetNewsWire, Slack, Discord, Mailchimp, Buttondown, Kill the Newsletter — todos aceitam Atom nativo.

### Feed por fonte

```
https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfe/feed.xml
https://raw.githubusercontent.com/stackin-io/data-source/master/data/nfse/feed.xml
```

Só NF-e ou só NFS-e — pra times que só se importam com uma das duas.

### Newsletter por e-mail

Aponte serviços tipo [Mailchimp RSS Campaign](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/), [Buttondown](https://buttondown.email/) ou [Kill the Newsletter](https://kill-the-newsletter.com/) pro feed acima. Cada publicação nova vira e-mail automático pra sua lista.

### Sitemap JSON

Aplicações consomem direto o manifest público:

```
https://raw.githubusercontent.com/stackin-io/data-source/master/data/manifest.json
```

Retorna a lista de contextos, contagens e link pros manifests detalhados de cada fonte. Cada manifest de fonte traz título, descrição, data de publicação, URL original e link direto pros arquivos já hospedados aqui.

## Como funciona por baixo

Todo o processo roda em GitHub Actions — sem servidor, sem banco de dados, sem custo de infra. A cada 6 horas o job varre as fontes, baixa o que é novo (pula o que já baixou), descompacta ZIPs, atualiza os manifests e feeds, e comita tudo no próprio repositório. Reprodutível, auditável, gratuito.

Genérico por design: adicionar uma nova fonte é criar uma classe, apontar a URL, e reaproveitar tudo — download com retry, descompactação, storage, feed, manifest, histórico. Um scraper novo vira feed público na hora.

## Por que existe

Todo integrador fiscal brasileiro repete o mesmo trabalho: monitorar dois portais, baixar zip, descompactar, comparar, guardar, avisar o time. Manualmente. Todo mês. Todo trimestre. Toda vez que a SEFAZ solta uma NT.

Isso não é diferencial de produto. É custo compartilhado que ninguém precisa pagar duas vezes. O `data-source` resolve uma vez pra todo mundo, em código aberto, versionado.

Feito pela [Stackin](https://stackin.io) — plataforma completa de emissão fiscal para o Brasil.

---

<div align="center">

Feito com ☕ e frustração acumulada com portais fiscais.

</div>

<!--
Keywords: NF-e, NFe, NFS-e, NFSe, SEFAZ, ADN, gov.br, Brasil, Nota Fiscal Eletrônica,
Nota Fiscal de Serviços, MOC, Manual de Orientação do Contribuinte, Nota Técnica, XSD,
XML schema, Pacote de Liberação, ICMS, tributário, fiscal, tax, invoicing, stackin,
sitemap, atom, RSS feed, newsletter, scraping, monitoring, GitHub Actions.
-->

