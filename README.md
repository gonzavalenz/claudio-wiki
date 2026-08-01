# Claude Code — Guía, buenas prácticas y casos de uso

Este repo es una wiki de referencia sobre **Claude Code**: cómo funciona, cómo configurarlo, buenas prácticas de uso y casos de uso reales, pensada para ir creciendo con el tiempo a medida que sumamos experiencia usándolo.

No es documentación oficial de Anthropic — es una base de conocimiento propia, con nuestras convenciones, ejemplos y decisiones.

## Estado

🚧 En construcción. La estructura ya está armada; el contenido se va completando de a poco.

## Estructura del repo

```
docs/                 Guía conceptual, capítulo por capítulo (fundamentos, modelos, memoria, skills, hooks, MCP, etc.)
buenas-practicas/      Reglas y recomendaciones de uso ("los mandamientos"): qué hacer y qué evitar, y por qué.
casos-de-uso/          Escenarios reales resueltos con Claude Code, de punta a punta.
ejemplos/              Configuraciones, prompts, comandos y snippets reutilizables (CLAUDE.md, hooks, skills, slash commands).
assets/                Material de referencia no versionado como código (ej. la guía visual en HTML).
```

## Índice de la guía (`docs/`)

1. [Fundamentos: LLM, agente y el bucle agéntico](docs/01-fundamentos.md)
2. [Qué es Claude Code y dónde vive](docs/02-que-es-claude-code.md)
3. [Modelos: cuál usar para qué](docs/03-modelos.md)
4. [Instalación y primeros pasos](docs/04-instalacion.md)
5. [Memoria: que no haya que reexplicar el proyecto cada vez](docs/05-memoria.md)
6. [Comandos: los atajos con `/`](docs/06-comandos-slash.md)
7. [Permisos: cuánta autonomía le das](docs/07-permisos.md)
8. [Skills: empaquetar conocimiento y procedimientos](docs/08-skills.md)
9. [Subagentes: delegar sin ensuciar la conversación principal](docs/09-subagentes.md)
10. [Hooks: reglas que no dependen de que el modelo se acuerde](docs/10-hooks.md)
11. [MCP: conectar herramientas y datos externos](docs/11-mcp.md)
12. [Arquitecturas de integración](docs/12-arquitecturas-de-integracion.md)
13. [Estructura de proyecto para sacarle el jugo](docs/13-estructura-de-proyecto.md)
14. [Flujos de trabajo para el día a día](docs/14-flujos-de-trabajo.md)
15. [Costos y buenas prácticas de uso](docs/15-costos.md)
16. [Cheatsheet / referencia rápida](docs/cheatsheet.md)

## Convenciones

- **Idioma**: contenido en español. Los términos técnicos propios de Claude Code (`skills`, `hooks`, `subagents`, `MCP`, `slash commands`, etc.) se dejan en inglés, sin traducir, porque así se los conoce en la documentación y en la comunidad. Ver [CONTRIBUTING.md](CONTRIBUTING.md).
- **Fuente visual**: `assets/claude-code-guia-equipo-datos.html` es una guía standalone en HTML (mismo tema, formato de página única navegable) que se mantiene aparte como pieza de referencia/diseño, no como fuente de verdad del contenido escrito en `docs/`.

## Cómo contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para las convenciones de estilo y estructura antes de sumar contenido.
