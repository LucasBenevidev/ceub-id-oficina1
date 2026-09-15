"""
Script de preparação prévia dos dados do ENEM 2025.
Gera o arquivo 'include/data/enem_municipios_medias.csv' agregando as notas
por município a partir dos microdados brutos em 'bigData/'.

Execução exclusiva do professor antes da oficina.
"""

from pathlib import Path
import pandas as pd
import numpy as np

# 1. Definição dos caminhos
BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "bigData" / "microdados_enem_2025" / "DADOS" / "RESULTADOS_2025.csv"
OUTPUT_DIR = BASE_DIR / "include" / "data"
OUTPUT_CSV = OUTPUT_DIR / "enem_municipios_medias.csv"

# Colunas necessárias do arquivo bruto
COLS_TO_USE = [
    "CO_MUNICIPIO_PROVA",
    "NO_MUNICIPIO_PROVA",
    "SG_UF_PROVA",
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO"
]

NOTA_COLS = [
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO"
]


def process_enem_data():
    print("=" * 60)
    print("Iniciando preparação dos dados do ENEM 2025...")
    print(f"Arquivo de origem: {INPUT_CSV}")
    print("=" * 60)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado em: {INPUT_CSV}\n"
            "Verifique se a pasta bigData/microdados_enem_2025/DADOS/RESULTADOS_2025.csv existe."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Dicionário de agregação acumulada por município:
    # {cod_ibge: {'municipio': str, 'uf': str, 'soma_notas': float, 'total_alunos': int}}
    municipio_stats = {}

    chunk_size = 100_000
    total_processados = 0

    print("Processando microdados em lotes de 100.000 linhas...")
    for chunk in pd.read_csv(
        INPUT_CSV,
        sep=";",
        encoding="latin-1",
        usecols=COLS_TO_USE,
        chunksize=chunk_size,
        low_memory=False
    ):
        # Converter notas para numérico (substituindo erros por NaN)
        for col in NOTA_COLS:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

        # Filtrar apenas participantes que tenham realizado ao menos uma prova
        # Calcula a média do participante entre as 5 áreas
        chunk["media_participante"] = chunk[NOTA_COLS].mean(axis=1, skipna=True)

        # Remove linhas sem nota e sem código de município
        valid_chunk = chunk.dropna(subset=["CO_MUNICIPIO_PROVA", "media_participante"]).copy()
        valid_chunk["CO_MUNICIPIO_PROVA"] = valid_chunk["CO_MUNICIPIO_PROVA"].astype(int)

        # Agregação por município no lote atual
        grouped = valid_chunk.groupby("CO_MUNICIPIO_PROVA").agg(
            municipio=("NO_MUNICIPIO_PROVA", "first"),
            uf=("SG_UF_PROVA", "first"),
            soma_notas=("media_participante", "sum"),
            contagem=("media_participante", "count")
        ).reset_index()

        # Acumulação global
        for _, row in grouped.iterrows():
            cod = int(row["CO_MUNICIPIO_PROVA"])
            if cod not in municipio_stats:
                municipio_stats[cod] = {
                    "municipio": row["municipio"],
                    "uf": row["uf"],
                    "soma_notas": 0.0,
                    "contagem": 0
                }
            municipio_stats[cod]["soma_notas"] += row["soma_notas"]
            municipio_stats[cod]["contagem"] += row["contagem"]

        total_processados += len(chunk)
        print(f" -> {total_processados:,} registros lidos...".replace(",", "."))

    # Construção do DataFrame final
    print("\nConsolidando médias municipais...")
    records = []
    for cod, dados in municipio_stats.items():
        if dados["contagem"] > 0:
            media = round(dados["soma_notas"] / dados["contagem"], 2)
            records.append({
                "codigo_municipio_ibge": cod,
                "municipio": dados["municipio"],
                "uf": dados["uf"],
                "nota_media_enem": media,
                "numero_participantes": int(dados["contagem"])
            })

    df_final = pd.DataFrame(records)
    df_final.sort_values(by=["uf", "municipio"], inplace=True)

    # Salva o arquivo final
    df_final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print("=" * 60)
    print(f"Sucesso! Arquivo gerado em: {OUTPUT_CSV}")
    print(f"Total de municípios processados: {len(df_final):,}".replace(",", "."))
    print("=" * 60)
    print("\nPrévia dos dados gerados:")
    print(df_final.head(10))


if __name__ == "__main__":
    process_enem_data()