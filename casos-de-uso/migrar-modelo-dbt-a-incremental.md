# Migrar un modelo dbt de vista a incremental

> Caso simulado con detalle suficiente para reproducirlo. Stack: dbt Core + BigQuery, corrido desde Composer.

**Contexto:** equipo de data engineering. `fct_eventos_app` es una `view` sobre `stg_app__eventos` (≈ 2 TB, crece 15 GB/día). Tres dashboards de Looker Studio la consultan varias veces por hora.

**Problema:** cada refresh de dashboard escanea la tabla entera: la factura de BigQuery del dominio se triplicó en dos meses y los dashboards tardan más de un minuto. Hay que pasarlo a `incremental` sin cambiar los resultados ni romper a los consumidores.

## Cómo se resolvió con Claude Code

**Preparación** (una vez): `CLAUDE.md` de [`ejemplos/claude-md/dbt-bigquery.md`](../ejemplos/claude-md/dbt-bigquery.md), permisos de [`ejemplos/settings`](../ejemplos/settings/README.md) (dry run permitido, `dbt build` con confirmación) y la [guardia de BigQuery](../ejemplos/hooks/README.md).

```bash
git switch -c perf/fct-eventos-incremental
claude -n eventos-incremental --permission-mode plan
```

### 1. Explorar y medir (modo plan, sin tocar nada)

```text
Quiero pasar @models/marts/app/fct_eventos_app.sql de view a incremental.
Antes de proponer nada:
1. Usá el subagent explorador-lineage para listar todo lo que depende de este modelo
   (modelos y exposures).
2. Decime el grano real (¿una fila por event_id?) y verificalo con una query
   de conteo vs. conteo distinto — solo con --dry_run para ver el costo, y
   pasame la query para que la corra yo.
3. Hacé un dry run del SQL compilado actual y decime cuántos bytes procesa.
```

Lo que devolvió: 2 modelos downstream + 3 exposures; grano `event_id`; **1,9 TB por consulta**. Corrí yo la query de unicidad (con `!` en el prompt) y encontró 0,02 % de `event_id` duplicados por reintentos del SDK. Dato clave que no estaba en ningún lado.

### 2. Plan

```text
Proponé el plan para la migración. Restricciones:
- partition_by event_date (day), cluster_by [user_id, event_name]
- incremental_strategy merge con unique_key event_id, deduplicando en el modelo
  (quedarse con el último ingested_at)
- ventana de reproceso de 3 días para eventos tardíos
- nada de cambios en el contrato de columnas
- cómo validamos que da lo mismo que la view
```

Revisé el plan con `Ctrl+G`, le agregué "sumá `require_partition_filter=true`" y lo aprobé.

### 3. Implementar con verificación

Claude escribió:

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='event_id',
    partition_by={'field': 'event_date', 'data_type': 'date', 'granularity': 'day'},
    cluster_by=['user_id', 'event_name'],
    require_partition_filter=true
) }}

with eventos as (
    select *
    from {{ ref('stg_app__eventos') }}
    {% if is_incremental() %}
    where event_date >= date_sub(current_date(), interval 3 day)
    {% endif %}
),

dedup as (
    select *
    from eventos
    qualify row_number() over (partition by event_id order by ingested_at desc) = 1
)

select ... from dedup
```

Más un test singular `tests/assert_fct_eventos_app_igual_a_view.sql` que compara conteos y sumas por día contra la view vieja (renombrada temporalmente a `fct_eventos_app_legacy`) para los últimos 30 días.

```text
Corré dbt build --select fct_eventos_app+ --target dev --full-refresh
y después el test de paridad. Mostrame resultados y el dry run de una
consulta típica de dashboard (último 7 días) contra la tabla nueva.
```

`dbt build` pidió confirmación (está en `ask`), lo aprobé. Paridad: OK en 30/30 días. Consulta de dashboard: **1,9 TB → 41 GB**.

### 4. Revisión y cierre

```text
@agent-revisor-dbt revisá fct_eventos_app
```

Marcó un bloqueante: uno de los dashboards filtraba por `event_timestamp`, no por `event_date`, y con `require_partition_filter=true` iba a fallar. Se ajustó la fuente de datos del dashboard (filtro por `event_date`) antes de mergear. Después: commit, PR, y `/clear`.

## Resultado / aprendizaje

- **Funcionó:** medir antes (dry run) y validar después (test de paridad) convirtió una migración riesgosa en un cambio verificable. Costo por refresh −98 %.
- **Lo que no hubiera visto sin explorar:** los duplicados del SDK (un `merge` sin dedup hubiera fallado en la primera corrida incremental) y el dashboard que filtraba por timestamp.
- **Lo que haría distinto:** pedir el chequeo de exposures *antes* de sugerir `require_partition_filter`. Lo agregué al `CLAUDE.md` como gotcha.
- **Patrón reutilizable:** modo plan + subagent de lineage + test de paridad contra la versión vieja. Vale para cualquier cambio de materialización.

Relacionado: [20 — Flujos de trabajo](../docs/20-flujos-de-trabajo.md) · [09 — Plan mode y checkpoints](../docs/09-plan-mode-y-checkpoints.md) · [11 — Subagents](../docs/11-subagents.md) · [21 — Costos](../docs/21-costos.md)
