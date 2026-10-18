# Subagents

> verificado: 2026-10-18 · fuentes: [Subagents (Claude Code)](https://code.claude.com/docs/en/sub-agents), [Agent teams](https://code.claude.com/docs/en/agent-teams), [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/), [VS Code subagents](https://code.visualstudio.com/docs/copilot/agents/subagents), [Antigravity subagents](https://antigravity.google/docs/subagents), [Copilot custom agents](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents), [Gemini CLI docs](https://geminicli.com/docs/)

Un subagent es un agent especializado al que el agent principal le delega una tarea. Corre en **su propia context window**, con su propio system prompt, tools y modelo, y **devuelve solo un resumen**.

## Cuándo usarlo y cuándo no

**Usarlo para:**
- Tareas laterales que inundarían el contexto principal: búsquedas amplias, logs, suites de tests.
- Investigar en paralelo áreas independientes.
- Restringir tools, por ejemplo un revisor de solo lectura.
- Usar un modelo más barato para trabajo mecánico.

**No usarlo para:**
- Trabajo iterativo o que comparte contexto entre fases.
- Cambios rápidos: un subagent arranca en frío, así que suma latencia y tokens.

| | Skill | Subagent | Agent team |
|---|---|---|---|
| Contexto | El principal | Aislado | Una instancia por teammate |
| Comunicación | — | Solo le reporta al agent principal | Los teammates se mensajean entre sí |
| Costo | Bajo | Medio | Alto |

## Cómo funciona

- Se define en un `.md` con frontmatter. El cuerpo del archivo es el system prompt. Este formato es casi igual en Claude Code, Gemini CLI, Antigravity y Copilot.
- El agent principal delega automáticamente según la `description`, o porque se lo pedís de forma explícita.
- **No hereda el historial de la conversación**: el prompt de delegación tiene que traer el objetivo, el contexto, las restricciones y el formato de salida.
- Lo que devuelve se suma al contexto principal. Pedile un resumen corto.

## En Claude Code

```markdown
---
name: revisor
description: Revisa cambios contra las convenciones. Usar después de editar.
tools: Read, Grep, Glob        # allowlist; sin este campo hereda todos
model: sonnet                  # sonnet | opus | haiku | inherit | ID completo
---

Revisá los archivos indicados y devolvé hallazgos con archivo:línea.
```

- **Rutas**, de mayor a menor prioridad: managed settings → flag `--agents` (JSON) → `.claude/agents/` (proyecto) → `~/.claude/agents/` (usuario) → plugin.
- **Campos útiles**: `disallowedTools`, `permissionMode`, `maxTurns`, `skills` (las precarga), `memory`, `isolation: worktree`, `background`.
- **Built-ins**: `Explore` y `Plan` (solo lectura, no leen `CLAUDE.md`) y `general-purpose`.
- **Invocación**: en lenguaje natural, con `@agent-<nombre>`, o para toda la sesión con `claude --agent <nombre>`.
- **Validar**: `claude plugin validate .claude/agents`.
- **Fork** (`/subtask`): a diferencia de un subagent, hereda **toda** la conversación.
- **Carga**: un archivo nuevo en un directorio que no existía al iniciar la sesión no se detecta hasta reiniciar.

## En otras herramientas

- **Gemini CLI**: `.gemini/agents/*.md`, se invoca con `@nombre`. Para el tier gratis y Google One fue reemplazado por Antigravity CLI (2026-06-18). `no probado`
- **Antigravity**: `.agents/agents/`. Si no declarás `tools`, el default es **ninguno**. `no probado`
- **Copilot**: "custom agents" en `.github/agents/`. En VS Code se llaman `.agent.md`. `no probado`

## Errores comunes

- **Delegar sin contexto**: el subagent no vio la conversación.
- **Typos en el frontmatter**: los campos desconocidos se ignoran sin avisar. Sin `name`, el archivo se toma como documentación; sin `description`, se descarta. Las dos cosas se ven solo en `claude --debug`.
- **Creer que `skills` restringe**: solo precarga. Para bloquear skills hay que sacar `Skill` de `tools`.
- **`permissionMode` en el subagent**: se ignora si la sesión principal está en `acceptEdits`, auto o bypass.
- **Con agent teams activado**: un subagent con nombre puede arrancar como teammate.

## Ver también

[skills](skills.md) · [context](context.md)
