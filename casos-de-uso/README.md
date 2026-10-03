# Casos de uso

Escenarios del stack de datos resueltos con Claude Code de punta a punta: contexto, problema, cómo se resolvió (con los prompts y comandos tal cual) y qué se aprendió. Los marcados como *simulados* no son anécdotas reales, pero tienen detalle suficiente para reproducirlos.

| Caso | Qué muestra |
|---|---|
| [Migrar un modelo dbt de vista a incremental](migrar-modelo-dbt-a-incremental.md) | Modo plan, subagent de lineage, dry run antes/después, test de paridad contra la versión vieja |
| [Investigar por qué falló un DAG de Airflow anoche](investigar-fallo-dag-airflow.md) | Pegar evidencia filtrada, diagnóstico con subagent, test primero, backfill idempotente con confirmación humana |

## Cómo sumar uno

Un archivo `.md` por caso (o una subcarpeta si necesita assets), con esta estructura:

```markdown
# Título del caso de uso

**Contexto:** quién, en qué proyecto, con qué objetivo.

**Problema:** qué había que resolver.

## Cómo se resolvió con Claude Code
Pasos, prompts y comandos reales; linkear a `docs/` o `ejemplos/` cuando aplique.

## Resultado / aprendizaje
Qué funcionó, qué no, qué se haría distinto la próxima vez.
```

Si un caso confirma, matiza o contradice alguna regla, actualizá también [buenas prácticas](../buenas-practicas/README.md).
