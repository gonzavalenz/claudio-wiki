# Diseño del proyecto

## Objetivo

Referencia técnica personal sobre **coding agents**: cómo funcionan (LLM + tools + agentic loop), cómo se extienden (`skills`, `subagents`, `hooks`, `MCP`, RAG, `mods`) y cómo aplicarlos en ingeniería y arquitectura de datos. Está pensada para consulta rápida ("¿cómo era X?"), para practicar lo aprendido y para seguir vigente con poco mantenimiento.

**No es objetivo:**
- Replicar la documentación oficial de cada herramienta.
- Tutoriales introductorios.
- Contenido que no se haya verificado o usado.

## Principios

1. **Agnóstico primero.** Cada concepto se explica en general. Lo específico va en `## En Claude Code` y `## En otras herramientas` (con fuente y `no probado` si aplica), o en `tools/` si no tiene equivalente general (por ejemplo, `mods` en Claude Code).
2. **Mínimo texto.** Una página = un concepto, con un máximo de ~150 líneas. Si algo ya está bien explicado en la documentación oficial, se enlaza en vez de reescribirse.
3. **Vigencia explícita.** Cada página declara sus fuentes y la fecha en que se verificó.
4. **Una sola fuente de verdad: Markdown.** El HTML se genera a pedido en `site/` y no se versiona.
5. **Ejemplos probados.** Lo que está en `examples/` se ejecutó en esta máquina. Si no se ejecutó, se marca `no probado`.

## Estructura

```
README.md        Objetivo + índice
DESIGN.md        Este documento: decisiones y convenciones
AGENTS.md        Reglas para agentes (CLAUDE.md lo importa)
GIT.md           Flujo de git
PREGUNTAS.md     Preguntas abiertas para el usuario
concepts/        Una página por concepto, agnóstica
tools/           Lo específico de cada herramienta (claude-code.md, ...)
practices.md     Reglas accionables: regla → por qué
examples/        Archivos copiables y probados
diagrams/        Diagramas Excalidraw (formato a definir en fase 4)
scripts/         Python: build de site/, chequeo de links
.claude/agents/  Agentes del proyecto
```

Las carpetas y los archivos se nombran en inglés. El contenido va en español y los términos técnicos se dejan en inglés, sin traducir.

Una carpeta se crea recién cuando tiene contenido.

### Conceptos

`agent`, `context`, `memory`, `tools-and-permissions`, `skills`, `subagents`, `multi-agent`, `hooks`, `mcp`, `rag`, `evals`, `costs`.

### Herramientas

- **Claude Code**: la principal. Ahí se prueba todo.
- **Gemini / Antigravity** y **GitHub Copilot**: se suman en `## En otras herramientas` cuando aporten, siempre con fuente. Lo que no se pueda probar acá se marca `no probado`.

## Plantilla de concepto

```markdown
# <Concepto>

> verificado: AAAA-MM-DD · fuentes: [oficial](url)

Definición en 1–2 frases.

## Cuándo usarlo y cuándo no
## Cómo funciona
## En Claude Code
## En otras herramientas
## Errores comunes
## Ver también
```

Las secciones que no aportan nada se omiten.

## Agentes del proyecto

Son `subagents` en `.claude/agents/`, con un prompt corto y solo los tools que necesitan. Ninguno edita contenido salvo el `visualizador`, y él solo toca el formato. Agent teams (experimental) está activado en `.claude/settings.json` para trabajar en paralelo.

| Agente | Responsabilidad |
|---|---|
| *sesión principal* | Coordina, escribe, integra y arma los PRs, guiada por `AGENTS.md`. |
| `investigador` | Busca novedades y cambios, y propone qué agregar o actualizar, con fuente. |
| `revisor` | Revisa páginas contra sus fuentes y contra este documento. |
| `seguridad` | Revisa `examples/`, configuración y scripts buscando riesgos. |
| `visualizador` | Genera `site/` y mejora el formato de los `.md`. |

## Flujo

1. `investigador` propone, con fuentes.
2. La sesión principal escribe.
3. `revisor` revisa, y `seguridad` también si el cambio toca `examples/`, `scripts/` o configuración.
4. Rama + PR según [GIT.md](GIT.md).

## Herramientas del repo

- **Markdown**: todo el contenido.
- **Python**: scripts. Stdlib salvo que haga falta otra cosa.
- **Excalidraw**: con la extensión de VS Code, sin MCP (requiere API key).
- **HTML/CSS/JS**: solo como salida generada.

## Estilo visual

Aplica a diagramas, HTML y cualquier diseño:

- Modo oscuro: fondo gris casi negro.
- Color de acento: rojo.
- Nunca combinar azul con amarillo.

## Fases

1. Base: este documento, `AGENTS.md` y agentes. ✓
2. Conceptos núcleo: `agent`, `context`, `memory`, `tools-and-permissions`, `skills`, `subagents`, `hooks`, `mcp`. ✓
3. `rag`, `multi-agent`, `evals`, `costs`, `tools/claude-code.md` (incluye `mods`) y `practices.md`. ✓
4. `scripts/build_site.py` (base: `assets/build_guia.py` de la rama `docs/mejora-integral`) y diagramas. ← actual

El RAG local sobre la wiki se descartó: la wiki entra entera en contexto, así que no lo justifica. Queda documentado en [rag](concepts/rag.md).
