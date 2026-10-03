# Claude Code — guía práctica en español

Todo lo que hay que saber para sacarle el máximo jugo a **Claude Code**: cómo funciona, cómo configurarlo, buenas prácticas, trucos, `skills`, `subagents`, `hooks`, `MCP`, automatización y trabajo con otros agentes. Ejemplos orientados a un stack de datos (Python, GCP, BigQuery, dbt, Airflow).

No es documentación oficial de Anthropic: es una base de conocimiento propia, verificada contra la [documentación oficial](https://code.claude.com/docs).

**Versión visual:** abrí [`assets/index.html`](assets/index.html) en el navegador (doble clic, sin instalar nada).

## Empezá acá

Si tenés una hora, leé esto en orden y ya trabajás mejor que la mayoría:

1. [Instalación y primeros pasos](docs/03-instalacion.md) — instalar, `/init`, primera sesión.
2. [Contexto](docs/05-contexto.md) — la regla que más impacta en la calidad: contexto limpio, `/clear`, `/compact`.
3. [Memoria (`CLAUDE.md`)](docs/06-memoria.md) — que no tengas que reexplicar el proyecto.
4. [Plan mode y checkpoints](docs/09-plan-mode-y-checkpoints.md) — explorar → planificar → implementar → commitear.
5. [Buenas prácticas](buenas-practicas/README.md) — los mandamientos, en una página.

Después, tené a mano el [cheatsheet](docs/cheatsheet.md).

## Índice

### 1 · Entender
1. [Fundamentos: LLM, agente y el bucle agéntico](docs/01-fundamentos.md)
2. [Qué es Claude Code y dónde vive](docs/02-que-es-claude-code.md)
3. [Instalación y primeros pasos](docs/03-instalacion.md)
4. [Modelos y esfuerzo: cuál usar para qué](docs/04-modelos.md)
5. [Contexto: el recurso que más importa](docs/05-contexto.md)

### 2 · Configurar
6. [Memoria: `CLAUDE.md` y compañía](docs/06-memoria.md)
7. [Permisos: cuánta autonomía le das](docs/07-permisos.md)
8. [Slash commands y atajos de teclado](docs/08-comandos-slash.md)
9. [Plan mode y checkpoints](docs/09-plan-mode-y-checkpoints.md)

### 3 · Extender
10. [Skills: empaquetar procedimientos](docs/10-skills.md)
11. [Subagents: delegar sin ensuciar el contexto](docs/11-subagents.md)
12. [Hooks: reglas que siempre se cumplen](docs/12-hooks.md)
13. [MCP: conectar herramientas externas](docs/13-mcp.md)
14. [Plugins: compartir todo lo anterior](docs/14-plugins.md)

### 4 · Escalar
15. [Paralelismo y worktrees](docs/15-paralelismo-y-worktrees.md)
16. [Automatización: headless, CI y tareas programadas](docs/16-automatizacion.md)
17. [Multi-agente: delegar tareas chicas a Gemini](docs/17-multi-agente-gemini.md)
18. [Arquitecturas de integración](docs/18-arquitecturas-de-integracion.md)

### 5 · Día a día
19. [Estructura de proyecto](docs/19-estructura-de-proyecto.md)
20. [Flujos de trabajo](docs/20-flujos-de-trabajo.md)
21. [Costos](docs/21-costos.md)

### Referencia
- [Cheatsheet](docs/cheatsheet.md) — comandos, atajos y rutas en una página.
- [Buenas prácticas](buenas-practicas/README.md) — regla → por qué → cómo.
- [Ejemplos copiables](ejemplos/README.md) — `CLAUDE.md`, `settings.json`, `hooks`, `skills`, `subagents`, `MCP`.
- [Casos de uso](casos-de-uso/README.md) — escenarios resueltos de punta a punta.
- [Git básico](docs/git-basico.md) — lo mínimo para trabajar seguro con un agente.

## Estructura del repo

```
docs/              Guía conceptual, un capítulo por tema (5 partes).
buenas-practicas/  Reglas accionables: qué hacer, qué evitar y por qué.
casos-de-uso/      Escenarios reales resueltos de punta a punta.
ejemplos/          Configuraciones y archivos listos para copiar.
assets/            Versión visual en HTML (guía + 32 trucos), sin build.
context/           Stack propio, para orientar los ejemplos.
.claude/skills/    Skills del propio repo (ej. delegar-a-gemini).
.agents/           Coordinación entre agentes (inbox, backlog).
```

## Cómo contribuir

Convenciones de contenido en [CONTRIBUTING.md](CONTRIBUTING.md), flujo de git en [GIT.md](GIT.md) y reglas para agentes (Claude Code + Gemini) en [AGENTS.md](AGENTS.md).
