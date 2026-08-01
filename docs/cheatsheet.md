# Cheatsheet / referencia rápida

> Pensado para consulta rápida, no para leer de corrido. Cada fila linkea al capítulo con el detalle completo.

## Comandos built-in más usados

| Comando | Qué hace | Más info |
|---|---|---|
| `/help` | Ayuda y lista completa de comandos disponibles | [06](06-comandos-slash.md) |
| `/init` | Analiza el repo y genera/actualiza `CLAUDE.md` | [04](04-instalacion.md), [05](05-memoria.md) |
| `/login` | Autenticación de la cuenta | [04](04-instalacion.md) |
| `/fast` | Modo de salida más rápida (según modelo) | [03](03-modelos.md) |

## Archivos y carpetas clave de un proyecto

| Archivo/carpeta | Para qué sirve | Versionado |
|---|---|---|
| `CLAUDE.md` | Contexto permanente del proyecto | Sí |
| `.claude/settings.json` | Permisos y config compartida del equipo | Sí |
| `.claude/settings.local.json` | Permisos/config personal | No (gitignored) |
| `.claude/skills/` | Skills propias del proyecto | Sí |
| `.claude/commands/` | Slash commands custom del proyecto | Sí |

Ver [13 — Estructura de proyecto](13-estructura-de-proyecto.md).

## Permisos: acciones que siempre conviene confirmar

- Operaciones destructivas (borrar archivos/branches, `rm -rf`).
- Difíciles de revertir (`push --force`, `reset --hard`, `amend` de commits publicados).
- Visibles para otros / estado compartido (push, PRs, mensajes).
- Saltear controles de seguridad (`--no-verify`, `--no-gpg-sign`).

Ver [07 — Permisos](07-permisos.md).

## Modelo: cuál usar

| Situación | Modelo sugerido |
|---|---|
| Tarea ambigua, multi-paso, alto costo de error | Más grande/capaz |
| Trabajo de desarrollo día a día | Intermedio (default) |
| Tarea mecánica, acotada, o muchas corridas en paralelo | Más chico/rápido |

Ver [03 — Modelos](03-modelos.md).

## `CLAUDE.md` vs. skill vs. hook

| Mecanismo | Cuándo usarlo |
|---|---|
| `CLAUDE.md` | Contexto que aplica *siempre* en ese repo |
| Skill | Procedimiento que aplica *a veces*, con pasos definidos |
| Hook | Regla que tiene que cumplirse *sí o sí*, sin depender del criterio del modelo |

Ver [05](05-memoria.md), [08](08-skills.md), [10](10-hooks.md).

## Subagentes: cuándo delegar

- Investigación abierta que toma varias búsquedas/lecturas.
- Se puede paralelizar en tareas independientes.
- Se busca una segunda opinión sin sesgo del contexto ya acumulado.
- **No delegar entendimiento**: siempre dar al subagente todo el contexto que necesita para trabajar solo.

Ver [09 — Subagentes](09-subagentes.md).

## Flujo recomendado ante una tarea nueva

1. Explorar (directo o con subagente si es una búsqueda abierta).
2. Planear el enfoque si hay ambigüedad real (modo plan).
3. Ejecutar en pasos verificables.
4. Revisar el diff y correr tests/verificación real antes de dar por terminado.

Ver [14 — Flujos de trabajo](14-flujos-de-trabajo.md).

## Costos: para no gastar de más

- Modelo acorde a la tarea, no siempre el más grande.
- Delegar exploración pesada a subagentes en vez de inflar el contexto principal.
- Contexto completo desde el pedido inicial (evita rondas de ida y vuelta).
- Cerrar sesiones/tareas que ya cumplieron su propósito.

Ver [15 — Costos](15-costos.md).
