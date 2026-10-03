# CLAUDE.md — repo de DAGs de Airflow (Cloud Composer)

## Comandos
- Tests: `uv run pytest tests/ -q` (incluye `tests/test_dag_integrity.py`, que importa todos los DAGs)
- Lint/format: `ruff check . && ruff format .`
- Probar un DAG local sin scheduler: `airflow dags test <dag_id> 2024-01-01`
- Probar una task: `airflow tasks test <dag_id> <task_id> 2024-01-01`
- Errores de import en Composer: `gcloud composer environments run <env> --location <region> dags list-import-errors`

## Estructura
- `dags/<dominio>/<dag_id>.py` — un DAG por archivo, `dag_id` igual al nombre del archivo.
- `dags/common/` — operadores y helpers compartidos. Cambios acá afectan a todos los DAGs: avisame antes.
- `sql/<dag_id>/*.sql` — queries que usan los `BigQueryInsertJobOperator`.

## Convenciones
- Nada de lógica pesada a nivel de módulo (se ejecuta en cada parseo del scheduler): conexiones, queries y `Variable.get()` van dentro de las tasks o como templates `{{ var.value.x }}`.
- `catchup=False` salvo que el DAG sea de backfill explícito.
- Toda task que escribe en BigQuery tiene que ser idempotente (`WRITE_TRUNCATE` sobre la partición o `MERGE`).
- Fechas: usar `{{ ds }}` / `data_interval_start`, nunca `datetime.now()`.
- Secrets: siempre por Connections/Secret Manager, nunca en el código.

## Cosas que no son obvias
- Composer corre Airflow 2.x: no usar APIs de Airflow 3.
- El bucket de DAGs se sincroniza por CI al mergear a `main`; no subas archivos a mano con `gsutil`.

## Al terminar una tarea
1. `uv run pytest tests/ -q` en verde (el test de integridad tiene que pasar).
2. `ruff check .` sin errores.
