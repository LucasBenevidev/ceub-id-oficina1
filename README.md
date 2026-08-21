# Webaula 07 — Oficina de Orquestração com Apache Airflow (Astro CLI)

Disciplina: Ingestão de Dados — Pós-Graduação EAD — CEUB
Prof. Lucas Benevides

## O que este repositório contém
- `dags/enem_idhm_pipeline.py` — a DAG que vamos executar e adaptar em aula.
- `prepare_enem_data.py` — script de preparação prévia dos dados (só o professor roda, antes da aula).
- `include/data/` — pasta onde ficam os dois arquivos de dados usados pelo pipeline (ver `include/data/README.md`).
- `include/output/` — pasta onde o resultado final (`enem_idhm_join.csv`) será salvo após a execução do DAG.

## Pré-requisitos (já devem estar instalados antes da aula)
- Docker Desktop rodando
- Astro CLI instalado (`astro version` deve funcionar no terminal)

## Passo a passo para os alunos, no início da aula

1. Clonar o repositório:
   ```bash
   git clone https://github.com/LucasBenevidev/ceub-id-oficina1.git
   cd ceub-id-oficina1
   ```

2. Subir o ambiente Airflow local:
   ```bash
   astro dev start
   ```
   Isso pode levar alguns minutos na primeira vez (download das imagens Docker).

3. Abrir a interface do Airflow no navegador:
   ```
   http://localhost:8080
   ```
   Login padrão: `admin` / `admin`

4. Localizar a DAG `enem_idhm_pipeline` na lista, ativá-la e disparar uma
   execução manual (botão "Trigger DAG").

5. Acompanhar a execução na Grid View / Graph View, e abrir os logs de cada
   tarefa para ver as mensagens impressas (`print`) pelo pipeline.

## Ao final da aula
```bash
astro dev stop
```
