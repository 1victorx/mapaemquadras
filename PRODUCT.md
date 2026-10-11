# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Leiturista de água que percorre diferentes rotas em João Pessoa e precisa consultar quadras durante o trabalho de campo. O uso principal é pelo celular.

## Product Purpose

Ajudar o leiturista a relacionar bairro, setor e número da quadra aos logradouros próximos e montar a lista ordenada das quadras do dia. O sucesso é identificar a rua de referência rapidamente e abrir sua localização no Google Maps.

## Positioning

A consulta usa quadras e logradouros da base cartográfica municipal Filipeia/SEPLAN/PMJP, permitindo localizar ruas a partir da identificação por bairro, setor e quadra usada na rota de leitura.

## Operating Context

O usuário percorre uma rota diferente a cada dia, e a quantidade de quadras pode variar. A consulta ocorre em campo e a lista diária permanece disponível no aparelho. O fluxo termina com a abertura de um logradouro no Google Maps.

## Capabilities and Constraints

- Selecionar bairro, informar setor e quadra e adicionar quantas quadras forem necessárias, mantendo a ordem de trabalho.
- Consultar logradouros próximos e abrir cada localização no Google Maps.
- Salvar a lista diária localmente no navegador; não há conta ou sincronização.
- Os nomes de rua e as associações bairro/quadra dependem da base municipal fornecida. A proximidade calculada indica referência cartográfica e precisa ser conferida no mapa.

## Evidence on Hand

- Shapefiles municipais de quadras, bairros e logradouros em `data/source`.
- Índice local com 8.986 quadras em `data/generated/quadras.json`; a primeira geração excluiu registros sem associação espacial resolvida.
- Portal de consulta e origem: Filipeia/SEPLAN/PMJP, https://filipeia.joaopessoa.pb.gov.br/sigweb/.
- A combinação Torre / Setor 10 / Quadra 119 foi verificada na base e associada a quatro logradouros próximos.

## Product Principles

- Priorizar leitura rápida em campo, especialmente em telas de celular.
- Tratar a ordem da rota diária como parte central do fluxo.
- Mostrar claramente quando a combinação informada diverge da base oficial e oferecer um caminho de recuperação.
- Abrir destinos de mapa diretamente a partir de cada logradouro.
- Preservar a atribuição e os limites dos dados municipais.
