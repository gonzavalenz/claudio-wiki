# Multi-agent

> verificado: 2026-10-18 · fuentes: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), [Parallel agents (Claude Code)](https://code.claude.com/docs/en/agents), [Agent teams](https://code.claude.com/docs/en/agent-teams), [Worktrees](https://code.claude.com/docs/en/worktrees), [Workflows](https://code.claude.com/docs/en/workflows), [Copilot /fleet](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/fleet), [Antigravity teamwork](https://antigravity.google/docs/teamwork), [Costs: agent teams](https://code.claude.com/docs/en/costs#agent-team-token-costs), [Don't build multi-agents (Cognition)](https://cognition.com/blog/dont-build-multi-agents), [Gemini CLI worktrees](https://geminicli.com/docs/cli/git-worktrees/), [Gemini CLI docs](https://geminicli.com/docs/)

Varios agents (o instancias del mismo) trabajan en una tarea, cada uno con su contexto. Cambia tokens y coordinación por paralelismo y especialización. La base, delegar en un [subagent](subagents.md), está en su propia página.

## Cuándo usarlo y cuándo no

**Usarlo para:**
- Trabajo realmente paralelizable e independiente: research, review desde varios ángulos, el mismo cambio en muchos archivos.
- Tareas que no entran en una sola context window.

**No usarlo para:**
- **La mayoría del coding.** Hay pocas subtareas paralelizables y muchas dependencias. Lo dice el propio post de Anthropic.
- Tareas donde las decisiones implícitas de un agent afectan a otro. Cognition (una opinión de vendor, no una fuente técnica) muestra un juego armado por dos subagents que salió inconsistente: su propuesta es un solo agent lineal con compresión de contexto.

**Costo**: un agent consume ~4x tokens frente a un chat, y un sistema multi-agent ~15x (Anthropic, en research).

## Cómo funciona

Patrones de [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), de menor a mayor autonomía:

| Patrón | Qué es |
|---|---|
| Prompt chaining | Pasos fijos en secuencia, con chequeos entre ellos |
| Routing | Clasifica el input y lo manda al handler correspondiente |
| Parallelization | Subtareas predefinidas en paralelo (sectioning) o la misma tarea varias veces (voting) |
| Orchestrator-workers | Un lead decide en runtime qué subtareas crear y delega |
| Evaluator-optimizer | Uno genera y otro critica, en loop |

Regla: arrancá por lo más simple y sumá complejidad solo si mejora un resultado medible ([evals](evals.md)).

Lecciones del research system de Anthropic:
- Escalá el esfuerzo en el prompt del lead (1 agent con 3–10 tool calls para algo simple, 2–4 subagents para comparar, más para research amplio). Sin esa guía, lanzaba 50 subagents para queries simples.
- Delegá con objetivo, formato de salida y límites precisos. Si no, los workers duplican trabajo.

## En Claude Code

| Mecanismo | Qué es | Detalle |
|---|---|---|
| [Subagents](subagents.md) | Delegación con contexto aislado | Solo le reportan al principal |
| Worktrees (`claude -w <nombre>`) | Sesiones paralelas manuales, cada una en `.claude/worktrees/<nombre>/` | `.worktreeinclude` copia `.env`. Con `-p` no se limpian solos |
| `/batch` | Skill que reparte un cambio en 5–30 subagents, cada uno en su worktree | Para cambios mecánicos masivos |
| Agent view (`claude agents`, research preview) | Panel para lanzar y seguir sesiones en paralelo | — |
| Agent teams (experimental) | Un lead + teammates + una task list compartida + mensajes entre ellos | Ver abajo |
| Dynamic workflows | Claude escribe un script JS (`agent()`, `parallel()`, `pipeline()`) y el runtime lo ejecuta | Se activa pidiéndolo ("use a workflow"), con `ultracode` en el prompt o con `/effort ultracode`. Hasta 16 agents concurrentes (menos si hay pocas CPUs) y 1.000 por corrida |

**Agent teams**:
- Se activa con `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` en `env` de settings (este repo lo tiene en `.claude/settings.json`).
- **Con la flag prendida, un subagent con nombre puede arrancar como teammate** sin que pidas un team (ver [subagents](subagents.md#errores-comunes)).
- Los teammates usan las mismas definiciones que los subagents, pero no aplican el campo `skills`.
- No aíslan en worktrees: asigná archivos distintos a cada teammate.
- Hooks `TeammateIdle`, `TaskCreated` y `TaskCompleted`: con exit 2 bloquean y devuelven feedback.
- Limitaciones: un team por sesión, no hay teams anidados, `/resume` y `/rewind` no restauran teammates in-process, y no funciona con `-p` ni con el Agent SDK.
- Recomendación oficial: 3–5 teammates, empezando por research o review.

## En otras herramientas

- **Copilot CLI**: `/fleet` orquesta subagents en paralelo, cada uno con su contexto. `no probado`
- **Antigravity**: `/teamwork-preview` (planes pagos, App y CLI) con roles orchestrator, explorers, workers y critic. Coordina vía artifacts. `no probado`
- **Gemini CLI**: worktrees experimentales (`gemini -w`). Para el tier gratis y Google One fue reemplazado por Antigravity CLI el 2026-06-18. `no probado`

## Errores comunes

- **Multi-agent por default**: multiplica el costo sin garantizar una mejora. Medilo.
- **Dos agents editando el mismo archivo**: sin worktrees ni dueños claros, gana el último que escribe.
- **Delegar sin contexto ni formato de salida**: trabajo duplicado y resúmenes inútiles.
- **No apagar los teammates al terminar**: cada uno sigue consumiendo tokens hasta que sale.

## Ver también

[subagents](subagents.md) · [costs](costs.md) · [evals](evals.md)
