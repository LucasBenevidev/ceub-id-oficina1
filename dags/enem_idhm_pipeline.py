"""
Webaula 07 - Oficina de Orquestração com Apache Airflow (Astronomer / Astro CLI)
Disciplina: Ingestão de Dados - Pós-Graduação EAD - CEUB
Prof. Lucas Benevides

Pipeline: cruzamento das médias municipais do ENEM (INEP) com o IDHM municipal
(IBGE / Atlas Brasil), demonstrando um fluxo clássico de Extract -> Transform -> Load,
com tratamento de falhas (retries) e uma etapa final de validação (desafio da turma).

IMPORTANTE: este DAG espera que os arquivos abaixo já estejam na pasta include/data/
antes do início da aula (ver include/data/README.md e o script prepare_enem_data.py):
    - enem_municipios_medias.csv
    - idhm_municipios.csv
"""
import os
from datetime import datetime, timedelta

import pandas as pd
from airflow.decorators import dag, task

DATA_DIR = "/usr/local/airflow/include/data"
OUTPUT_DIR = "/usr/local/airflow/include/output"

default_args = {
    "owner": "prof-lucas-benevides",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,  # espera crescente entre tentativas (Webaula 06)
    "max_retry_delay": timedelta(minutes=10),
}


@dag(
    dag_id="enem_idhm_pipeline",
    description="Cruza médias municipais do ENEM com o IDHM municipal (IBGE)",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # execução manual durante a oficina (não precisa de agendamento)
    catchup=False,
    default_args=default_args,
    tags=["webaula07", "enem", "idhm"],
)
def enem_idhm_pipeline():
    @task
    def extract_enem() -> str:
        """Lê o CSV de médias municipais do ENEM, já pré-processado antes da aula."""
        path = f"{DATA_DIR}/enem_municipios_medias.csv"
        df = pd.read_csv(path)
        print(f"ENEM: {len(df)} municípios carregados.")
        return path

    @task
    def extract_idhm() -> str:
        """Lê o CSV do IDHM municipal (IBGE / Atlas Brasil)."""
        path = f"{DATA_DIR}/idhm_municipios.csv"
        df = pd.read_csv(path)
        print(f"IDHM: {len(df)} municípios carregados.")
        return path

    @task
    def transform(enem_path: str, idhm_path: str) -> str:
        """Cruza as duas bases pelo código do município (IBGE) e calcula um indicador simples."""
        enem = pd.read_csv(enem_path)
        idhm = pd.read_csv(idhm_path)

        # TODO (em aula): conferir se os nomes/tipos da coluna de código do
        # município batem nas duas bases antes do merge (ex.: str vs int)
        df = pd.merge(enem, idhm, on="codigo_municipio_ibge", how="inner")

        correlacao = df["nota_media_enem"].corr(df["idhm"])
        print(f"Correlação (Pearson) entre nota média do ENEM e o IDHM: {correlacao:.3f}")

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = f"{OUTPUT_DIR}/enem_idhm_join.csv"
        df.to_csv(output_path, index=False)
        return output_path

    @task
    def validate(joined_path: str) -> None:
        """
        DESAFIO DA AULA (os alunos completam esta etapa):
        validar se o arquivo de saída não está vazio e se não há notas médias
        fora do intervalo plausível (0 a 1000 pontos).
        """
        df = pd.read_csv(joined_path)

        assert len(df) > 0, "O arquivo de saída está vazio!"

        # TODO (desafio dos alunos): descomente e complete a validação abaixo
        # assert df["nota_media_enem"].between(0, 1000).all(), (
        #     "Existe(m) município(s) com nota média fora do intervalo esperado!"
        # )

        print(f"Validação concluída com sucesso. {len(df)} municípios no resultado final.")

    enem = extract_enem()
    idhm = extract_idhm()
    joined = transform(enem, idhm)
    validate(joined)


enem_idhm_pipeline()
