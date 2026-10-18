# Coding agents — referencia técnica

Wiki personal sobre agentes de IA para desarrollo: cómo funcionan, cómo extenderlos (`skills`, `subagents`, `hooks`, `MCP`, RAG, `mods`) y cómo aplicarlos en ingeniería de datos. Agnóstica, con Claude Code como herramienta principal de ejemplo.

> 🚧 En reconstrucción. Ver el plan en [DESIGN.md](DESIGN.md#fases).

## Índice

| Concepto | En una línea |
|---|---|
| [agent](concepts/agent.md) | LLM + tools en un loop; cuándo conviene y cuándo no |
| [context](concepts/context.md) | La context window, compaction y caching |
| [memory](concepts/memory.md) | `AGENTS.md` / `CLAUDE.md`: instrucciones persistentes |
| [tools-and-permissions](concepts/tools-and-permissions.md) | Modos, reglas allow/ask/deny y sandbox |
| [skills](concepts/skills.md) | Procedimientos que se cargan a demanda |
| [subagents](concepts/subagents.md) | Delegar con contexto aislado |
| [hooks](concepts/hooks.md) | Reglas deterministas en el ciclo del agent |
| [mcp](concepts/mcp.md) | Protocolo para conectar tools y datos externos |
| [multi-agent](concepts/multi-agent.md) | Patrones, agent teams y worktrees; cuándo no conviene |
| [rag](concepts/rag.md) | Retrieval: agentic search vs embeddings; RAG local con DuckDB |
| [evals](concepts/evals.md) | Medir prompts, skills y agents |
| [costs](concepts/costs.md) | De qué depende el costo y cómo medirlo |

| Otras páginas | |
|---|---|
| [practices](practices.md) | Reglas accionables: regla → por qué |
| [tools/claude-code](tools/claude-code.md) | Lo exclusivo de Claude Code: `mods`, plugins, `/rewind`, `/goal`, review |

## Repo

- [DESIGN.md](DESIGN.md): objetivo, estructura y convenciones.
- [AGENTS.md](AGENTS.md): reglas para agentes.
- [GIT.md](GIT.md): flujo de git.
