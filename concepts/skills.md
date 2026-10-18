# Skills

> verificado: 2026-10-18 · fuentes: [Agent Skills spec](https://agentskills.io/specification), [Equipping agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [Authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [Skills (Claude Code)](https://code.claude.com/docs/en/skills), [Copilot skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [Gemini CLI skills](https://geminicli.com/docs/cli/skills/), [Antigravity skills](https://antigravity.google/docs/skills)

Una skill es una carpeta con un `SKILL.md` (frontmatter YAML + instrucciones) y, opcionalmente, scripts y archivos de referencia. El agent la carga **solo cuando la tarea la necesita**. Es un estándar abierto (Agent Skills): Claude Code, Copilot, Gemini CLI, Antigravity, Cursor, Codex y otros leen el mismo formato ([adoptantes](https://agentskills.io/home)).

## Cuándo usarla y cuándo no

Para elegir entre skill, memory y hook, ver la tabla de [memory](memory.md#cuándo-usarla-y-cuándo-no). Además:

- Una regla obligatoria no va en una skill: se puede ignorar o perder al compactar.
- Una tarea con output voluminoso va en un [subagent](subagents.md): la skill corre en el contexto principal.
- Una operación frágil o determinista va como script dentro de la skill, no como código que genere el modelo.

## Cómo funciona

**Progressive disclosure** en 3 niveles:

1. **Metadata**: al iniciar la sesión se cargan `name` + `description` de todas las skills (~100 tokens cada una).
2. **Instrucciones**: el cuerpo de `SKILL.md` se carga cuando el modelo decide que la skill aplica, comparando la tarea con la `description`.
3. **Recursos**: `scripts/`, `references/` y `assets/` se cargan bajo demanda. Los scripts **se ejecutan** sin cargarse en el contexto: solo su output consume tokens.

```
mi-skill/
├── SKILL.md
├── scripts/validar.py
└── references/convenciones.md
```

```markdown
---
name: mi-skill            # a-z0-9-, igual al nombre de la carpeta
description: Valida modelos SQL contra las convenciones del equipo. Usar al crear o revisar un modelo.
---

1. Correr `python ${CLAUDE_SKILL_DIR}/scripts/validar.py <archivo>`.
2. Si falla, ver references/convenciones.md.
```

- **Spec**: `description` ≤1024 caracteres (obligatorio). Recomendado: cuerpo < 500 líneas y referencias a **un solo nivel** desde `SKILL.md`. Claude Code trunca `description` + `when_to_use` a 1536 caracteres en el listado.
- **Validar**: `skills-ref validate ./mi-skill`.

## En Claude Code

- **Rutas**: `~/.claude/skills/<n>/` (personal), `.claude/skills/<n>/` (proyecto) y la carpeta `skills/` de un [plugin](https://code.claude.com/docs/en/plugins).
- **Invocación manual**: `/nombre`. Una skill y un slash command en `.claude/commands/` producen el mismo `/comando`; la skill además suma carpeta propia y carga automática.
- **Frontmatter propio** (además del estándar):

| Campo | Efecto |
|---|---|
| `disable-model-invocation: true` | Solo la invocás vos (por ejemplo, un deploy). |
| `user-invocable: false` | Solo la invoca el modelo. |
| `allowed-tools` | **Pre-aprueba** tools; no restringe los demás. |
| `context: fork` | Corre en un subagent. |
| `paths` | Globs que limitan cuándo se activa sola. |
| `model`, `effort` | Overrides para esa skill. |

- **Dentro de `SKILL.md`**: `$ARGUMENTS` y `${CLAUDE_SKILL_DIR}` se sustituyen al invocarla. `` !`cmd` `` inyecta la salida del comando antes de que el modelo lo lea.
- **Diagnóstico**: `/skill-doctor` muestra el costo en contexto y el uso de cada skill.

## En otras herramientas

- **Copilot**: lee `.github/skills/`, `.claude/skills/` o `.agents/skills/`. `no probado`
- **Gemini CLI / Antigravity**: `.agents/skills/`; pide confirmación antes de activar una skill. `no probado`

`.agents/skills/` es la ruta que comparten varias herramientas.

## Errores comunes

- **`description` vaga** ("ayuda con PDFs"). Tiene que decir qué hace, cuándo usarla y las palabras clave, en tercera persona. Es lo único que el modelo ve para decidir si la activa.
- **Frontmatter roto**: si el YAML es inválido, la skill se carga sin metadata: `/nombre` funciona pero nunca se activa sola. El error se ve con `claude --debug` o `claude plugin validate .claude/skills`.
- **`SKILL.md` gigante o referencias anidadas**: el modelo lee parcialmente. Conviene partirla en `references/` de un solo nivel.
- **Creer que `allowed-tools` restringe**: solo pre-aprueba.
- **Skills de fuentes no confiables**: pueden ejecutar scripts y exfiltrar datos. Revisalas antes de usarlas.

## Ver también

[memory](memory.md) · [subagents](subagents.md) · [hooks](hooks.md)
