# CLAUDE.md — proyecto dbt sobre BigQuery

## Comandos
- Instalar dependencias: `uv sync && dbt deps`
- Validar sin tocar BigQuery: `dbt parse` y `dbt compile --select <modelo>`
- Estimar costo de una query: `bq query --dry_run --use_legacy_sql=false "$(cat target/compiled/<ruta>.sql)"` (poné `--dry_run` primero, así matchea la allowlist)
- Correr en dev: `dbt build --select <modelo> --target dev` (nunca `--target prod` desde local)
- Lint SQL: `sqlfluff lint models/`

## Estructura
- `models/staging/<fuente>/stg_<fuente>__<entidad>.sql` — 1:1 con la fuente, solo renombres y casteos.
- `models/intermediate/int_<entidad>_<verbo>.sql` — lógica intermedia, no se expone.
- `models/marts/<dominio>/fct_*.sql` y `dim_*.sql` — lo que consume Looker Studio.
- Cada modelo tiene su entrada en el `_<carpeta>__models.yml` de la misma carpeta.

## Convenciones
- Siempre `ref()` / `source()`, nunca `proyecto.dataset.tabla` hardcodeado.
- Nada de `SELECT *` en marts.
- Tablas > 1 GB: `partition_by` por fecha + `cluster_by` por las columnas de filtro más usadas.
- Toda primary key lleva tests `unique` + `not_null`.
- Incrementales: `materialized='incremental'`, `incremental_strategy='merge'`, `unique_key` explícita y filtro `{% if is_incremental() %}` sobre la columna de partición.

## Cosas que no son obvias
- El dataset de dev es `dbt_<usuario>`; prod lo escribe solo el job de Composer.
- `require_partition_filter=true` en las tablas de eventos: cualquier query sin filtro de fecha falla.
- Antes de proponer un cambio de materialización, mostrá el dry run (bytes procesados) antes y después.

## Al terminar una tarea
1. `dbt build --select <modelo>+ --target dev` pasa en verde.
2. Mostrame el diff y los bytes del dry run.
