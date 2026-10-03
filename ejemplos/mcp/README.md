# Servidores MCP para el stack de datos

[`ejemplo.mcp.json`](ejemplo.mcp.json) trae tres servidores. Copialo a la raíz del repo como `.mcp.json` (con punto; si lo dejás en una subcarpeta no se carga):

```bash
cp ejemplos/mcp/ejemplo.mcp.json .mcp.json
```

| Server | Qué te da | Requisitos |
|---|---|---|
| `bigquery` | Listar datasets/tablas, ver esquemas, correr SQL (`execute_sql`), buscar en el catálogo. Vía [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) de Google | Node (`npx`), `gcloud auth application-default login`, `BIGQUERY_PROJECT` exportada |
| `dbt` | Lineage desde el `manifest.json`, `compile`, `list`, `show`, `build`/`run`/`test`, codegen. Vía [dbt-mcp](https://github.com/dbt-labs/dbt-mcp) | `uv` (`uvx`), `DBT_PROJECT_DIR` (ruta absoluta al proyecto) y `DBT_PATH` (`which dbt`) |
| `github` | PRs, issues, reviews | `GITHUB_PAT` (token fine-grained) |

Las variables `${VAR}` se expanden desde tu entorno al arrancar; `${VAR:-default}` usa el default si no está. Así el archivo se commitea **sin secretos**.

## Lo mismo con `claude mcp add`

```bash
# BigQuery (stdio). El "--" separa las opciones de claude de las del server.
claude mcp add --env BIGQUERY_PROJECT=mi-proyecto --env BIGQUERY_WRITE_MODE=blocked \
  --transport stdio --scope project \
  bigquery -- npx -y @toolbox-sdk/server --prebuilt=bigquery --stdio

# dbt (stdio)
claude mcp add --env DBT_PROJECT_DIR="$PWD" --env DBT_PATH="$(which dbt)" \
  --transport stdio --scope project \
  dbt -- uvx dbt-mcp

# GitHub (remoto, HTTP)
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer $GITHUB_PAT"
```

Ojo: no pongas el nombre del server justo después de un `--env` (lo lee como otro `KEY=valor`); por eso va `--transport` en el medio. Y `--env` con valores literales los escribe tal cual en el archivo. Para `--scope project` (se commitea) preferí editar `.mcp.json` a mano con `${VAR}`.

## Scopes

| Scope | Dónde se guarda | Para qué |
|---|---|---|
| `local` (default) | `~/.claude.json`, solo para este proyecto | Pruebas, servers con credenciales tuyas |
| `project` | `.mcp.json` en la raíz | Lo que usa todo el equipo (se commitea) |
| `user` | `~/.claude.json`, todos tus proyectos | Herramientas personales (ej. GitHub) |

## Administrar

```bash
claude mcp list            # todos los servers y su estado
claude mcp get bigquery    # detalle de uno
claude mcp remove dbt      # sacarlo
claude mcp reset-project-choices   # volver a preguntar por los de .mcp.json
```

Dentro de la sesión: `/mcp` para ver estado, reconectar, autenticar (OAuth) o deshabilitar un server sin borrarlo.

## Seguridad y costo

- **`BIGQUERY_WRITE_MODE=blocked`** deja el server en solo lectura (no ejecuta DML/DDL). **`BIGQUERY_MAXIMUM_BYTES_BILLED`** corta cualquier query que procese más de esa cantidad de bytes (10 GB en el ejemplo).
- La primera vez que abrís un repo con `.mcp.json`, Claude Code te pide aprobar sus servers. En `claude -p` (headless) los carga sin preguntar: tenelo en cuenta en CI.
- Las tools de MCP se controlan con permisos como cualquier otra: `mcp__bigquery__execute_sql` en `ask` si querés confirmar cada query, `mcp__dbt__run` en `deny` si no querés que materialice.
- Para el uso diario, `bq` y `gcloud` por Bash ocupan menos contexto que un server MCP. Usá MCP cuando aporta algo que el CLI no (catálogo, lineage del manifest, OAuth a un SaaS).

## Trucos

- Si un server aparece `failed` en `/mcp`, el detalle muestra el error (ej. un `401` = token mal). `claude mcp add` no valida credenciales al guardar.
- Instrucciones de otro cliente (Claude Desktop, Cursor) con un bloque `mcpServers`: pasale el objeto interno a `claude mcp add-json <nombre> '<json>'`.
- Un subagent puede tener sus propios servers con `mcpServers:` en el frontmatter, así no cargás todo en la sesión principal.

Ver [13 — MCP](../../docs/13-mcp.md).
