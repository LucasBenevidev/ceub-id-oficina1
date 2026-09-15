"""
Script para download e preparação dos dados do IDHM Municipal (Atlas Brasil / PNUD / IPEA).
Gera o arquivo 'include/data/idhm_municipios.csv' formatado para o pipeline.
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "include" / "data"
OUTPUT_CSV = OUTPUT_DIR / "idhm_municipios.csv"

# Base pública consolidada do Atlas do Desenvolvimento Humano (PNUD/IPEA/FJP)
DATA_URL = "https://raw.githubusercontent.com/mauriciocramos/IDHM/master/municipal.csv"


def download_and_prepare_idhm():
    print("=" * 60)
    print("Baixando base de IDHM dos municípios (Atlas Brasil / PNUD)...")
    print(f"URL de origem: {DATA_URL}")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Leitura da base completa do Atlas Brasil
    df = pd.read_csv(
        DATA_URL,
        sep=";",
        decimal=",",
        encoding="utf-8",
        low_memory=False,
        usecols=["ANO", "Codmun7", "Município", "UF", "IDHM", "IDHM_E", "IDHM_L", "IDHM_R"]
    )

    # Filtrar o ano mais recente da série (2010)
    df_2010 = df[df["ANO"] == 2010].copy()

    # Converter IDHM para numérico caso necessário
    df_2010["IDHM"] = pd.to_numeric(df_2010["IDHM"], errors="coerce")

    # Renomear colunas para o padrão esperado pelo pipeline Airflow
    df_final = df_2010.rename(columns={
        "Codmun7": "codigo_municipio_ibge",
        "Município": "municipio",
        "IDHM": "idhm"
    })[["codigo_municipio_ibge", "municipio", "idhm"]].dropna(subset=["codigo_municipio_ibge", "idhm"])

    df_final["codigo_municipio_ibge"] = df_final["codigo_municipio_ibge"].astype(int)
    df_final.sort_values(by="codigo_municipio_ibge", inplace=True)

    # Salvar no diretório esperado
    df_final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print("=" * 60)
    print(f"Sucesso! Arquivo gerado em: {OUTPUT_CSV}")
    print(f"Total de municípios com IDHM: {len(df_final):,}".replace(",", "."))
    print("=" * 60)
    print("\nPrévia dos dados:")
    print(df_final.head(10))


if __name__ == "__main__":
    download_and_prepare_idhm()
