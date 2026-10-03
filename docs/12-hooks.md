# Hooks: reglas que no dependen de que el modelo se acuerde

> **En 30 segundos:** un hook es un comando que Claude Code ejecuta automáticamente en un evento del ciclo de vida (antes de usar una tool, después de editar, al terminar de responder, al arrancar la sesión). Lo corre el harness, no el modelo: pasa siempre. Se configura en `settings.json` y con `exit 2` puede bloquear una acción.

## Qué es y cómo funciona

`CLAUDE.md` es una instrucción que el modelo **intenta** seguir. Un hook es código que **se ejecuta siempre** en su evento, sin pasar por el criterio del modelo. Si algo tiene que cumplirse el 100% de las veces ("nunca correr `bq rm`", "todo `.py` editado pasa por ruff"), va en un hook.

Flujo: ocurre un evento → si el `matcher` coincide, Claude Code le pasa al hook un JSON por **stdin** con el detalle (tool, input, cwd, sesión) → el hook hace lo suyo y responde con su **exit code** y, opcionalmente, JSON por stdout.

### Eventos más útiles

Hay más de 30 eventos; estos cubren el 95% de los casos:

| Evento | Cuándo dispara | ¿Puede bloquear? | Uso típico |
|---|---|---|---|
| `PreToolUse` | Antes de ejecutar una tool | Sí | Bloquear comandos peligrosos, validar inputs |
| `PostToolUse` | Después de que una tool terminó bien | No (ya se ejecutó), pero le puede avisar a Claude | Formatear/lintear lo que se editó |
| `UserPromptSubmit` | Al enviar un prompt, antes de que Claude lo procese | Sí | Agregar contexto, filtrar prompts |
| `Stop` | Cuando Claude termina de responder | Sí (lo obliga a seguir) | Notificar, exigir que pasen los tests |
| `SessionStart` | Al iniciar, retomar, `/clear` o después de compactar | No | Inyectar contexto dinámico |
| `Notification` | Cuando Claude Code necesita tu atención | No | Notificación de escritorio |
| `SubagentStart` / `SubagentStop` | Al lanzar / terminar un subagent | Solo `SubagentStop` | Logs, validar el resultado de un subagent |
| `PreCompact` / `PostCompact` | Antes / después de compactar | Solo `PreCompact` | Guardar estado antes de perder detalle |
| `PermissionRequest` | Cuando se va a pedir permiso | Por JSON | Auto-aprobar o negar ciertos pedidos |
| `SessionEnd` | Al cerrar la sesión | No | Limpieza, logs |

Otros que existen: `PostToolUseFailure`, `PostToolBatch`, `StopFailure`, `ConfigChange`, `CwdChanged`, `FileChanged`, `InstructionsLoaded`, `WorktreeCreate`/`WorktreeRemove`, `TaskCreated`/`TaskCompleted`, `Elicitation`, entre otros. Lista completa en la [referencia oficial](https://code.claude.com/docs/en/hooks).

## Cómo se usa

### Dónde se configuran

| Archivo | Alcance |
|---|---|
| `~/.claude/settings.json` | Todos tus proyectos |
| `.claude/settings.json` | El repo, compartido con el equipo (se commitea) |
| `.claude/settings.local.json` | El repo, solo vos |
| `hooks/hooks.json` de un [plugin](14-plugins.md) | Donde el plugin esté habilitado |
| Frontmatter de una [skill](10-skills.md) o [subagent](11-subagents.md) | Mientras esa skill/agente esté activo |

Los hooks de distintos archivos **se suman**, no se pisan. `/hooks` abre un visor de solo lectura con todos los hooks activos y de dónde viene cada uno. Para editarlos, cambiás el JSON (o se lo pedís a Claude).

### Estructura

Tres niveles: evento → grupo con `matcher` → lista de handlers.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/ruff.sh" }
        ]
      }
    ]
  }
}
```

- **`matcher`**: para eventos de tools filtra por nombre de tool. `"Bash"` exacto, `"Edit|Write"` lista, y si tiene otros caracteres se toma como regex (`"mcp__bigquery__.*"`). Vacío u omitido = todos. Distingue mayúsculas.
- **`if`** (opcional, por handler): filtro con sintaxis de [permisos](07-permisos.md) sobre tool + argumentos, ej. `"Bash(git *)"` o `"Edit(*.py)"`. Es *best-effort*: no lo uses como única barrera de seguridad.
- **`type`**: `command` (lo más común), `http`, `mcp_tool`, `prompt` (un modelo evalúa y decide) o `agent` (experimental).
- **`timeout`**: en segundos. Default 600 para `command`.
- Usá `$CLAUDE_PROJECT_DIR` para referenciar scripts del repo sin depender del directorio actual.

### Exit codes: cómo responde un hook

| Exit code | Qué pasa |
|---|---|
| `0` | OK. En `SessionStart` y `UserPromptSubmit` lo que imprimas por stdout se agrega como contexto para Claude |
| `2` | **Error bloqueante.** En `PreToolUse` bloquea la tool; en `Stop` obliga a seguir; en `PostToolUse` le muestra el stderr a Claude. El mensaje es tu stderr |
| Cualquier otro (incluido `1`) | Error **no bloqueante**: la acción sigue y ves un aviso |

Para control fino, salí con `0` e imprimí JSON. Por ejemplo, en `PreToolUse`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Escrituras en prod no permitidas"
  }
}
```

`permissionDecision` acepta `allow`, `deny`, `ask` o `defer`. Un `deny` de un hook bloquea incluso en `bypassPermissions`; un `allow` **no** salta las reglas `deny` de tus settings.

## Recetas copiables

Todas usan `jq` para leer el JSON (`brew install jq`). Acordate de `chmod +x` en los scripts.

### 1. Formatear y lintear con ruff después de editar un `.py`

`.claude/hooks/ruff.sh`:

```bash
#!/bin/bash
f=$(jq -r '.tool_input.file_path // empty')
[[ "$f" == *.py ]] || exit 0

ruff format --quiet "$f"
if ! out=$(ruff check --fix "$f" 2>&1); then
  echo "ruff encontró problemas que no pudo arreglar solo en $f:" >&2
  echo "$out" >&2
  exit 2   # PostToolUse: no deshace la edición, pero Claude ve esto y lo corrige
fi
exit 0
```

`.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/ruff.sh" }
        ]
      }
    ]
  }
}
```

El truco del `exit 2` en `PostToolUse`: Claude recibe el error del linter como feedback y lo arregla en el mismo turno, sin que vos digas nada.

### 2. Bloquear `bq rm`, `DROP` y borrados en GCS

Primera barrera, en [permisos](07-permisos.md) (`.claude/settings.json`):

```json
{
  "permissions": {
    "deny": ["Bash(bq rm *)", "Bash(gsutil rm *)", "Bash(gcloud storage rm *)"]
  }
}
```

Las reglas de permisos matchean por prefijo de comando; no ven un `DROP TABLE` escondido dentro de un `bq query "..."`. Para eso, un hook que mira el texto completo. `.claude/hooks/bloquear-destructivos.py`:

```python
#!/usr/bin/env python3
import json
import re
import sys

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

PATRONES = [
    r"\bbq\s+rm\b",
    r"\bDROP\s+(TABLE|SCHEMA|VIEW)\b",
    r"\bTRUNCATE\s+TABLE\b",
    r"\bDELETE\s+FROM\b(?![\s\S]*\bWHERE\b)",  # DELETE sin WHERE
    r"\b(gsutil|gcloud\s+storage)\s+(-m\s+)?rm\b",
]

for patron in PATRONES:
    if re.search(patron, cmd, re.IGNORECASE):
        print(
            f"Bloqueado por hook: el comando matchea '{patron}'. "
            "Si de verdad hace falta, pedile al usuario que lo corra a mano.",
            file=sys.stderr,
        )
        sys.exit(2)

sys.exit(0)
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/bloquear-destructivos.py" }
        ]
      }
    ]
  }
}
```

Si usás el [MCP de BigQuery](13-mcp.md), sumá un deny sobre su tool de escritura (por ejemplo `mcp__bigquery__execute_sql`) en `permissions.deny`.

### 3. Notificación de macOS cuando Claude termina o necesita algo

En `~/.claude/settings.json` (es preferencia personal, no del repo):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "osascript -e 'display notification \"Terminó de responder\" with title \"Claude Code\"'" }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          { "type": "command", "command": "osascript -e 'display notification \"Necesita un permiso\" with title \"Claude Code\" sound name \"Glass\"'" }
        ]
      }
    ]
  }
}
```

Si no aparece nada: `osascript` notifica a través de **Script Editor**. Corré una vez `osascript -e 'display notification "test"'` y habilitá Script Editor en **Ajustes del Sistema → Notificaciones**.

### 4. Inyectar contexto al iniciar (rama + proyecto GCP activo)

Evita el clásico "corrió contra el proyecto equivocado". En `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Rama git actual: $(git branch --show-current). Proyecto GCP activo: $(gcloud config get-value project 2>/dev/null).\""
          }
        ]
      }
    ]
  }
}
```

En `SessionStart`, lo que el hook imprime por stdout entra al contexto de Claude. Con `compact` en el matcher, se vuelve a inyectar después de cada compactación. Escribilo como hechos ("El proyecto activo es X"), no como órdenes: el texto con tono de "instrucción de sistema" puede activar las defensas contra prompt injection.

## Trucos y errores comunes

- **`exit 1` no bloquea.** Es la convención de Unix para error, pero acá es "no bloqueante". Si tu hook es una política, usá `exit 2`.
- **Un path mal escrito desactiva el hook en silencio**: el shell sale con 127, es error no bloqueante y la acción sigue. Mirá el primer aviso después de configurar un hook nuevo.
- **Probalo a mano antes**: `echo '{"tool_name":"Bash","tool_input":{"command":"bq rm -t ds.tabla"}}' | .claude/hooks/bloquear-destructivos.py; echo $?`.
- **Si imprimís JSON, que sea lo único en stdout.** Un `echo` en tu `~/.zshrc` que se ejecuta en shells no interactivos rompe el parseo sin avisar. Envolvelo en `if [[ $- == *i* ]]`.
- **`Stop` que bloquea en loop**: si tu hook obliga a seguir, chequeá `stop_hook_active` en el input y salí con 0 cuando sea `true`. Claude Code corta igual después de 8 bloqueos seguidos.
- **`Stop` dispara cada vez que Claude termina de responder**, no solo al "terminar la tarea". No dispara si lo interrumpiste.
- **Los hooks de tools corren también dentro de subagents**, así que tu bloqueo de `bq rm` los cubre.
- **`PreToolUse` no ve los archivos que agregás con `@`** en el prompt: esos no pasan por una tool. Para bloquear lecturas usá reglas `deny` de `Read`.
- **Un hook que da timeout no bloquea**: no confíes en un script lento como barrera.
- **Hooks de repos ajenos**: con `claude -p` los hooks de `.claude/settings.json` corren aunque nunca hayas confiado en la carpeta. Revisalos antes de automatizar sobre un repo que no es tuyo.
- **Debug**: `claude --debug-file /tmp/claude.log` y `tail -f` en otra terminal; `Ctrl+O` muestra el transcript con los resultados de cada hook.
- **`/goal <condición>`** es un atajo incluido que arma un hook de tipo `Stop` para que Claude siga trabajando hasta cumplir una condición, sin escribir JSON.

## Ver también

- [Permisos](07-permisos.md) — la primera barrera; los hooks son la segunda.
- [Skills](10-skills.md) y [Subagents](11-subagents.md) — hooks en el frontmatter.
- [Plugins](14-plugins.md) — repartir hooks al equipo.
- [Automatización](16-automatizacion.md) — hooks en corridas headless y CI.
- Documentación oficial: [Guía de hooks](https://code.claude.com/docs/en/hooks-guide) · [Referencia](https://code.claude.com/docs/en/hooks).
