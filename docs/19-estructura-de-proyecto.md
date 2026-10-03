# Estructura de proyecto para sacarle el jugo

> **En 30 segundos:** Claude Code funciona en cualquier repo, pero rinde mucho más si el repo le dice cómo testear, qué convenciones seguir y qué no tocar. Eso vive en `CLAUDE.md`, `.claude/` y `.mcp.json`: se commitea para el equipo, y lo personal queda afuera.

## Qué es / cómo funciona

Al abrir una sesión, Claude Code lee la configuración en capas:

1. **Memoria** (`CLAUDE.md`): se carga entera al arrancar. Los `CLAUDE.md` de subcarpetas se cargan cuando Claude lee archivos de esa carpeta.
2. **Settings** (`.claude/settings.json` y compañía): permisos, hooks, variables de entorno. Se combinan por precedencia y las listas se suman.
3. **Extensiones**: skills, subagents, servers MCP. De cada skill y subagent solo se carga la `description` hasta que se usa.

Lo que hace rendir a un repo, además de esa config:

- **Comandos de test/lint estándar y que funcionen** (`uv run pytest`, `dbt build --select ...`). Si una persona no puede correr los tests siguiendo el README, Claude tampoco.
- **Convenciones consistentes**: un repo con un solo estilo se "lee" mejor que uno con tres mezclados.
- **Una forma de verificar**: tests, `dbt build`, un dry run. Es lo que le permite a Claude saber si terminó.

## Cómo se usa

```
mi-repo-dbt/
├── CLAUDE.md                    # contexto permanente (corto)
├── CLAUDE.local.md              # tu contexto personal de este repo  (gitignored)
├── .mcp.json                    # servers MCP del equipo
├── .claude/
│   ├── settings.json            # permisos + hooks del equipo
│   ├── settings.local.json      # tus overrides                      (gitignored)
│   ├── rules/
│   │   └── sql-bigquery.md      # reglas con paths: ["models/**/*.sql"]
│   ├── hooks/
│   │   ├── guardia-bigquery.sh
│   │   └── formatear-python.sh
│   ├── agents/
│   │   ├── revisor-dbt.md
│   │   └── explorador-lineage.md
│   └── skills/
│       └── dbt-nuevo-modelo/
│           └── SKILL.md
├── models/ ...
└── tests/ ...
```

| Qué | Dónde | Cuándo se carga |
|---|---|---|
| Contexto que aplica siempre | `CLAUDE.md` | Cada sesión, entero |
| Reglas de un tipo de archivo o carpeta | `.claude/rules/*.md` con `paths:` | Cuando Claude lee/edita un archivo que matchea |
| Procedimiento de varios pasos | `.claude/skills/<n>/SKILL.md` | Solo la `description`; el resto al invocarla |
| Rol especializado con su propio contexto | `.claude/agents/<n>.md` | Solo la `description`; corre aparte al delegar |
| Algo obligatorio | Hook en `.claude/settings.json` | Siempre, en el evento configurado |
| Acceso a sistemas externos | `.mcp.json` | Al arrancar (con aprobación la primera vez) |

Todo esto se puede copiar armado desde [`ejemplos/`](../ejemplos/README.md) (hay un "kit mínimo" de 6 comandos).

## Ejemplo

Regla con alcance para que no viva en el `CLAUDE.md` principal, en `.claude/rules/sql-bigquery.md`:

```markdown
---
paths:
  - "models/**/*.sql"
  - "sql/**/*.sql"
---

# SQL en BigQuery
- Filtrá siempre por la columna de partición en tablas de eventos (`require_partition_filter`).
- `SAFE_CAST` en vez de `CAST` en staging.
- Nada de `SELECT *` fuera de staging.
```

Y en un monorepo con dbt y DAGs, un `CLAUDE.md` por subproyecto:

```
data-platform/
├── CLAUDE.md            # lo común: cómo correr tests, rama, convenciones de PR
├── dbt/CLAUDE.md        # se carga cuando Claude trabaja dentro de dbt/
└── dags/CLAUDE.md       # se carga cuando Claude trabaja dentro de dags/
```

## Trucos y errores comunes

- **`CLAUDE.md` gigante**: si tiene cientos de líneas, Claude ignora la mitad. Movelo a `rules/` con `paths:` o a skills. `/context` muestra cuánto pesa.
- **Mezclar contexto permanente con la tarea de hoy**: "hoy migramos X" no va en `CLAUDE.md`; va en el prompt o en un `SPEC.md` que se borra al terminar.
- **Convenciones que solo están en la cabeza del equipo**: si no está escrito, Claude no lo sabe (y una persona nueva tampoco).
- **No versionar `.claude/`**: cada uno rearma lo mismo y el agente se comporta distinto según quién lo use. Commiteá todo menos `settings.local.json` y `CLAUDE.local.md`.
- **Secretos en `.mcp.json`**: usá `${VAR}` y que cada uno exporte la suya.
- **Archivos llamados `CLAUDE.md` en carpetas de ejemplos o fixtures**: se cargan cuando Claude entra ahí. Por eso los ejemplos de esta wiki tienen otro nombre.
- **`.claudeignore` no existe**: para que Claude no lea algo, `deny` con `Read(...)` en settings.
- **Probá la config**: `/permissions`, `/hooks`, `/skills`, `/mcp` y `/context` muestran qué cargó y de dónde. `claude doctor` valida los settings.

## Ver también

- [06 — Memoria](06-memoria.md) · [07 — Permisos](07-permisos.md) · [10 — Skills](10-skills.md) · [11 — Subagents](11-subagents.md) · [12 — Hooks](12-hooks.md) · [13 — MCP](13-mcp.md) · [14 — Plugins](14-plugins.md)
- [Ejemplos copiables](../ejemplos/README.md) · [Cheatsheet](cheatsheet.md)
