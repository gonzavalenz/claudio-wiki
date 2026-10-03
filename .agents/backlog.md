# Backlog — mejora integral de la wiki

Rama: `docs/mejora-integral`. Coordina Claude Code (agente principal). Cada tarea tiene dueño y archivos propios: **nadie edita archivos de otra tarea**.

## Objetivo

Que la wiki sea la guía práctica para sacarle el máximo jugo a Claude Code: conceptos verificados contra la documentación oficial (`https://code.claude.com/docs/en/claude_code_docs_map.md`), buenas prácticas, trucos, MCP, skills, subagents, hooks, plugins, automatización y trabajo con otros agentes (Gemini vía Antigravity CLI). Sencilla, escaneable, con ejemplos copiables del stack de datos (Python, GCP, BigQuery, dbt, Airflow — ver `context/stack.md`).

## Mapa final de `docs/` (ya renombrado con `git mv`)

| Parte | Archivo | Estado |
|---|---|---|
| 1 · Entender | `01-fundamentos.md` | reescribir |
| | `02-que-es-claude-code.md` | reescribir |
| | `03-instalacion.md` (antes 04) | reescribir |
| | `04-modelos.md` (antes 03) | reescribir |
| | `05-contexto.md` | **nuevo** — context window, `/context`, `/compact`, `/clear`, `/resume`, sesiones |
| 2 · Configurar | `06-memoria.md` (antes 05) | reescribir |
| | `07-permisos.md` | reescribir |
| | `08-comandos-slash.md` (antes 06) | reescribir |
| | `09-plan-mode-y-checkpoints.md` | **nuevo** — plan mode, `Esc`, `/rewind`, checkpoints |
| 3 · Extender | `10-skills.md` (antes 08) | reescribir |
| | `11-subagents.md` (antes 09) | reescribir |
| | `12-hooks.md` (antes 10) | reescribir |
| | `13-mcp.md` (antes 11) | reescribir |
| | `14-plugins.md` | **nuevo** — plugins y marketplaces |
| 4 · Escalar | `15-paralelismo-y-worktrees.md` | **nuevo** |
| | `16-automatizacion.md` | **nuevo** — headless `claude -p`, GitHub Actions, `/loop`, tareas programadas, Agent SDK |
| | `17-multi-agente-gemini.md` | **nuevo** — delegar tareas chicas a Gemini vía `agy -p` |
| | `18-arquitecturas-de-integracion.md` (antes 12) | revisar |
| 5 · Día a día | `19-estructura-de-proyecto.md` (antes 13) | revisar |
| | `20-flujos-de-trabajo.md` (antes 14) | reescribir |
| | `21-costos.md` (antes 15) | reescribir |
| Referencia | `cheatsheet.md`, `git-basico.md` | actualizar / dejar |

## Plantilla de capítulo (para todos los `docs/`)

```markdown
# Título

> **En 30 segundos:** 2–3 líneas con la idea central.

## Qué es / cómo funciona
## Cómo se usa        (comandos, rutas, config copiable)
## Ejemplo            (stack de datos)
## Trucos y errores comunes
## Ver también        (links a otros capítulos / ejemplos)
```

## Tareas

| ID | Tarea | Dueño | Archivos |
|---|---|---|---|
| T1 ✅ | Parte 1 + Parte 2 de docs (01–09) | subagent `docs-base` | `docs/01`…`docs/09` |
| T2 ✅ | Parte 3 + Parte 4 de docs (10–18, salvo 17) | subagent `docs-extender` | `docs/10`…`docs/16`, `docs/18` |
| T3 | Ejemplos copiables + buenas prácticas + cheatsheet + casos de uso + 19–21 | subagent `practica` | `ejemplos/**`, `buenas-practicas/**`, `casos-de-uso/**`, `docs/cheatsheet.md`, `docs/19`–`21` |
| T4 ✅ | Rediseño del sitio (rojo/negro/gris/blanco) | subagent `sitio` | `assets/**` |
| T5 ✅ | Integración con Gemini (Antigravity CLI): skill de delegación + capítulo 17 + `AGENTS.md` | Claude Code (principal) | `.claude/skills/**`, `docs/17`, `AGENTS.md`, `.agents/**` |
| T6 ✅ | README (portada + ruta de aprendizaje), `CONTRIBUTING.md` | Claude Code (principal) | `README.md`, `CONTRIBUTING.md` |
| T7 ✅ | Revisión de consistencia de términos y links | Gemini vía `agy -p` (solo lectura) → `.agents/inbox/` | — |
| T8 ✅ | Sincronizar el contenido de la guía HTML con los docs nuevos | subagent `sitio` (2ª pasada) | `assets/**` |
| T9 ✅ | Revisión final, commit y PR | Claude Code (principal) | — |
