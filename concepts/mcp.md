# MCP

> verificado: 2026-10-18 · fuentes: [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture), [Server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [Security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices), [MCP (Claude Code)](https://code.claude.com/docs/en/mcp), [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp), [Copilot MCP](https://docs.github.com/en/copilot/concepts/context/mcp), [Gemini CLI MCP](https://geminicli.com/docs/tools/mcp-server/), [Antigravity MCP](https://antigravity.google/docs/mcp?tab=cli)

Model Context Protocol es un protocolo abierto, cliente/servidor sobre JSON-RPC 2.0, para que un agent se conecte de forma estándar a programas externos (servers) que exponen tools, datos y prompts. Un mismo server sirve para cualquier host compatible: Claude Code, Copilot, Gemini CLI, Antigravity, Cursor y otros.

## Cuándo usarlo y cuándo no

**Usarlo para:**
- Integrar sistemas externos de forma reutilizable entre herramientas: issue trackers, bases de datos, APIs SaaS, observabilidad.
- Casos con auth (OAuth) y datos en vivo.

**No usarlo cuando:**
- Ya existe un CLI que el agent usa bien por shell (`gh`, `psql`, `duckdb`). Es más simple y no tiene costo fijo de contexto. (Esta es una heurística de la comunidad, no algo que diga la doc oficial.)
- El server expone decenas de tools que no vas a usar.
- No confiás en el server.

## Cómo funciona

```
host (Claude Code) ─┬─ client ── server A (stdio, proceso local)
                    └─ client ── server B (HTTP, remoto)
```

| Primitiva | La controla | Qué es |
|---|---|---|
| **Tools** | el modelo | Funciones con un input en JSON Schema (`tools/call`). |
| **Resources** | la app | Datos que se identifican por URI (`resources/read`). |
| **Prompts** | el usuario | Plantillas, que suelen aparecer como slash commands. |

- **Transports**: `stdio` para procesos locales y **Streamable HTTP** para remotos (con OAuth). SSE quedó deprecado.
- **Spec vigente (`2026-07-28`)**:
  - El protocolo es stateless: cada request lleva la versión y las capacidades en `_meta`.
  - Sampling y logging quedaron deprecados.
- **Costo en contexto**: las definiciones de tools y sus resultados ocupan la ventana. Para mitigarlo hay dos técnicas: cargar las definiciones bajo demanda (tool search) y exponer los servers como código que el agent ejecuta. En el ejemplo de Anthropic, eso bajó el consumo de ~150k a ~2k tokens.

## En Claude Code

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer $GITHUB_PAT"                              # remoto
claude mcp add --scope project duck -- uvx mcp-server-duckdb --db-path data.db   # local; todo después de -- va al server (no probado)
claude mcp list
```

| Scope | Dónde vive | Uso |
|---|---|---|
| `local` (default) | `~/.claude.json`, por proyecto | Personal, en este repo. |
| `project` | `.mcp.json` (versionado) | Compartido con el equipo. Se aprueba al abrir el proyecto. |
| `user` | `~/.claude.json` | Personal, en todos los repos. |

- **Secretos**: en `.mcp.json` usar `${VAR}` o `${VAR:-default}`, nunca valores literales.
- **Nombres**: los tools se llaman `mcp__<server>__<tool>` (es lo que usan los permisos y los matchers de hooks). Los resources se referencian con `@server:uri`.
- **Tool search** (activado por default): al inicio solo se cargan los nombres; las definiciones se traen cuando hacen falta. Se controla con `ENABLE_TOOL_SEARCH`.
- **Límite de output**: 25k tokens por default (`MAX_MCP_OUTPUT_TOKENS`).
- **`/mcp`**: estado de los servers y login OAuth.
- **`claude mcp serve`**: expone Claude Code como server MCP.

## En otras herramientas

- **Copilot**: IDEs, CLI y cloud agent. El GitHub MCP server viene integrado. `no probado`
- **Gemini CLI**: `mcpServers` en `settings.json`, comando `gemini mcp add`. Con `trust: true` saltea todas las confirmaciones. `no probado`
- **Antigravity**: `.agents/mcp_config.json`. `no probado`

## Errores comunes

- **Instalar servers sin revisarlos**: un server local corre con tus privilegios.
- **[Prompt injection](tools-and-permissions.md#cómo-funciona)**: los servers que traen contenido externo (web, issues, mails) son la vía más común.
- **Secretos hardcodeados** en un `.mcp.json` versionado.
- **Olvidar el `--`** antes del comando de un server local.
- **Inflar el contexto**: desactivar tool search o conectar servers "por las dudas".
- **Resultados enormes** que quedan truncados. Mejor filtrar del lado del server.

## Ver también

[tools-and-permissions](tools-and-permissions.md) · [context](context.md) · [hooks](hooks.md)
