# Recetas de `hooks`

Tres hooks listos para copiar. Un hook es un comando que Claude Code ejecuta **siempre** en un punto del ciclo (antes de una tool, después, al terminar), sin depender de que el modelo "se acuerde".

| Script | Evento | Qué hace |
|---|---|---|
| [`guardia-bigquery.sh`](scripts/guardia-bigquery.sh) | `PreToolUse` (`Bash`) | Bloquea `bq rm` y SQL destructivo; pide confirmación para `bq query` sin `--dry_run` |
| [`formatear-python.sh`](scripts/formatear-python.sh) | `PostToolUse` (`Edit\|Write`) | Corre `ruff format` + `ruff check --fix` sobre el `.py` editado; si queda algo, se lo devuelve a Claude |
| [`notificar-macos.sh`](scripts/notificar-macos.sh) | `Stop` + `Notification` | Notificación nativa de macOS cuando Claude termina o espera tu permiso |

Requieren `jq` (`brew install jq`) y, el de formato, `ruff`.

## Instalación

**Proyecto** (guardia + ruff, se commitea):

```bash
mkdir -p .claude/hooks
cp ejemplos/hooks/scripts/{guardia-bigquery,formatear-python}.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

Y sumá el bloque `hooks` de [`settings-proyecto.json`](settings-proyecto.json) a `.claude/settings.json` (si ya tenés el de [`settings/`](../settings/settings.json), mergealos: `permissions` y `hooks` conviven en el mismo archivo).

**Usuario** (la notificación es preferencia personal, va en tu home):

```bash
mkdir -p ~/.claude/hooks
cp ejemplos/hooks/scripts/notificar-macos.sh ~/.claude/hooks/ && chmod +x ~/.claude/hooks/notificar-macos.sh
```

Y el bloque de [`settings-usuario.json`](settings-usuario.json) en `~/.claude/settings.json`.

Verificá con `/hooks` (lista lo que cargó y de dónde).

## Cómo funcionan (lo mínimo para escribir los tuyos)

- **Entrada**: el hook recibe un JSON por stdin. Para `Bash` el comando está en `.tool_input.command`; para `Edit`/`Write`, la ruta en `.tool_input.file_path`. Siempre vienen `hook_event_name`, `cwd` y `session_id`.
- **Exit codes**: `0` = OK (sigue el flujo normal). `2` = bloquea (en `PreToolUse` frena la tool; en `PostToolUse` le muestra tu stderr a Claude). **Cualquier otro código, incluido `1`, NO bloquea**: si tu hook es una política, usá `exit 2` o JSON.
- **Decisión con JSON** (`PreToolUse`): imprimir en stdout `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny" | "ask" | "allow", "permissionDecisionReason": "..."}}`. Con `ask` el motivo se te muestra a vos; con `deny`, a Claude.
- **Matcher**: `"Bash"` matchea exacto; `"Edit|Write"` es una lista; si tiene otros caracteres se evalúa como regex (`"mcp__bigquery__.*"`).
- **Rutas**: usá `${CLAUDE_PROJECT_DIR}` y la forma *exec* (`"args": []`) para que funcione desde cualquier subcarpeta. La forma *shell* (sin `args`) sirve cuando querés `~`, pipes o `&&`.
- **Filtro `if`**: un hook puede llevar `"if": "Bash(bq *)"` (sintaxis de reglas de permisos) para correr solo en esos comandos. Es *best effort*: para un bloqueo duro, combiná con `deny` en permisos.

## Trucos y errores comunes

- **Script sin `chmod +x` o ruta mal escrita** → el hook falla con un error no bloqueante y la acción sigue. Tu guardia queda apagada sin que te enteres: mirá el primer aviso `hook error` en el transcript.
- **Probalo a mano** antes de confiar en él:
  ```bash
  echo '{"tool_input":{"command":"bq --location=US rm -t ds.t"}}' | .claude/hooks/guardia-bigquery.sh
  ```
- **La guardia es conservadora**: también bloquea un `--dry_run` que contenga `DROP`/`DELETE`. Si necesitás eso, lo corrés vos con `!` en el prompt.
- **`Stop` se dispara al final de cada respuesta**, no solo de la tarea. Si te molesta, dejá solo `Notification` con `permission_prompt`.
- **`osascript` no muestra nada**: habilitá notificaciones para *Script Editor* en Configuración del Sistema (macOS no te lo pregunta).
- **Hooks de un subagent**: se pueden declarar en el frontmatter del subagent (`hooks:`), y corren solo mientras ese subagent está activo.

Ver [12 — Hooks](../../docs/12-hooks.md).
