---
name: dbt-nuevo-modelo
description: Crea un modelo dbt nuevo (SQL + YAML con tests) siguiendo las convenciones del proyecto y lo valida con compile y dry run en BigQuery. Usar cuando piden "creá un modelo", "nuevo modelo de staging/mart", "armá el stg de la tabla X".
argument-hint: "[nombre_modelo] [staging|intermediate|marts]"
allowed-tools:
  - Bash(dbt parse *)
  - Bash(dbt compile *)
  - Bash(dbt ls *)
  - Bash(bq show *)
  - Bash(bq query --dry_run *)
---

# Nuevo modelo dbt: $0 (capa: $1)

Si falta el nombre o la capa, preguntalos antes de seguir.

## 1. Entender antes de escribir

- Si es staging: identificá el `source` en los `_*__sources.yml`. Si no existe, proponé la entrada y mostrámela antes de crearla. Mirá el esquema real con `bq show --schema --format=prettyjson <proyecto>:<dataset>.<tabla>`.
- Si es intermediate/marts: listá los `ref()` que vas a usar y confirmá que existen con `dbt ls --select <modelo>`.
- Mirá 1–2 modelos existentes de la misma capa y copiá su estilo (CTEs, orden de columnas, nombres).
- Preguntá: grano de la tabla (una fila por qué), primary key, y si se filtra por fecha.

## 2. Escribir

- SQL en `models/$1/.../$0.sql` con CTEs: `source`/`ref` arriba → transformaciones → `final` → `select * from final`.
- `config()`:
  - staging → `materialized='view'`
  - marts grandes → `materialized='table'` o `'incremental'`, con `partition_by={'field': '<fecha>', 'data_type': 'date'}` y `cluster_by=[...]`
  - incremental → `unique_key`, `incremental_strategy='merge'` y `{% if is_incremental() %}` filtrando la columna de partición
- YAML en el `_*__models.yml` de la carpeta: `description` del modelo, columnas con descripción, y tests `unique` + `not_null` en la PK.

## 3. Validar (no materializar)

1. `dbt parse`
2. `dbt compile --select $0`
3. `bq query --dry_run --use_legacy_sql=false "<SQL de target/compiled/...>"` → reportá los bytes procesados.

No corras `dbt run` ni `dbt build`: eso lo decido yo.

## 4. Entregar

- Lista de archivos creados/modificados.
- Bytes del dry run.
- El comando para materializar en dev: `dbt build --select $0 --target dev`.
