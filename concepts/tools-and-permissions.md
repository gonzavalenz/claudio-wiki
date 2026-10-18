# Tools and permissions

> verificado: 2026-10-18 · fuentes: [Permissions](https://code.claude.com/docs/en/permissions), [Permission modes](https://code.claude.com/docs/en/permission-modes), [Sandboxing](https://code.claude.com/docs/en/sandboxing), [Tools reference](https://code.claude.com/docs/en/tools-reference), [Auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode), [Copilot CLI tools](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools), [Antigravity permissions](https://antigravity.google/docs/permissions)

Los tools son las acciones que el modelo puede pedir: leer y editar archivos, ejecutar shell, web, [MCP](mcp.md), [subagents](subagents.md). El modelo de permisos decide qué corre solo, qué pide aprobación y qué se bloquea. Lo hace cumplir el **harness**, no el modelo.

## Cómo funciona

Hay tres capas, que se combinan como defensa en profundidad:

| Capa | Qué controla | Límite |
|---|---|---|
| **Modo** | El comportamiento base: preguntar todo, aceptar edits, solo planificar, auto, bypass. | — |
| **Reglas** `allow / ask / deny` | Tools y patrones concretos. Precedencia: **deny > ask > allow**. | Se aplican sobre el *texto* del comando. `sh -c '…'` o `/bin/rm` las evaden. |
| **Sandbox del SO** | A qué archivos y hosts llega un comando de shell, sin importar el texto. | Solo cubre shell. |

**Prompt injection**: texto con instrucciones escondido en contenido no confiable (web, archivos, outputs de MCP) que intenta redirigir al agent. La defensa principal es el entorno (sandbox, red limitada), no el prompt.

**Prompt fatigue**: la gente aprueba ~93% de los prompts. La solución no es aprobar a ciegas sino usar allowlists, sandbox o auto mode.

## En Claude Code

**Modos** (`Shift+Tab`, `--permission-mode` o `permissions.defaultMode`):

| Modo | Uso |
|---|---|
| `default` (Manual) | Pregunta antes de editar, ejecutar shell o acceder a la red. Las lecturas no preguntan. |
| `acceptEdits` | Edita sin preguntar. |
| `plan` | Solo lee y planifica. |
| `auto` (default interactivo desde v2.1.283) | Un clasificador aprueba o bloquea. En la evaluación de Anthropic dejó pasar ~17% de acciones overeager reales: no usarlo como único control en infra crítica. |
| `dontAsk` | Deniega todo lo que preguntaría. Para CI; solo con `--permission-mode`, no aparece en `Shift+Tab`. |
| `bypassPermissions` | Saltea los prompts; las reglas deny siguen aplicando. Solo en contenedor o VM aislada. |

**Reglas** (en `settings.json` o con `/permissions`):

```json
{
  "permissions": {
    "allow": ["Bash(uv run pytest *)", "Bash(git log *)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Read(./.env)", "Bash(rm -rf *)"]
  }
}
```

- **`Bash`**:
  - El `*` va después del subcomando (`Bash(git log *)`, no `Bash(git *)`).
  - Cada subcomando unido con `&&`, `|` o `;` tiene que coincidir por separado.
- **`Read`/`Edit`**:
  - Usan sintaxis gitignore.
  - `//ruta` es absoluta; `/ruta` es relativa **al archivo de settings**.
  - Las reglas `Write(...)` se ignoran.
- **Deny con solo el nombre de un tool** (`"Bash"`): saca el tool del contexto.
- **Precedencia de settings**: managed > CLI > `.claude/settings.local.json` > `.claude/settings.json` > `~/.claude/settings.json`. Un deny no se puede revertir desde otro nivel.
- **Protected paths** (`.git`, `.claude`, `.mcp.json`, `.zshrc`…): nunca se auto-aprueban, salvo en bypass.
- **Sandbox** (`/sandbox`, apagado por default):
  - Usa Seatbelt en macOS.
  - Por default **puede leer `~/.ssh` y `~/.aws`**: configurá `sandbox.filesystem.denyRead` (o `sandbox.credentials`).
  - No cubre Read, Edit, WebFetch, MCP ni hooks.
- Un [hook](hooks.md) `PreToolUse` puede bloquear por encima de cualquier allow.

## En otras herramientas

- **Copilot CLI**:
  - Flags `--allow-tool='shell(git:*)'` y `--deny-tool`. Deny siempre gana.
  - `--yolo` habilita todo.
  - `no probado`
- **Antigravity**:
  - Reglas `action(target)` con precedencia deny > ask > allow.
  - Presets Default (sandbox, sin red), Request Review y Turbo.
  - `no probado`

## Errores comunes

- **Creer que `deny: Bash(curl *)` bloquea la red**: para eso está el sandbox.
- **Escribir `/Users/x/archivo` pensando que es absoluto**: hace falta `//`.
- **Usar `Bash(git *)` cuando querías solo `git log`.**
- **Suponer que el sandbox protege credenciales o cubre MCP.**
- **Usar `bypassPermissions` fuera de un contenedor**: queda expuesto a prompt injection.
- **Poner `auto` en el `.claude/settings.json` del proyecto**: no tiene efecto. Va en el settings de usuario.

## Ver también

[hooks](hooks.md) · [mcp](mcp.md) · [agent](agent.md)
