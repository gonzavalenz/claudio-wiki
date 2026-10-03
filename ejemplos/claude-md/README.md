# Ejemplos de `CLAUDE.md`

| Archivo | Para qué repo |
|---|---|
| [`dbt-bigquery.md`](dbt-bigquery.md) | Proyecto dbt que materializa en BigQuery |
| [`airflow-composer.md`](airflow-composer.md) | Repo de DAGs de Airflow que corre en Cloud Composer |

Están guardados con otro nombre a propósito: un archivo llamado `CLAUDE.md` dentro de este repo lo cargaría Claude Code cada vez que trabaja en esta carpeta.

## Cómo usarlos

```bash
cp ejemplos/claude-md/dbt-bigquery.md ~/repos/mi-proyecto-dbt/CLAUDE.md
```

Después adaptalo: nombres de datasets, comandos reales, gotchas de tu equipo. Si arrancás de cero, también podés correr `/init` en el repo y usar estos como referencia de qué dejar y qué sacar.

## Qué va y qué no va en un `CLAUDE.md`

| Sí | No |
|---|---|
| Comandos que Claude no puede adivinar (cómo testear, cómo hacer un dry run) | Lo que se deduce leyendo el código |
| Convenciones que se apartan del default | "Escribí código limpio" y obviedades parecidas |
| Gotchas reales (filtros de partición obligatorios, dataset de dev) | Docs largas (linkealas o pasalas a una skill) |
| Qué significa "terminado" (qué tiene que pasar en verde) | Cosas que cambian todas las semanas |

La prueba de cada línea: *¿si la saco, Claude se equivoca?* Si no, afuera. Apuntá a menos de 200 líneas; los procedimientos de varios pasos van como [skill](../skills/README.md).

Ver [06 — Memoria](../../docs/06-memoria.md).
