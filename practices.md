# Prácticas

> verificado: 2026-10-18 · fuentes: [Best practices](https://code.claude.com/docs/en/best-practices), [Memory](https://code.claude.com/docs/en/memory), [MCP](https://code.claude.com/docs/en/mcp), [Checkpointing](https://code.claude.com/docs/en/checkpointing), [Worktrees](https://code.claude.com/docs/en/worktrees), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Costs](https://code.claude.com/docs/en/costs)

Reglas accionables con su motivo. Los ejemplos son de Claude Code, pero las reglas aplican a cualquier coding agent.

## Contexto

- **Usá `/clear` entre tareas que no tienen relación.** El contexto viejo compite por atención y además se paga. → [context](concepts/context.md)
- **Después de dos correcciones fallidas, hacé `/clear` y escribí un prompt mejor.** Los intentos fallidos contaminan el contexto.
- **Si existe un CLI maduro (`gh`, `bq`, `dbt`), usalo antes que un MCP.** Los docs dicen que los CLI son "the most context-efficient way". Es un trade-off, no una regla absoluta: con tool search, cada server MCP conectado carga solo sus nombres e instrucciones. MCP gana con OAuth, datos estructurados o sistemas sin CLI. → [mcp](concepts/mcp.md)
- **Mandá los outputs largos (tests, logs) a un subagent o filtralos con un hook.** Así solo vuelve lo relevante. → [subagents](concepts/subagents.md), [hooks](concepts/hooks.md)

## Memory (`CLAUDE.md` / `AGENTS.md`)

- **Mantenelo por debajo de ~200 líneas y podalo con un solo criterio: "Would removing this cause Claude to make mistakes?".** Se carga en cada turno. → [memory](concepts/memory.md)
- **Los imports `@` no ahorran contexto: los archivos importados también se cargan al inicio.** Para cargar algo bajo demanda están las rules con `paths:` o las [skills](concepts/skills.md).
- **No pegues un árbol de archivos.** Los docs piden excluir las descripciones archivo por archivo y todo lo que cambia seguido: el agent navega just-in-time con glob/grep, y un árbol se desactualiza y cuesta tokens en cada turno. Lo que sí sirve, aunque es inferencia y no lo dicen los docs, son 3–5 líneas sobre carpetas no obvias que expliquen *por qué* existen.
- **Las reglas van en el archivo, no en el chat.** Lo que se dice en el chat se pierde al compactar.

## Planificar y verificar

- **Usá plan mode solo si el cambio toca varios archivos o el enfoque no es obvio.** "If you could describe the diff in one sentence, skip the plan": planificar tiene overhead.
- **En features grandes, pedí que el agent te entreviste, después armá un `SPEC.md` y recién ahí abrí una sesión nueva para implementar.** El spec queda como contexto limpio y revisable.
- **Dale un check ejecutable (tests, linter, `dbt build`, un dry-run) y pedile evidencia, no afirmaciones.** Sin un check, "looks done" es la única señal que tiene. Se puede escalar así: el check en el prompt → `/goal` → Stop hook → subagent revisor.
- **Pedile al revisor solo gaps de correctitud.** Un revisor casi siempre encuentra algo, y si perseguís todo terminás en over-engineering.

## Seguridad

- **La red de seguridad es git, no `/rewind`.** El checkpointing no cubre los cambios hechos por Bash, los de subagents ni las ediciones externas. Hacé commits chicos y trabajá en ramas.
- **Para trabajar en paralelo, usá worktrees.** `claude -w <nombre>` crea uno en `.claude/worktrees/`: agregá esa carpeta a `.gitignore`. Para copiar `.env` u otros archivos ignorados está `.worktreeinclude`. → [multi-agent](concepts/multi-agent.md)
- **Antes de instalar un plugin, mod o MCP, leelo.** Los mods corren sin sandbox y los MCP pueden ser un vector de prompt injection. → [tools/claude-code](tools/claude-code.md#mods)

## Costos

- **Usá Sonnet por defecto, Haiku en subagents mecánicos y Opus para razonamiento difícil.** → [costs](concepts/costs.md)
- **No cambies de modelo ni de effort a mitad de una tarea.** Se invalida el cache (con excepciones, ver [context](concepts/context.md)).
