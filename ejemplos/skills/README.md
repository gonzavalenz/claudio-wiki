# Skills de ejemplo

Cada subcarpeta es una skill completa, lista para copiar a `.claude/skills/<nombre>/` (proyecto) o `~/.claude/skills/<nombre>/` (personal).

```bash
cp -r ejemplos/skills/dbt-nuevo-modelo .claude/skills/
```

| Skill | Para qué sirve | Se invoca |
|---|---|---|
| [`dbt-nuevo-modelo/`](dbt-nuevo-modelo/SKILL.md) | Crea un modelo dbt (SQL + YAML + tests) con las convenciones del proyecto y lo valida con `dbt compile` + dry run | `/dbt-nuevo-modelo fct_ventas marts` o "creá un modelo de..." |
| [`revision-de-diffs/`](revision-de-diffs/SKILL.md) | Checklist para revisar un diff antes de commitear | "revisá esto antes de commitear" |

## Anatomía de una skill (campos verificados)

```yaml
---
name: dbt-nuevo-modelo          # nombre del /comando; si falta, usa el de la carpeta
description: Qué hace y cuándo usarla   # lo que lee Claude para decidir si la carga
argument-hint: "[nombre] [capa]"        # ayuda en el autocompletado
allowed-tools:                          # tools sin pedir permiso mientras corre
  - Bash(dbt compile *)
disable-model-invocation: true          # opcional: solo vos la disparás con /nombre
---
Instrucciones en Markdown. $ARGUMENTS = todo lo que escribiste después del comando;
$0, $1... = cada argumento por posición.
```

Otros campos útiles: `when_to_use` (frases disparadoras extra), `context: fork` + `agent: Explore` (correrla en un subagent), `model`, `effort`, `paths` (cargarla solo al tocar ciertos archivos). Los nombres de campo van con guiones y tienen que coincidir exacto: un campo mal escrito se ignora sin error.

## Trucos

- La `description` decide si Claude la usa sola: poné primero el caso de uso y las frases con las que la pedirías.
- `` !`comando` `` en el cuerpo se ejecuta **antes** de mandar la skill y se reemplaza por su salida (ej. `` !`git diff --stat` ``): Claude recibe datos, no instrucciones de ir a buscarlos.
- Una vez cargada, la skill queda en contexto el resto de la sesión: cuanto más corta, más barata.
- Los viejos `.claude/commands/<nombre>.md` siguen funcionando y aceptan el mismo frontmatter, pero una skill en carpeta puede traer archivos de soporte (plantillas, scripts).
- `/skills` lista las disponibles; `/reload-skills` las relee si las editaste en la sesión.

Ver [10 — Skills](../../docs/10-skills.md) y la regla de [buenas prácticas](../../buenas-practicas/README.md#claudemd) sobre qué va en una skill y qué en `CLAUDE.md`.
