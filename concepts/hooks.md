# Hooks

> verificado: 2026-10-18 · fuentes: [Hooks reference](https://code.claude.com/docs/en/hooks), [Hooks guide](https://code.claude.com/docs/en/hooks-guide), [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-configuration), [Gemini CLI hooks](https://geminicli.com/docs/hooks/), [Antigravity hooks](https://antigravity.google/docs/hooks/)

Un hook es un comando (u otro handler) que el **harness** ejecuta automáticamente en un punto fijo del ciclo del agent: antes de usar un tool, después de usarlo, al terminar un turno, etc. Garantiza que algo pase **siempre**, sin depender de que el modelo se acuerde.

## Cuándo usarlo y cuándo no

**Usarlo para:**
- Formatear o lintear después de cada edit.
- Bloquear comandos peligrosos o edits a archivos protegidos.
- Notificar cuando el agent espera input.
- Re-inyectar contexto después de una compaction.
- Hacer un gate de verificación al terminar (tests en `Stop`).

**No usarlo para:**
- Decisiones de criterio: eso va en una [skill](skills.md) o en un hook de tipo `prompt`.
- Ser la única barrera de seguridad: para eso están los [permisos](tools-and-permissions.md).

## Cómo funciona

Claude Code, Copilot y Gemini CLI comparten este modelo:

```
evento → matcher (¿aplica?) → handler recibe JSON por stdin → responde con exit code / JSON
```

| Exit code | Efecto |
|---|---|
| `0` | OK. Si stdout es JSON, se interpreta como decisión. |
| `2` | **Bloquea** la acción (en los eventos que pueden bloquear). stderr llega al modelo como motivo. |
| Otro | Error que no bloquea (en Copilot `preToolUse`, en cambio, deniega). |

- **Pre-tool**: puede permitir, denegar, pedir confirmación o reescribir los argumentos.
- **Post-tool**: no puede deshacer nada, porque el tool ya se ejecutó.
- **Corre con tus permisos completos**: un hook en un repo ajeno es código ajeno.

## En Claude Code

Se configuran en `settings.json` (usuario, proyecto o local), en plugins y en el frontmatter de skills y subagents.

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "ruff format \"$CLAUDE_PROJECT_DIR\"" }] }
    ],
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "if": "Bash(rm *)", "command": ".claude/hooks/guard.sh" }] }
    ]
  }
}
```

- **Eventos más usados**: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SubagentStop`, `PreCompact`/`PostCompact`. La lista completa (más de 30) está en la [referencia](https://code.claude.com/docs/en/hooks).
- **Tipos de handler**: `command`, `http`, `mcp_tool`, `prompt` y `agent` (experimental).
- **Matcher**:
  - Distingue mayúsculas.
  - `*` o vacío coincide con todo.
  - `A|B` es una lista.
  - Cualquier otro carácter lo vuelve una regex.
  - Para los tools MCP: `mcp__<server>__.*`.
- **Decisión en `PreToolUse`**: `hookSpecificOutput.permissionDecision` = `allow | ask | deny` (y `defer`, solo con `-p`). Si varios hooks deciden: `deny` > `defer` > `ask` > `allow`.
- **Un `deny` en un hook bloquea incluso en modo bypass**. Un `allow` no saltea las reglas deny de settings.
- **Ver la config activa**: `/hooks`. Para desactivarlos todos: `disableAllHooks`.

## En otras herramientas

- **Copilot**: `.github/hooks/*.json`, eventos en camelCase (`preToolUse`, `agentStop`). `no probado`
- **Gemini CLI**: `settings.json`, eventos `BeforeTool`/`AfterTool`. Avisa si un hook del proyecto cambió desde la última vez. `no probado`
- **Antigravity**: `.agents/hooks.json`. `no probado`

## Errores comunes

- **Un `echo` en `.zshrc`** ensucia stdout y rompe el JSON que espera el harness.
- **Un hook `Stop` que no chequea `stop_hook_active`** bloquea el cierre una y otra vez, hasta que Claude Code lo corta a las 8 veces seguidas.
- **Paths relativos o scripts sin `chmod +x`**. Usar `$CLAUDE_PROJECT_DIR`.
- **Armar el JSON concatenando strings**: usar `jq`.
- **Esperar que `PostToolUse` revierta algo.**
- **`claude -p` sobre un repo ajeno**: en modo headless no hay diálogo de confianza, así que los hooks commiteados corren directo. Revisar `.claude/` antes, o usar `--settings '{"disableAllHooks": true}'`.

## Ver también

[tools-and-permissions](tools-and-permissions.md) · [skills](skills.md) · [mcp](mcp.md)
