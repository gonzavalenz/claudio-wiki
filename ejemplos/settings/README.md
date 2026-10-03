# `settings.json` de proyecto para un repo de datos

[`settings.json`](settings.json) es un punto de partida para un repo con dbt + BigQuery + Airflow. Se copia a `.claude/settings.json` y se commitea, así todo el equipo tiene las mismas reglas.

```bash
mkdir -p .claude && cp ejemplos/settings/settings.json .claude/settings.json
```

## Cómo leerlo

| Lista | Qué hace | Qué puse ahí |
|---|---|---|
| `allow` | Corre sin preguntar | Todo lo de solo lectura o gratis: `git status/diff/log`, `dbt parse/compile/ls`, `bq query --dry_run`, `bq show/ls/head`, linters y tests |
| `ask` | Pregunta siempre, incluso en modo `acceptEdits` o `auto` | Lo que cuesta plata o es visible para otros: `dbt run/build`, `git push`, `git commit`, subir archivos a GCS, comandos de Composer |
| `deny` | Bloqueado | Borrados (`bq rm`, `gsutil rm`, `gcloud ... delete`), `git reset --hard`, y leer secretos (`.env`, keys de service account, credenciales de `gcloud`, `profiles.yml`) |

Lo que no aparece en ninguna lista, en modo `default` (Manual), te pregunta la primera vez.

## Las reglas que hay que saber (verificadas en la doc oficial)

- **Orden de evaluación: `deny` → `ask` → `allow`.** Gana la primera que matchea, sin importar cuál es más específica. Por eso **no** puse `Bash(bq query *)` en `ask`: también matchearía `bq query --dry_run ...` y te preguntaría por cada dry run. Para pedir confirmación solo en las queries reales usá el hook [`guardia-bigquery.sh`](../hooks/scripts/guardia-bigquery.sh), que devuelve `ask` cuando falta `--dry_run`.
- **El `*` matchea texto literal en esa posición.** `Bash(bq query --dry_run *)` matchea `bq query --dry_run --use_legacy_sql=false "..."`, pero **no** `bq query --use_legacy_sql=false --dry_run "..."` ni `bq --project_id=x query --dry_run ...`. Por eso el `CLAUDE.md` de ejemplo le pide a Claude que ponga `--dry_run` primero.
- **`Bash(ls *)` con espacio** no matchea `lsof`; `Bash(ls*)` sin espacio sí.
- **Comandos compuestos**: `Bash(git status *)` no autoriza `git status && rm -rf x`; cada subcomando tiene que matchear por separado. Los `deny`/`ask` aplican si *cualquier* subcomando matchea.
- **Restringir argumentos es frágil.** `Bash(bq rm *)` no frena `bq --location=US rm -t ...`. Para bloqueos que importan, sumá un hook `PreToolUse` (ver [hooks](../hooks/README.md)) o el [sandbox](../../docs/07-permisos.md).
- **`Read(...)` bloquea las tools de archivos** (Read, Grep, Glob, menciones con `@`, y también Edit/Write sobre esa ruta), **no** un `cat .env` por Bash: `cat`, `ls`, `grep`, `head` y las formas read-only de `git` son comandos que Claude Code ya considera de solo lectura y corre sin preguntar. Si el secreto tiene que quedar inaccesible de verdad, usá el sandbox o sacalo del repo. Los patrones sin `/` (`Read(.env)`) siguen la semántica de `.gitignore`: matchean a cualquier profundidad.
- **Rutas**: `Read(./x)` o `Read(x)` es relativo al proyecto, `Read(~/x)` al home, `Read(//x)` es absoluta.
- **Las listas se suman entre archivos**: lo que pongas en `~/.claude/settings.json` (tuyo) y `.claude/settings.local.json` (tuyo, no se commitea) se combina con esto.
- **Las reglas las aplica Claude Code, no el modelo.** Escribir "no borres tablas" en `CLAUDE.md` es una sugerencia; un `deny` es una garantía.

## Cómo verificar que cargó

- `/permissions` muestra cada regla y de qué archivo viene.
- `claude doctor` valida los archivos de settings desde la terminal.
- El `$schema` te da autocompletado y validación en VS Code.

## Variantes útiles

```json
{
  "permissions": {
    "defaultMode": "plan",
    "deny": ["Agent(Explore)", "mcp__bigquery__execute_sql"]
  }
}
```

- `defaultMode`: el modo con el que arranca cada sesión (`default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`).
- `Agent(nombre)`: deshabilita un subagent.
- `mcp__<server>__<tool>`: controla tools de un servidor MCP (`mcp__bigquery` matchea todo el server).

Ver [07 — Permisos](../../docs/07-permisos.md).
