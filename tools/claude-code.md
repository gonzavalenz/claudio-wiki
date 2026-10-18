# Claude Code

> verificado: 2026-10-18 · fuentes: [Mods](https://code.claude.com/docs/en/plugins/mods/overview), [Crear mods](https://code.claude.com/docs/en/plugins/mods/create), [Plugins](https://code.claude.com/docs/en/plugins/overview), [Checkpointing](https://code.claude.com/docs/en/checkpointing), [Permission modes](https://code.claude.com/docs/en/permission-modes), [Goal](https://code.claude.com/docs/en/goal), [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks), [Code review](https://code.claude.com/docs/en/code-review-local), [Ultrareview](https://code.claude.com/docs/en/ultrareview), [Headless](https://code.claude.com/docs/en/headless), [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview), [Statusline](https://code.claude.com/docs/en/statusline), [Voice](https://code.claude.com/docs/en/voice-dictation), [Chrome](https://code.claude.com/docs/en/chrome), [Mods interface](https://code.claude.com/docs/en/plugins/mods/interface), [Session recap](https://code.claude.com/docs/en/interactive-mode#session-recap)

Lo que es propio de Claude Code y no tiene un equivalente general. Los conceptos compartidos están en [concepts/](../README.md#índice). Los requisitos de versión envejecen rápido: revisalos contra la fecha de verificación.

## Mods

Un mod es un plugin que corre código JS/TS **dentro del proceso** de Claude Code. Los hooks de settings, las skills y MCP, en cambio, corren afuera. Los docs tienen una [tabla mod / hook / skill / MCP](https://code.claude.com/docs/en/plugins/mods/overview) para elegir entre ellos.

- **Forma**: el `hooks/hooks.json` del plugin tiene una clave `modules` que apunta a un archivo que exporta `register(on)`. Cada `on('evento', ($, e, next) => …)` puede observar, reescribir o responder el evento sin llamar a `next`. Se carga `.js`/`.ts` directo, sin build. Requiere v2.1.287+ en terminal.
- **Qué puede hacer**: panes laterales, una banda sobre el prompt, toasts y su propia status line. También redibuja el spinner y las filas de tool calls, retiene o responde tool calls, consulta otro modelo y registra `/comandos` que corren sin turno de Claude. En `claude -p` y en el Agent SDK los hooks corren, pero no dibujan.
- **Crearlo**: se le pide a Claude, que usa la skill built-in `plugin-authoring`. El mod queda en `~/.claude/dev-mods/<session-id>/`, carga solo en esa sesión y se borra con la limpieza periódica. Para conservarlo, copialo afuera y cargalo con `--plugin-dir` (que hace hot-reload, pero resetea las variables).
- **Validar**: `claude plugin validate` analiza estáticamente los `hooks:` y `calls:`, por eso `$` no se puede asignar ni desestructurar. `claude plugin test` corre los tests sin sesión.
- **Seguridad**: **no tiene sandbox**. Puede auto-aprobar tool calls, incluso los que bloqueó un hook `PreToolUse`, y leer env vars y API keys. Lo único que no puede tocar es el permission prompt. Se apagan con `disableAllHooks` o `--safe-mode`, salvo los built-in. Instalá solo mods que hayas leído.

## Plugins

Un plugin empaqueta skills, agents, hooks, MCP y mods. Un marketplace es un `.claude-plugin/marketplace.json` en un repo: es un catálogo, no un store.

- Un plugin habilitado mete los nombres y descripciones de sus skills y agents en el contexto **en cada turno** (las que Claude puede invocar solo), aunque no se usen. Para los del marketplace oficial, `/plugin` muestra un "Context cost" estimado.
- Scopes: user, project o local.

## Checkpointing y `/rewind`

Hay un checkpoint por cada prompt (guarda los últimos 100). `/rewind` o `Esc Esc` restaura el código, la conversación o ambos.

**No restaura**:
- Cambios hechos por Bash (`rm`, `mv`, `cp`).
- Ediciones externas o de otras sesiones.
- Ediciones de subagents (incluido `/code-review --fix`).
- Symlinks y hard links.

Para eso sirve git, ver [practices](../practices.md).

## Plan mode

Claude explora pero no edita. Se entra con `Shift+Tab` o escribiendo `/plan` delante de un prompt. `Ctrl+G` abre el plan en el editor.

En la terminal interactiva, si la sesión arrancó con bypass disponible (`--dangerously-skip-permissions`, `--permission-mode bypassPermissions` o `defaultMode` en bypass), los bloqueos de plan mode no se aplican: queda solo la instrucción. En `-p`, el SDK y VS Code sí se aplican.

## Trabajo autónomo

| Feature | Qué es | Detalle no obvio |
|---|---|---|
| `/goal <condición>` | Stop hook de sesión: un modelo chico juzga después de cada turno si la condición se cumplió | El evaluador no corre tools, solo lee el transcript. Para acotarlo, agregá "or stop after N turns". |
| `/loop [intervalo] <prompt>` | Repite un prompt en la sesión | Solo dispara con la sesión abierta y ociosa, sin catch-up. Las recurrentes expiran a los 7 días. |
| Routines (`/schedule`) | Agentes en la nube con cron | Son la opción durable, sin depender de tu máquina. |
| `claude -p` | Headless, para scripts y CI | `--bare` saltea `CLAUDE.md`, hooks, MCP, plugins, skills y auto memory, y exige `ANTHROPIC_API_KEY` o `apiKeyHelper`. `--json-schema` devuelve output estructurado. |
| Agent SDK | Librería Python/TS que corre el binario de Claude Code | Carga `.claude/` igual que el CLI. Un producto de terceros tiene que usar API key. |

## Review

- **`/code-review [nivel]`**: subagent en background que consume el uso normal del plan. Recuerda el último nivel de effort y con `--fix` aplica los hallazgos.
- **`/code-review ultra`** (alias `/ultrareview`, research preview): flota de agentes en un sandbox cloud que verifican cada hallazgo. Tarda 15–25 min y en Pro/Max trae 3 corridas gratis **por única vez**; después cuesta unos US$5–25 en usage credits (tienen que estar activados). Requiere una cuenta claude.ai. El límite por default es de 500 archivos / 8.000 líneas.

## Interfaz

- **Statusline**: un script que recibe JSON por stdin (`context_window.used_percentage`, `cost.total_cost_usd`, `rate_limits`, `effort.level`). No consume tokens. Se configura con `/statusline`.
- **Voice dictation**: el audio se transcribe en servidores de Anthropic, no localmente. Requiere una cuenta claude.ai y no funciona por SSH. Soporta español con el setting `language`.
- **Browser**: la extensión Claude in Chrome comparte el login de tu navegador y requiere plan Pro/Max/Team/Enterprise. La alternativa es [Playwright MCP](https://github.com/microsoft/playwright-mcp), que trabaja sobre el accessibility tree.
- **Session recap**: aparece al volver a la terminal si pasaron 3 min desde el último turno, con la terminal sin foco y al menos 3 turnos en la sesión. También está `/recap`.

## Ver también

[hooks](../concepts/hooks.md) · [skills](../concepts/skills.md) · [mcp](../concepts/mcp.md) · [practices](../practices.md)
