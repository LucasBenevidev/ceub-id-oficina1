"""
Script de PREPARAÇÃO PRÉVIA - rodar ANTES da aula, na máquina do professor
(fora do ambiente Astro/Docker, direto no seu Python local).

Gera o arquivo include/data/enem_municipios_medias.csv a partir dos
microdados COMPLETOS do ENEM.

PASSO A PASSO:
1. Baixe os microdados em: https://download.inep.gov.br/microdados/microdados_enem
2. Extraia o .zip e localize o CSV principal dentro da pasta DADOS/
   (ex.: MICRODADOS_ENEM_2023.csv)
3. Ajuste CAMINHO_MICRODADOS abaixo para apontar para esse arquivo
4. Rode: python prepare_enem_data.py
5. Copie o CSV gerado para include/data/enem_municipios_medias.csv no repositório

ATENÇÃO:
- Os nomes exatos das colunas podem mudar de uma edição do ENEM para outra.
  Confira o "Dicionário de Dados" que acompanha o download e ajuste
  COLUNAS_NECESSARIAS abaixo se necessário.
- O arquivo completo tem vários gigabytes: este script lê em pedaços (chunks)
  para não estourar a memória RAM. Mesmo assim, pode levar alguns minutos.
"""
import pandas as pd

CAMINHO_MICRODADOS = "MICRODADOS_ENEM_2023.csv"  # ajuste o caminho e o ano
ENCODING = "latin-1"   # microdados do INEP costumam vir em latin-1
SEPARADOR = ";"        # e separados por ponto e vírgula

COLUNAS_NECESSARIAS = [
    "CO_MUNICIPIO_PROVA",   # código do município (padrão IBGE de 7 dígitos)
    "NO_MUNICIPIO_PROVA",
    "SG_UF_PROVA",
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO",
]

acumulador = []

leitor = pd.read_csv(
    CAMINHO_MICRODADOS,
    sep=SEPARADOR,
    encoding=ENCODING,
    usecols=COLUNAS_NECESSARIAS,
    chunksize=200_000,
)

for pedaco in leitor:
    pedaco = pedaco.dropna(
        subset=["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    )
    pedaco["nota_media_enem"] = pedaco[
        ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    ].mean(axis=1)
    acumulador.append(pedaco)

dados = pd.concat(acumulador, ignore_index=True)

resumo = (
    dados.groupby(["CO_MUNICIPIO_PROVA", "NO_MUNICIPIO_PROVA", "SG_UF_PROVA"])
    .agg(
        nota_media_enem=("nota_media_enem", "mean"),
        numero_participantes=("nota_media_enem", "count"),
    )
    .reset_index()
    .rename(columns={
        "CO_MUNICIPIO_PROVA": "codigo_municipio_ibge",
        "NO_MUNICIPIO_PROVA": "municipio",
        "SG_UF_PROVA": "uf",
    })
)

resumo.to_csv("enem_municipios_medias.csv", index=False)
print(f"Arquivo gerado com {len(resumo)} municípios: enem_municipios_medias.csv")
