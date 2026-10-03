# Memoria: que no haya que reexplicar el proyecto cada vez

> **En 30 segundos:** cada sesión arranca sin recordar las anteriores. Dos mecanismos cargan conocimiento entre sesiones: **`CLAUDE.md`** (instrucciones que escribís vos, se cargan siempre) y **auto memory** (notas que Claude guarda solo a partir de tus correcciones). Un buen `CLAUDE.md` es corto (menos de 200 líneas), concreto y solo tiene lo que Claude no puede deducir leyendo el código.

## `CLAUDE.md` vs. auto memory

| | `CLAUDE.md` | Auto memory |
|---|---|---|
| Quién lo escribe | Vos | Claude |
| Qué tiene | Instrucciones y reglas | Aprendizajes: tus preferencias, correcciones, contexto del proyecto |
| Alcance | Organización, usuario, proyecto o local | Por repositorio (compartida entre worktrees), solo en tu máquina |
| Se carga | Entero, en cada sesión | `MEMORY.md`: primeras 200 líneas o 25 KB |
| Dónde vive | En el repo o en `~/.claude/` | `~/.claude/projects/<proyecto>/memory/` |

Las dos son **contexto, no configuración obligatoria**: Claude intenta seguirlas, pero no hay garantía. Si algo *tiene* que pasar siempre (o nunca), usá un [hook](12-hooks.md) o una regla de [permisos](07-permisos.md).

## Jerarquía de `CLAUDE.md`

| Alcance | Ruta | Para qué | Se comparte con |
|---|---|---|---|
| Organización (managed) | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md` · Linux/WSL: `/etc/claude-code/CLAUDE.md` | Políticas de la empresa, lo gestiona IT | Toda la organización |
| Usuario | `~/.claude/CLAUDE.md` | Tus preferencias en todos los proyectos | Solo vos |
| Proyecto | `./CLAUDE.md` o `./.claude/CLAUDE.md` | Convenciones del repo, comandos, arquitectura | El equipo, vía git |
| Local | `./CLAUDE.local.md` (agregalo al `.gitignore`) | Tus notas personales de este repo: tu dataset de dev, tu perfil de dbt | Solo vos |
| Subcarpetas | `models/marts/CLAUDE.md`, etc. | Reglas de una parte del repo | El equipo |

Cómo se cargan:

- Al arrancar, carga los `CLAUDE.md` y `CLAUDE.local.md` de la carpeta actual **y de todas las carpetas de arriba**. No se pisan: **se concatenan**, de la raíz hacia abajo, así que lo más cercano a donde lanzaste se lee último.
- Los de **subcarpetas** se cargan **bajo demanda**, cuando Claude lee archivos de esa subcarpeta.
- Los comentarios HTML (`<!-- nota para humanos -->`) se eliminan antes de mandarlos al modelo: sirven para notas de mantenimiento sin gastar tokens.

### `AGENTS.md`

Si el repo tiene `AGENTS.md` (el formato que usan otros agentes) y **no** tiene `CLAUDE.md`, Claude Code lee el `AGENTS.md`. Si hay los dos, por defecto lee solo `CLAUDE.md`. La forma más simple de compartir un único archivo entre agentes es la que usa este mismo repo: un `CLAUDE.md` que solo importa el `AGENTS.md`.

```markdown
# CLAUDE.md

@AGENTS.md
```

## Imports con `@`

Un `CLAUDE.md` puede importar otros archivos con `@ruta`:

```markdown
Ver @README.md para la descripción del proyecto.

# Convenciones
- SQL: @docs/convenciones-sql.md
- Git: @docs/git.md
```

- Rutas relativas al archivo que importa (no a la carpeta actual). También absolutas o con `~`.
- Hasta 4 niveles de imports anidados.
- Un `@algo` dentro de backticks (`` `@README` ``) **no** se importa.
- Los imports se cargan al arrancar: **ordenan, pero no ahorran contexto**.
- La primera vez que un `CLAUDE.md` de proyecto importa algo fuera del repo, Claude Code pide aprobación.

## Rules: instrucciones por tipo de archivo

Para repos grandes, partí las instrucciones en `.claude/rules/*.md`. Con `paths:` en el frontmatter, la regla se carga **solo** cuando Claude trabaja con archivos que matchean:

```markdown
---
paths:
  - "models/staging/**/*.sql"
---

# Reglas de staging
- Un modelo staging por tabla fuente, nombre `stg_<fuente>__<tabla>`.
- Solo renombrar, castear y limpiar. Nada de joins.
```

Las rules sin `paths:` se cargan siempre, como el `CLAUDE.md`.

## Auto memory

Claude guarda notas solo cuando algo le parece útil para el futuro: tu rol y preferencias, correcciones que le hiciste, decisiones del proyecto que no están en el código, dónde encontrar cosas externas (un tablero, un tracker).

- Está **activada por defecto** en sesiones locales.
- Se activa/desactiva desde `/memory` (guarda `autoMemoryEnabled` en `~/.claude/settings.json`), o con `"autoMemoryEnabled": false` en los settings de un proyecto.
- Son archivos Markdown comunes: podés leerlos, editarlos o borrarlos.
- No se comparte entre máquinas ni con la nube.

Cuando le decís "acordate de que en este repo usamos `uv`, no `pip`", va a la **auto memory**. Si querés que vaya al **`CLAUDE.md`** (y que lo vea el equipo), decilo: "agregá esto al CLAUDE.md".

## `/memory` y `/init`

| Comando | Qué hace |
|---|---|
| `/init` | Genera un `CLAUDE.md` inicial analizando el repo. Si ya existe, propone mejoras |
| `/memory` | Lista los `CLAUDE.md` de usuario y proyecto (aunque no existan todavía), abre el que elijas en tu editor, activa/desactiva la auto memory y abre su carpeta |
| `/context` | Muestra qué archivos de memoria se cargaron de verdad en esta sesión |
| `/doctor prompt-audit` | Revisa tus `CLAUDE.md`, rules y skills buscando instrucciones contradictorias, desactualizadas o que referencian archivos que no existen |

## Qué poner y qué no

| Poner | No poner |
|---|---|
| Comandos que no se adivinan (`dbt build --select state:modified+ --defer --state prod-artifacts/`) | Lo que se deduce leyendo el código (estructura de carpetas, lista de dependencias) |
| Convenciones que difieren del default | Convenciones estándar que el modelo ya conoce ("escribí código limpio") |
| Cómo testear y con qué | Documentación larga de APIs (linkeala) |
| Etiqueta del repo: ramas, PRs, commits | Información que cambia seguido |
| Decisiones de arquitectura propias | Tutoriales y explicaciones largas |
| Trampas no obvias del entorno (variables requeridas, proyectos de GCP) | Descripción archivo por archivo |
| Qué **nunca** hacer (y por qué) | Historial de lo que hiciste en una tarea (eso va en git) |

Para cada línea preguntate: *"¿si la saco, Claude se equivocaría?"*. Si no, sacala. Un `CLAUDE.md` inflado hace que ignore justo las reglas importantes.

## Ejemplo: `CLAUDE.md` para un repo dbt

```markdown
# dbt-analytics

Proyecto dbt sobre BigQuery. Capas: staging → intermediate → marts.

## Comandos
- Instalar deps: `uv sync && dbt deps`
- Build de lo modificado: `dbt build --select state:modified+ --defer --state prod-artifacts/`
- Un modelo y sus tests: `dbt build --select <modelo>`
- Lint SQL: `sqlfluff lint models/`

## Convenciones
- Nombres: `stg_<fuente>__<tabla>`, `int_<entidad>_<verbo>`, `fct_<proceso>`, `dim_<entidad>`.
- Toda PK tiene tests `unique` y `not_null` en el `schema.yml` del modelo.
- Tablas de más de 1 GB: `materialized='incremental'` con `partition_by` por fecha.
- Fuentes solo vía `source()`, nunca nombres de tabla hardcodeados.

## Entorno
- Target dev escribe en el dataset `dbt_<usuario>` del proyecto `analytics-dev`. Nunca correr con `--target prod`.
- Antes de una query exploratoria con `bq`, usar `--dry_run` para ver bytes procesados.

## Git
- Ramas `feat/`, `fix/`. PR contra `main`, nunca push directo.

## Compact Instructions
Al compactar, conservá la lista de modelos modificados y los comandos de test usados.
```

## Trucos y errores comunes

- **Cuándo agregar algo**: cuando Claude comete el mismo error dos veces, cuando un code review encuentra algo que "tendría que haber sabido", o cuando te encontrás reescribiendo la misma aclaración en cada sesión.
- **Si ignora una regla**, probablemente el archivo es muy largo o la regla es vaga. "Usá 2 espacios de indentación" funciona; "formateá bien" no. Si una sola regla se saltea siempre, un `IMPORTANTE` en esa línea ayuda (si marcás todo, no destaca nada).
- **Reglas contradictorias** entre archivos (usuario vs. proyecto vs. subcarpeta) hacen que elija una al azar. Revisalos cada tanto o corré `/doctor prompt-audit`.
- **Procedimientos de varios pasos no van en `CLAUDE.md`**: van en una [skill](10-skills.md), que se carga solo cuando hace falta. Regla: si aplica *siempre*, `CLAUDE.md`; si aplica *a veces*, skill o rule con `paths:`.
- **`CLAUDE.local.md` en un worktree** solo existe en ese worktree. Para preferencias personales compartidas entre worktrees, importá un archivo de tu home: `@~/.claude/mis-notas-dbt.md`.
- **Tener un `CLAUDE.local.md` hace que deje de leer el `AGENTS.md`** si el repo dependía solo de este. Importá el `AGENTS.md` desde un `CLAUDE.md`.
- **Versioná el `CLAUDE.md` del proyecto** y tratalo como código: revisalo en los PRs.

## Ver también

- [Contexto](05-contexto.md) — qué sobrevive a `/compact`
- [Skills](10-skills.md) — para procedimientos que no tienen que estar siempre cargados
- [Hooks](12-hooks.md) — para reglas que tienen que cumplirse sí o sí
- [Estructura de proyecto](19-estructura-de-proyecto.md)
- [Ejemplos copiables](../ejemplos/)
