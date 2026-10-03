# Flujos de trabajo para el día a día

> **En 30 segundos:** casi todo flujo bueno es el mismo esqueleto: **explorar → planificar → implementar con verificación → revisar el diff → commitear**, con `/clear` entre tareas. Abajo, cinco recetas concretas del stack de datos con los prompts tal cual.

## Qué es / cómo funciona

El esqueleto y cuándo saltear pasos:

| Paso | Herramienta | Saltealo si... |
|---|---|---|
| Explorar | Preguntas directas, `@archivo`, subagent para búsquedas abiertas | Ya sabés exactamente qué archivo y qué cambio |
| Planificar | Plan mode (`Shift+Tab` o `/plan`), `Ctrl+G` para editar el plan | El cambio entra en una frase (renombre, typo, una línea) |
| Implementar | Modo `default` o `acceptEdits` | — |
| Verificar | Tests, `dbt build`, dry run, `airflow dags test` | Nunca |
| Revisar | `/diff`, `/code-review`, subagent revisor | Nunca para algo que va a prod |
| Commitear | "commiteá con un mensaje que explique el porqué" | — |

Regla práctica para el plan: si al leer el pedido en voz alta hay más de una forma razonable de resolverlo, planeá primero.

## Cómo se usa

Antes de cualquier receta: rama nueva, sesión limpia.

```bash
git switch -c fix/duplicados-ventas
claude -n duplicados-ventas
```

### 1. Onboarding a un repo que no conocés

```text
Explicame este repo como si fuera mi primer día: qué hace, cómo está organizado,
de dónde vienen los datos y adónde van, cómo se corren los tests. No modifiques nada.
```

Seguí con preguntas puntuales ("¿qué DAG escribe en `raw.pagos`?", "¿por qué `fct_ventas` es incremental?"). Cuando entiendas el repo: `/init` para generar un `CLAUDE.md` base y podalo a mano. Ideal en plan mode: lee todo y no toca nada.

### 2. Bugfix con test primero

```text
En fct_ventas hay order_id duplicados desde el 3/10 (ver query abajo).
1. Escribí un test singular en tests/ que reproduzca el problema y mostrame que falla.
2. Encontrá la causa (sospecho del join con stg_pagos, pero verificalo).
3. Arreglalo sin DISTINCT y mostrame que el test pasa con
   dbt build --select fct_ventas+ --target dev.
```

Si a la segunda corrección sigue errado: `/clear` y reescribí el prompt con lo aprendido.

### 3. Nuevo modelo dbt

Con la skill [`dbt-nuevo-modelo`](../ejemplos/skills/dbt-nuevo-modelo/SKILL.md) instalada:

```text
/dbt-nuevo-modelo stg_crm__clientes staging
```

Sin la skill, el mismo pedido explícito: fuente, grano, PK, materialización, tests, y "validá con `dbt compile` + dry run, no corras `dbt run`". Cerrá con `@agent-revisor-dbt revisá stg_crm__clientes`.

### 4. Revisar un PR

```text
Revisá el PR 142 (gh pr diff 142). Enfocate en correctitud de los datos:
granularidad, joins que multiplican filas, filtros de partición, tests faltantes.
Ignorá estilo. Para cada hallazgo: archivo:línea, qué se rompe y cómo arreglarlo.
```

Alternativas: `/code-review 142` (subagent con contexto limpio), `/security-review` para la rama actual. Si tenés el MCP de GitHub, Claude puede dejar los comentarios en el PR, pero que lo haga después de que vos leas los hallazgos.

### 5. Debug de un DAG que falló

```text
El DAG ingesta_ventas falló anoche en la task cargar_bq. Log abajo.
Usá un subagent para leer el DAG, el SQL de la task y los helpers de dags/common que use,
y devolveme: causa más probable, evidencia, y cómo reproducirlo con
airflow tasks test. No cambies nada todavía.

<pegá acá el log de Composer>
```

Después: test que reproduzca → fix → `uv run pytest tests/test_dag_integrity.py` → diff. Caso completo en [casos de uso](../casos-de-uso/investigar-fallo-dag-airflow.md).

## Ejemplo

Una tarde típica con tres tareas, sin arrastrar contexto:

```text
> [tarea 1] fix de duplicados con test primero (receta 2)
> commiteá con un mensaje que explique la causa
> /rename fix-duplicados-ventas
> /clear
> [tarea 2] /dbt-nuevo-modelo fct_cobranzas marts
> @agent-revisor-dbt revisá fct_cobranzas
> /clear
> [tarea 3] /btw ¿qué hacía require_partition_filter?   ← no ensucia el historial
```

## Trucos y errores comunes

- **Contexto completo de entrada**: log real, archivo con `@`, qué ya probaste. Ahorra vueltas.
- **Pasos verificables**: un modelo, `dbt build`, el siguiente. Corregir después de un paso chico es barato.
- **`Esc` apenas ves que se desvía**; `Esc Esc` / `/rewind` para volver. Los checkpoints no cubren lo que cambió un comando de Bash: para eso, git.
- **Exploración en paralelo**: "en paralelo, con subagents: ..." cuando las preguntas no dependen entre sí. Para trabajar en dos ramas a la vez: `claude -w nombre` ([15](15-paralelismo-y-worktrees.md)).
- **Spec para lo grande**: que te entreviste, escriba `SPEC.md`, `/clear`, e implemente otra sesión leyendo la spec.
- **Tareas repetitivas → skill**. Si escribiste el mismo prompt largo tres veces, es una skill ([10](10-skills.md)).
- **Autonomía según confianza**: `acceptEdits` en un repo que conocés y con buena allowlist; `default` en uno nuevo.
- **"Compiló" no es "está bien"**: cerrá el loop con la verificación real y el diff.

## Ver también

- [Buenas prácticas](../buenas-practicas/README.md) — el porqué de cada paso.
- [09 — Plan mode y checkpoints](09-plan-mode-y-checkpoints.md) · [05 — Contexto](05-contexto.md) · [11 — Subagents](11-subagents.md) · [16 — Automatización](16-automatizacion.md)
- [Casos de uso](../casos-de-uso/README.md) · [Ejemplos](../ejemplos/README.md)
