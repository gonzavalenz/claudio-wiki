# Cheatsheet

> Referencia rápida de una página. Verificado contra la [doc oficial](https://code.claude.com/docs/en/claude_code_docs_map.md); `/help` y `claude --help` muestran lo de tu versión.

## Arrancar

| Comando | Qué hace |
|---|---|
| `claude` | Sesión interactiva en la carpeta actual |
| `claude "explicá este repo"` | Sesión interactiva con un primer prompt |
| `claude -c` | Continúa la última conversación de esta carpeta |
| `claude -r` / `claude -r nombre` | Elegir una sesión para retomar / retomar por nombre o ID |
| `claude -n dbt-ventas` | Arranca con nombre (después `claude -r dbt-ventas`) |
| `claude -p "pregunta"` | Headless: responde y sale (scripts, CI) |
| `cat error.log \| claude -p "qué pasó"` | Le pasás contenido por pipe |
| `claude -p "..." --output-format json` | Salida JSON para parsear |
| `claude --permission-mode plan` | Arranca en plan mode |
| `claude --model opus` | Elige modelo para la sesión (`sonnet`, `opus`, `haiku`, `fable` o ID) |
| `claude -w nombre` | Sesión en un git worktree aislado (`.claude/worktrees/nombre`) |
| `claude --add-dir ../otro-repo` | Suma otra carpeta con acceso de lectura/escritura |
| `claude --agent revisor-dbt` | Toda la sesión corre como ese subagent |
| `claude update` · `claude doctor` · `claude -v` | Actualizar · diagnosticar instalación y settings · versión |

Flags útiles en `-p`: `--max-turns N`, `--max-budget-usd 2`, `--allowedTools "Bash(dbt compile *)"`, `--append-system-prompt "..."`, `--mcp-config archivo.json`.

## Atajos de teclado

| Atajo | Qué hace |
|---|---|
| `Esc` | Frena a Claude en el momento (conserva lo hecho) |
| `Esc` `Esc` | Con texto: borra el input. Vacío: menú de rewind (checkpoints) |
| `Shift+Tab` | Rota modos: `default` → `acceptEdits` → `plan` (→ `auto` si está disponible) |
| `Ctrl+G` | Abre el prompt (o el plan) en tu editor |
| `Ctrl+O` | Transcript detallado (tools, timestamps, modelo) |
| `Ctrl+B` | Manda a background un comando o agente que está corriendo |
| `Ctrl+T` | Muestra/oculta la lista de tareas de Claude |
| `Ctrl+R` | Busca en el historial de prompts |
| `Ctrl+S` | Guarda el prompt a medio escribir y lo recupera después |
| `Ctrl+V` (`Cmd+V` en iTerm2) | Pega una imagen del portapapeles |
| `Option+P` / `Option+T` / `Option+O` | Cambiar modelo / thinking / fast mode (en Windows/Linux: `Alt`) |
| `\` + `Enter`, `Ctrl+J` o `Shift+Enter` | Salto de línea en el prompt |
| `Ctrl+C` · `Ctrl+D` | Interrumpir / limpiar input · salir (doble) |
| `?` con el input vacío | Panel de atajos |

## Prefijos en el prompt

| Prefijo | Qué hace |
|---|---|
| `/` | Comando o skill |
| `@ruta` | Mete el archivo en el contexto (autocompleta) · `@agent-nombre` fuerza un subagent |
| `!` | Modo shell: corre el comando y Claude ve la salida (`! dbt ls -s fct_ventas+`) |

## Slash commands que más se usan

| Comando | Qué hace |
|---|---|
| `/clear` | Conversación nueva, contexto vacío (lo más usado) |
| `/compact [foco]` | Resume la conversación para liberar contexto |
| `/context` | Qué está ocupando el context window |
| `/btw pregunta` | Pregunta al costado, no queda en el historial |
| `/rewind` | Volver código y/o conversación a un checkpoint (alias `/undo`) |
| `/resume` · `/rename` · `/branch` | Retomar · nombrar · bifurcar la sesión |
| `/plan [tarea]` | Entrar a plan mode |
| `/model` · `/effort` · `/fast` | Modelo · nivel de esfuerzo · modo rápido |
| `/usage` (alias `/cost`, `/stats`) | Costo de la sesión, límites del plan, estadísticas |
| `/init` | Genera un `CLAUDE.md` inicial |
| `/memory` | Editar `CLAUDE.md` y auto memory |
| `/permissions` | Ver/editar reglas allow/ask/deny y de qué archivo vienen |
| `/hooks` · `/skills` · `/agents` · `/mcp` · `/plugin` | Ver/administrar cada extensión |
| `/diff` | Ver los cambios del working tree |
| `/code-review` (alias `/review`) | Revisión del diff en un subagent con contexto limpio |
| `/security-review` | Revisión de seguridad de la rama |
| `/simplify` | Busca simplificaciones en lo cambiado y las aplica |
| `/tasks` | Trabajo en background (subagents, comandos) |
| `/loop 5m /algo` · `/schedule` | Repetir algo mientras la sesión está abierta · tareas programadas en la nube |
| `/statusline` | Configurar la status line |
| `/fewer-permission-prompts` | Sugiere allowlist según tu historial |
| `/doctor` | Chequeo de instalación y config |
| `/config` | Settings (tema, modelo, etc.) |

## Archivos y rutas

| Ruta | Qué es | ¿Se commitea? |
|---|---|---|
| `CLAUDE.md` o `.claude/CLAUDE.md` | Memoria del proyecto | Sí |
| `CLAUDE.local.md` | Memoria personal del proyecto | No |
| `~/.claude/CLAUDE.md` | Memoria personal, todos los proyectos | — |
| `.claude/rules/*.md` | Reglas por tema; con `paths:` solo aplican a ciertos archivos | Sí |
| `.claude/settings.json` | Permisos, hooks, env del equipo | Sí |
| `.claude/settings.local.json` | Overrides personales del proyecto | No |
| `~/.claude/settings.json` | Settings personales globales | — |
| `.claude/skills/<n>/SKILL.md` · `~/.claude/skills/` | Skills de proyecto · personales | Sí · — |
| `.claude/commands/<n>.md` | Comandos custom (formato viejo, sigue andando) | Sí |
| `.claude/agents/<n>.md` · `~/.claude/agents/` | Subagents de proyecto · personales | Sí · — |
| `.mcp.json` | Servers MCP del proyecto | Sí |
| `~/.claude.json` | Servers MCP local/user, estado interno (no editar a mano) | — |
| `~/.claude/projects/<proyecto>/` | Sesiones guardadas y auto memory | — |

Precedencia de settings (gana el de arriba): managed → flags de CLI → `settings.local.json` → `settings.json` del proyecto → `~/.claude/settings.json`. Las listas de permisos se **suman** entre archivos.

## Permisos en 4 líneas

```json
{ "permissions": {
    "allow": ["Bash(dbt compile *)", "Bash(bq query --dry_run *)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Bash(bq rm *)", "Read(.env)"] } }
```

Orden: `deny` → `ask` → `allow`, gana la primera que matchea. `Bash(x *)` matchea `x` y `x algo`; `mcp__server__tool`; `Agent(nombre)`. Ver [07 — Permisos](07-permisos.md) y [ejemplos/settings](../ejemplos/settings/README.md).

## ¿Dónde pongo esto?

| Si es... | Va en |
|---|---|
| Contexto que aplica siempre | `CLAUDE.md` ([06](06-memoria.md)) |
| Procedimiento que aplica a veces | Skill ([10](10-skills.md)) |
| Investigación que llenaría el contexto | Subagent ([11](11-subagents.md)) |
| Algo que tiene que pasar sí o sí | Hook ([12](12-hooks.md)) o `deny` ([07](07-permisos.md)) |
| Acceso a un sistema externo | MCP o CLI ([13](13-mcp.md)) |
| Paquete de todo lo anterior para compartir | Plugin ([14](14-plugins.md)) |

## Ver también

[Buenas prácticas](../buenas-practicas/README.md) · [20 — Flujos de trabajo](20-flujos-de-trabajo.md) · [21 — Costos](21-costos.md) · [Ejemplos](../ejemplos/README.md)
