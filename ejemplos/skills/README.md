# Skills de ejemplo

Cada subcarpeta es una skill completa, lista para copiar a `.claude/skills/<nombre>/` en un proyecto real. La estructura sigue el formato estándar: un `SKILL.md` con frontmatter (`name`, `description`) y las instrucciones en el cuerpo del archivo.

Ver [docs/08 — Skills](../../docs/08-skills.md) para la teoría (qué es una skill, cuándo conviene crear una, skill vs. `CLAUDE.md`).

## Índice

| Skill | Para qué sirve |
|---|---|
| [`revision-de-diffs/`](revision-de-diffs/SKILL.md) | Checklist consistente para revisar un diff antes de commitear o aceptar cambios generados por el agente. Operacionaliza la regla de [buenas-practicas](../../buenas-practicas/README.md#revisión-de-código-generado-antes-de-aceptar-cambios). |

Se van a ir sumando más a medida que aparezcan casos de uso reales (ver ideas pendientes en el `description` de cada skill agregada, y las categorías sugeridas en [docs/08-skills.md](../../docs/08-skills.md#ejemplos-de-buenos-casos-de-uso): checklist de release/deploy, generación de reportes, convenciones de SQL para equipos de datos).
