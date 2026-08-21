# Dados necessários para a oficina (Webaula 07)

Antes da aula, coloque os dois arquivos abaixo nesta pasta (`include/data/`).
Sem eles, o DAG `enem_idhm_pipeline` falha logo na etapa de extração.

## 1. `enem_municipios_medias.csv`
Gerado a partir dos microdados completos do ENEM (INEP), usando o script
`prepare_enem_data.py` que está na raiz deste repositório. Veja as instruções
detalhadas dentro do próprio script.

Colunas esperadas:
- `codigo_municipio_ibge`
- `municipio`
- `uf`
- `nota_media_enem`
- `numero_participantes`

## 2. `idhm_municipios.csv`
Tabela do IDHM (Índice de Desenvolvimento Humano Municipal), disponível no
Atlas do Desenvolvimento Humano no Brasil (PNUD/IBGE/Ipea):
https://www.atlasbrasil.org.br/consulta/planilha

Baixe a planilha de IDHM por município, e salve como CSV com (pelo menos)
estas colunas, renomeando se necessário:
- `codigo_municipio_ibge` (código IBGE de 7 dígitos — confira se bate com a
  coluna `CO_MUNICIPIO_PROVA` do ENEM; em alguns casos é preciso usar apenas
  os 6 primeiros dígitos, dependendo da fonte)
- `idhm`

## Dica de verificação rápida
Antes da aula, abra os dois CSVs e confira:
- Se `codigo_municipio_ibge` está no mesmo formato (mesmo número de dígitos,
  mesmo tipo) nas duas bases — essa é a causa mais comum de um `merge` que
  "não encontra nada" durante a oficina.
