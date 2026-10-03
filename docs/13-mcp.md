# MCP: conectar herramientas y datos externos

> **En 30 segundos:** MCP (Model Context Protocol) es el estándar abierto para enchufarle a Claude Code herramientas externas: GitHub, un navegador, BigQuery, Linear, docs actualizadas. Se agrega un server con `claude mcp add`, se revisa con `/mcp`, y sus tools quedan disponibles como cualquier otra, sujetas a los mismos permisos. Antes de sumar uno, preguntate si una CLI que ya tenés (`gh`, `bq`, `gcloud`) no alcanza.

## Qué es y cómo funciona

Un **server MCP** expone tools (y a veces recursos y prompts) que Claude puede usar. Hay dos formas de correrlo:

| Transporte | Qué es | Ejemplo |
|---|---|---|
| `http` (remoto) | Un servicio en la nube; suele autenticar con OAuth | Linear, Sentry, Notion, BigQuery de Google |
| `stdio` (local) | Un proceso que Claude Code levanta en tu máquina | Playwright vía `npx` |

`sse` también existe pero está deprecado; usá `http`.

Las tools de un server se llaman `mcp__<server>__<tool>` (ej. `mcp__github__list_issues`). Ese nombre es el que usás en permisos y en matchers de [hooks](12-hooks.md).

### Cuánto contexto cuesta un server

Por defecto Claude Code usa **tool search**: al arrancar solo carga los nombres de las tools y las instrucciones de cada server; la definición completa de una tool se trae cuando Claude la necesita. Por eso sumar servers ya no explota el context window como antes. Igual tiene costo:

- Las instrucciones de cada server y los nombres de tools se pagan en cada turno.
- Cada resultado de tool entra al contexto. Claude Code avisa si un resultado pasa los 10.000 tokens y, por encima de 25.000 (default, configurable con `MAX_MCP_OUTPUT_TOKENS`), lo guarda en un archivo.
- `ENABLE_TOOL_SEARCH=false` carga todo de entrada (no lo hagas salvo que tengas un motivo); `"alwaysLoad": true` en un server hace que sus tools estén siempre visibles.

Mirá el impacto real con `/context`.

## Cómo se usa

### Agregar un server

```bash
# Remoto (HTTP)
claude mcp add --transport http linear https://mcp.linear.app/mcp

# Remoto con token en header
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer $GITHUB_PAT"

# Local (stdio): todo lo que va después de -- es el comando del server
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Con variables de entorno para el server
claude mcp add --transport stdio --env API_KEY=xxx mi-server -- python server.py

# Desde un bloque JSON que te dio la doc del server
claude mcp add-json clima '{"type":"http","url":"https://api.ejemplo.com/mcp"}'
```

Gestión:

```bash
claude mcp list            # todos los servers configurados
claude mcp get linear      # detalle de uno
claude mcp remove linear   # sacarlo (borra también los tokens OAuth guardados)
```

Dentro de la sesión, `/mcp` muestra el estado de cada server (`connected`, `failed`, necesita auth), permite autenticar, re-autenticar y deshabilitar un server sin borrarlo.

### Scopes: dónde queda guardado

| Scope | Flag | Dónde se guarda | Para qué |
|---|---|---|---|
| `local` (default) | `--scope local` | `~/.claude.json`, bajo la ruta del proyecto | Solo vos, solo este repo. Ideal para servers con credenciales |
| `project` | `--scope project` | `.mcp.json` en la raíz del repo | Todo el equipo (se commitea) |
| `user` | `--scope user` | `~/.claude.json` | Vos, en todos tus proyectos |

Si el mismo server está en varios scopes, gana local > project > user, y se usa la definición entera de ese scope (no se mezclan campos).

`.mcp.json` compartido, sin secretos, usando variables de entorno:

```json
{
  "mcpServers": {
    "linear": { "type": "http", "url": "https://mcp.linear.app/mcp" },
    "interno": {
      "type": "http",
      "url": "${API_BASE_URL:-https://mcp.interno.empresa.com}/mcp",
      "headers": { "Authorization": "Bearer ${MCP_INTERNO_TOKEN}" }
    }
  }
}
```

La expansión `${VAR}` y `${VAR:-default}` funciona en `command`, `args`, `env`, `url` y `headers`. La primera vez que alguien abre el repo, Claude Code pide aprobar los servers de `.mcp.json` (se resetea con `claude mcp reset-project-choices`).

### Autenticación OAuth

Para servers remotos con OAuth: agregás el server, abrís `/mcp`, lo seleccionás y seguís el login en el navegador. Los tokens se guardan de forma segura y se refrescan solos. Desde la terminal también existe `claude mcp login <nombre>`. En modo headless (`claude -p`) no hay forma de completar OAuth: autenticá antes en una sesión interactiva.

## CLI vs MCP: cuándo conviene cada uno

Claude ya sabe usar CLIs muy bien. Para el stack de datos, muchas veces la CLI gana:

| Herramienta | CLI | ¿MCP? |
|---|---|---|
| GitHub | `gh` (PRs, issues, Actions, API) | Solo si querés que funcione sin `gh` instalado o en entornos sin shell |
| BigQuery | `bq query`, `bq show`, `bq ls`, `--dry_run` | Opcional (ver abajo). La CLI + reglas de permisos suele alcanzar |
| GCP en general | `gcloud` (logging, composer, storage) | Rara vez hace falta |
| Navegador | No hay CLI equivalente | Sí: Playwright |
| Linear / Jira / Notion | No suele haber CLI cómoda | Sí |

Ventajas de la CLI: cero contexto extra, ya está autenticada con tus credenciales, y la controlás con reglas de [permisos](07-permisos.md) del tipo `Bash(bq query *)`. Ventajas del MCP: tools tipadas, OAuth, resultados estructurados y funciona donde no hay shell (Claude Desktop, rutinas en la nube).

Regla práctica: si la CLI existe y está en tu `PATH`, empezá por la CLI. Sumá un MCP cuando no hay CLI o cuando la integración es claramente mejor.

## Servers recomendados (opciones, no obligaciones)

| Server | Para qué | Cómo agregarlo |
|---|---|---|
| **Docs de Claude Code** | Que Claude consulte la documentación oficial actual | `claude mcp add --transport http claude-code-docs https://code.claude.com/docs/mcp` |
| **Playwright** | Navegador real: probar un dashboard de Looker Studio, scrapear una página, ver un error en una UI | `claude mcp add playwright -- npx -y @playwright/mcp@latest` |
| **Context7** | Docs actualizadas y por versión de librerías (dbt, Airflow, pandas…) | `claude mcp add --transport http context7 https://mcp.context7.com/mcp` |
| **GitHub** | PRs e issues sin `gh` | `claude mcp add --transport http github https://api.githubcopilot.com/mcp/ --header "Authorization: Bearer <PAT>"` |
| **BigQuery (Google, remoto)** | Listar datasets/tablas, ver schemas, correr SQL | Endpoint `https://bigquery.googleapis.com/mcp` (HTTP). Requiere habilitar la API y roles `roles/mcp.toolUser`, `roles/bigquery.jobUser`, `roles/bigquery.dataViewer`. Seguí la [guía de Google](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp) para la autenticación |
| **Linear** | Leer y actualizar issues | `claude mcp add --transport http linear https://mcp.linear.app/mcp` y después `/mcp` para el login |
| **Sentry** | Errores y stack traces | `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp` |

Para Jira/Confluence, Slack, Notion y otros, buscá el server oficial del proveedor en el [Anthropic Directory](https://claude.ai/directory): los conectores de ahí se agregan igual con `claude mcp add`. Si usás Claude con cuenta de claude.ai, los conectores que habilitaste ahí también aparecen en Claude Code.

## Ejemplo: explorar un dataset con el MCP de BigQuery, en solo lectura

El server de BigQuery expone, entre otras, `execute_sql_readonly` (solo SELECT) y `execute_sql` (puede correr DML/DDL). Dejá la de escritura bloqueada (asumiendo que agregaste el server con el nombre `bigquery`):

```json
{
  "permissions": {
    "allow": [
      "mcp__bigquery__list_dataset_ids",
      "mcp__bigquery__list_table_ids",
      "mcp__bigquery__get_table_info",
      "mcp__bigquery__execute_sql_readonly"
    ],
    "deny": ["mcp__bigquery__execute_sql"]
  }
}
```

Y después:

```text
Mirá el schema de analytics.fct_ventas y decime qué columnas tienen más de 5% de nulls en los últimos 7 días de partición.
```

## Trucos y errores comunes

- **Seguridad primero.** Un server MCP corre con tus credenciales. Usá solo servers de fuentes confiables, preferí usuarios/roles de solo lectura (en DBs, un usuario `readonly` en el connection string) y negá las tools de escritura con `permissions.deny`.
- **Prompt injection:** un server que trae contenido externo (páginas web, issues, emails) puede meter instrucciones maliciosas en el contexto. No combines ese tipo de server con permisos amplios de escritura.
- **Nada de tokens en `.mcp.json`.** Usá `${VAR}` y que cada uno tenga la variable en su entorno, o agregá el server con scope `local`.
- **El `--` es obligatorio en stdio** para separar las opciones de Claude de los flags del server. Y `--env` no puede ir pegado al nombre del server: poné otra opción en el medio.
- **`url` sin `type` es error**: en JSON, una entrada con `url` necesita `"type": "http"`.
- **Rutas que Claude Code NO lee:** `~/.claude/.mcp.json`, `~/.claude/mcp.json`. Las válidas son `~/.claude.json` y `.mcp.json` en la raíz del repo.
- **Server que no conecta:** `/mcp` muestra el error; para stdio corré el comando del server a mano en la terminal. Si tarda en arrancar (primer `npx`), subí `MCP_TIMEOUT` (ms).
- **`claude mcp add` no valida credenciales**: un token mal puesto se ve recién como `failed` en `/mcp`.
- **En CI**, los servers de `.mcp.json` se cargan sin preguntar con `claude -p`. Si no los querés, usá `--strict-mcp-config` con `--mcp-config` explícito, o `--bare`.
- **Servers MCP por subagent:** el campo `mcpServers` de un [subagent](11-subagents.md) le da un server solo a ese agente, sin cargarlo en tu sesión principal.

## Ver también

- [Permisos](07-permisos.md) — reglas `allow`/`deny` para tools `mcp__*`.
- [Hooks](12-hooks.md) — matchers `mcp__<server>__.*`.
- [Plugins](14-plugins.md) — empaquetar servers MCP junto con skills y hooks.
- [Contexto](05-contexto.md) — `/context` para ver cuánto ocupa cada server.
- Documentación oficial: [MCP en Claude Code](https://code.claude.com/docs/en/mcp) · [Quickstart](https://code.claude.com/docs/en/mcp-quickstart).
