# Subagents de ejemplo

| Archivo | Para qué | Modelo |
|---|---|---|
| [`revisor-dbt.md`](revisor-dbt.md) | Revisa modelos dbt nuevos/cambiados contra convenciones, tests y costo (dry run) | `sonnet` |
| [`explorador-lineage.md`](explorador-lineage.md) | Responde "de dónde sale" / "quién usa" un modelo o columna | `haiku` (tarea mecánica, barata) |

## Instalación

```bash
mkdir -p .claude/agents
cp ejemplos/agents/revisor-dbt.md ejemplos/agents/explorador-lineage.md .claude/agents/
```

Proyecto: `.claude/agents/` (se commitea). Personal, para todos tus repos: `~/.claude/agents/`. Claude Code detecta cambios en esos archivos en caliente; si es la primera vez que creás la carpeta, reiniciá la sesión.

## Cómo se usan

- **Automático**: Claude delega solo cuando la tarea encaja con la `description`. Por eso la `description` dice *cuándo* usarlo ("usalo proactivamente después de...").
- **Explícito**: "usá el subagent revisor-dbt para revisar fct_ventas" (Claude decide), o `@agent-revisor-dbt revisá fct_ventas` / elegirlo con `@` del typeahead (garantiza que corre ese).
- **Toda la sesión como ese agente**: `claude --agent revisor-dbt`.
- `/agents` te recuerda cómo crearlos; `/tasks` muestra los que están corriendo y en qué modelo.

## Frontmatter (campos verificados)

| Campo | Obligatorio | Notas |
|---|---|---|
| `name` | Sí | Identificador único, sin `:` |
| `description` | Sí | Cuándo delegar. Es lo que lee Claude para decidir |
| `tools` | No | Lista separada por comas. Si lo omitís, hereda todas. Sin `Edit`/`Write` = no modifica archivos |
| `disallowedTools` | No | Tools a sacar de las heredadas |
| `model` | No | `sonnet`, `opus`, `haiku`, `fable`, un ID completo o `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | Corta al subagent después de N turnos |
| `skills` | No | Skills que se precargan enteras en su contexto |
| `mcpServers` | No | Servidores MCP disponibles para este subagent |
| `hooks` | No | Hooks que corren solo mientras está activo |
| `memory` | No | `user`, `project` o `local`: memoria persistente entre sesiones |
| `isolation` | No | `worktree`: trabaja en una copia aislada del repo |
| `effort`, `color`, `background` | No | Esfuerzo, color en la UI, correr siempre en background |

Los campos con varias palabras van en camelCase y tienen que coincidir exacto: un campo mal escrito se ignora **sin error**.

## Trucos

- Un subagent **no ve tu conversación**: arranca con su system prompt (el cuerpo del `.md`) más lo que Claude le pase al delegar. Lo que necesite saber, ponelo en el prompt o en el archivo.
- Devuelve un resumen, no todo lo que leyó: ideal para exploraciones que llenarían tu contexto.
- `model: haiku` para tareas mecánicas (buscar, listar, resumir) ahorra bastante.
- Si el subagent no tiene `Edit`/`Write` pero sí `Bash`, igual puede modificar cosas por shell: los `deny` de [settings](../settings/README.md) y la [guardia de BigQuery](../hooks/README.md) aplican también dentro de los subagents.

Ver [11 — Subagents](../../docs/11-subagents.md).
