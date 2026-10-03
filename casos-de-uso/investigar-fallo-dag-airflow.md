# Investigar por qué falló un DAG de Airflow anoche

> Caso simulado con detalle suficiente para reproducirlo. Stack: Cloud Composer (Airflow 2), BigQuery, repo de DAGs en Python.

**Contexto:** a las 8:00 llega la alerta: `ingesta_pagos` falló en la task `cargar_bq` a las 03:12. Los dashboards de cobranzas muestran datos de antes de ayer. Nadie tocó ese DAG en semanas.

**Problema:** encontrar la causa rápido, arreglarla sin romper otros DAGs y recuperar el día que faltó sin duplicar datos.

## Cómo se resolvió con Claude Code

**Preparación:** `CLAUDE.md` de [`ejemplos/claude-md/airflow-composer.md`](../ejemplos/claude-md/airflow-composer.md), hook de [ruff](../ejemplos/hooks/README.md) y permisos con `gcloud composer *` en `ask`.

```bash
git switch -c fix/ingesta-pagos-schema
claude -n fallo-ingesta-pagos
```

### 1. Darle la evidencia real, no un resumen

Bajé el log de la task desde la UI de Airflow a un archivo y filtré lo relevante antes de pegarlo (un log de Composer entero se come el contexto):

```bash
grep -n -E "ERROR|Traceback|Exception" ~/Downloads/cargar_bq.log | head -40
```

```text
El DAG @dags/pagos/ingesta_pagos.py falló anoche en la task cargar_bq. Log filtrado abajo.
Usá un subagent para leer el DAG, el SQL que ejecuta esa task, y los helpers de
dags/common/ que use. Devolveme: causa más probable, evidencia (archivo:línea y
línea del log), qué otros DAGs usan el mismo helper, y cómo reproducirlo local.
No cambies nada todavía.

<log filtrado>
google.api_core.exceptions.BadRequest: 400 Provided Schema does not match Table
proyecto:raw.pagos. Field monto has changed type from NUMERIC to STRING
...
```

### 2. Diagnóstico

El subagent volvió con:

- El proveedor empezó a mandar `monto` como string con separador de miles (`"1.234,50"`) en el CSV de anoche.
- `dags/common/gcs_to_bq.py:48` usa `autodetect=True` en el `LoadJobConfig`, así que BigQuery infirió `STRING` y chocó con el esquema de la tabla.
- Otros 4 DAGs usan ese helper con `autodetect=True`: el mismo problema les puede pasar a todos.

Verifiqué el archivo crudo con `!`:

```text
! gcloud storage cat gs://bucket-ingestas/pagos/2024-10-01/pagos.csv | head -3
```

Confirmado.

### 3. Plan y fix con test primero

```text
Modo plan. Quiero:
1. Un test en tests/ que cargue un CSV de muestra con "1.234,50" y falle con el código actual.
2. Esquema explícito para pagos (schema_fields desde un JSON en schemas/pagos.json)
   en vez de autodetect, y parseo del monto en staging, no en la carga.
3. Que el helper acepte schema opcional sin cambiar el comportamiento de los otros 4 DAGs.
4. Cómo recupero el 2024-10-01 sin duplicar (la task tiene que ser idempotente).
```

Plan aprobado. Claude:

- Escribió `tests/test_gcs_to_bq.py` y mostró que fallaba.
- Agregó el parámetro `schema_fields` opcional al helper (default `None` → mismo comportamiento que antes para los otros DAGs).
- Cargó `monto` como `STRING` en `raw.pagos_landing` y movió el parseo a `stg_pagos` con `SAFE_CAST(REPLACE(REPLACE(monto, '.', ''), ',', '.') AS NUMERIC)`.
- Confirmó que la carga usa `WRITE_TRUNCATE` sobre la partición `$20241001`: re-ejecutar es idempotente.

```text
Corré uv run pytest tests/ -q y ruff check . y mostrame el diff completo.
```

Verde. El hook de ruff ya había formateado los `.py` en cada edición.

### 4. Revisión, deploy y backfill

- `/code-review` sobre el diff: señaló que `SAFE_CAST` convierte basura en `NULL` en silencio → se agregó un test dbt `not_null` sobre `monto` en `stg_pagos` para que un formato nuevo falle ruidoso.
- PR, merge, CI sincroniza el bucket de DAGs.
- Backfill: Claude armó el comando y yo lo ejecuté (está en `ask`):
  ```bash
  gcloud composer environments run composer-prod --location us-central1 \
    dags backfill -- -s 2024-10-01 -e 2024-10-01 --reset-dagruns -y ingesta_pagos
  ```

## Resultado / aprendizaje

- **Tiempo:** de alerta a fix mergeado en ~50 minutos, la mayor parte en revisión y CI.
- **Funcionó:** pegar el log *filtrado* y delegar la lectura a un subagent dejó la sesión principal limpia para el fix. Pedir "qué más usa este helper" encontró 4 DAGs con la misma bomba.
- **Regla nueva en `CLAUDE.md`:** "No usar `autodetect=True` en cargas a tablas existentes; esquema explícito en `schemas/`".
- **Lo que haría distinto:** tener un hook o un test de integridad que falle si algún DAG usa `autodetect=True`, en vez de depender de que alguien lo vea en review.
- **Nunca** dejar que Claude corra el backfill solo: es una acción sobre prod, visible para otros. Él arma el comando, vos lo ejecutás.

Relacionado: [20 — Flujos de trabajo](../docs/20-flujos-de-trabajo.md) · [11 — Subagents](../docs/11-subagents.md) · [12 — Hooks](../docs/12-hooks.md) · [Buenas prácticas](../buenas-practicas/README.md)
