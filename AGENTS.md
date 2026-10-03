# Instrucciones para agentes en este repo

Este archivo lo leen los agentes de IA que trabajan sobre este proyecto (Claude Code vía `@AGENTS.md` desde `CLAUDE.md`, y Antigravity CLI de forma nativa). Es infraestructura del repo, no contenido de la wiki — no confundir con lo que vive en `docs/`, `buenas-practicas/`, etc.

## Qué es este repo

Wiki de referencia en español sobre **Claude Code**: cómo funciona, cómo configurarlo, buenas prácticas y casos de uso. Ver [README.md](README.md) para la estructura completa y [CONTRIBUTING.md](CONTRIBUTING.md) para las convenciones de contenido (idioma, formato, dónde va cada cosa). Cualquier agente que agregue o edite contenido de la wiki debe seguir esas convenciones — no se repiten acá para no duplicar y desincronizar.

## Roles: quién es principal y quién es secundario

- **Claude Code es el agente principal** de este repo: es quien coordina el trabajo, decide estructura, arma commits/PRs y tiene la última palabra si hay una diferencia de criterio.
- **Antigravity CLI es agente secundario**: se usa para tareas puntuales en paralelo — segunda opinión sobre un documento, revisión de consistencia, un borrador inicial de una sección, búsqueda/investigación — pero no decide solo sobre estructura del repo (carpetas, índice del README, convenciones de `CONTRIBUTING.md`). Si Antigravity detecta que algo así conviene cambiarlo, lo propone en vez de aplicarlo directo.
- Ninguno de los dos comitea directo a `main` ni fuerza cambios en el historial: todo cambio va en una rama y un Pull Request, siguiendo [GIT.md](GIT.md). Ningún agente hace `git push` a `main` ni mergea un PR sin que el usuario lo pida explícitamente.

## Cómo conviven

- **No pisarse**: si los dos van a tocar contenido al mismo tiempo, que trabajen en archivos distintos. No editar en paralelo el mismo archivo.
- **Consistencia de idioma y términos**: ambos siguen la regla de [CONTRIBUTING.md](CONTRIBUTING.md) — texto explicativo en español, términos propios de Claude Code (`skills`, `hooks`, `subagents`, `MCP`, `slash commands`, etc.) sin traducir.
- **Cambios estructurales** (nuevas carpetas, reorganizar `docs/`, tocar `README.md` o `CONTRIBUTING.md`) los coordina el agente principal con el usuario antes de aplicarlos.
- Si un agente no está seguro de si algo es su rol o no, pregunta antes de actuar en vez de asumir.

## Cómo se pasan trabajo

Hay dos canales, de más a menos directo:

1. **Delegación desde Claude Code (preferido).** Claude invoca a Gemini en modo headless y solo lectura con la skill [`delegar-a-gemini`](.claude/skills/delegar-a-gemini/SKILL.md) (`agy -p ... --mode plan`). Sirve para tareas chicas: segunda opinión, revisión de términos/links, resúmenes, borradores cortos. Gemini no edita archivos; Claude evalúa la respuesta y aplica lo que corresponda. Detalle en [docs/17-multi-agente-gemini.md](docs/17-multi-agente-gemini.md).
2. **Buzón `.agents/inbox/`.** Para revisiones que se procesan después (o cuando el usuario corre Antigravity por su cuenta), el resultado se guarda como Markdown en `.agents/inbox/YYYY-MM-DD-tema.md` en vez de aplicarse directo sobre `docs/`, `buenas-practicas/`, `casos-de-uso/`, etc.
   - Claude Code revisa `.agents/inbox/` al empezar a trabajar en este repo: lee lo pendiente, decide qué incorporar (siguiendo `CONTRIBUTING.md`) y qué descartar.
   - Un archivo procesado se borra; el rastro queda en el historial de git.

Ninguno de los dos canales cambia los roles: Antigravity no decide sobre estructura del repo.

> Nota: Gemini CLI (`gemini`) ya no funciona con cuentas individuales; se usa Antigravity CLI (`agy`).

## Backlog de trabajo grande

Cuando una tarea se reparte entre varios agentes, el agente principal deja el backlog en `.agents/backlog.md` con dueño y archivos de cada tarea, para que nadie edite archivos ajenos. Se borra cuando el trabajo se mergea.
