# Arquitecturas de integración

> **En 30 segundos:** Claude Code se puede usar en cuatro modos: interactivo en tu terminal, en paralelo/background, como script headless y dentro de CI o en la nube. La diferencia clave entre ellos es **quién confirma las acciones riesgosas y cuándo**. Empezá siempre interactivo y automatizá recién cuando el comportamiento es predecible.

## Los cuatro modos

| Modo | Cómo se ve | Quién aprueba acciones | Detalle en |
|---|---|---|---|
| **Interactivo local** | `claude` en el repo, ida y vuelta | Vos, sobre la marcha | [Flujos de trabajo](20-flujos-de-trabajo.md) |
| **Paralelo / background** | `claude -w`, `claude --bg`, `claude agents`, subagents | Vos, cuando la sesión te avisa que necesita algo | [Paralelismo y worktrees](15-paralelismo-y-worktrees.md) |
| **Script headless** | `claude -p` en un script o pipe | Nadie: todo pre-autorizado con `--allowedTools` / modo de permisos | [Automatización](16-automatizacion.md) |
| **CI / nube** | GitHub Actions, rutinas (`/schedule`) | Nadie, y además corre con credenciales compartidas | [Automatización](16-automatizacion.md) |

## La diferencia que importa: quién confirma

- **Con una persona presente**, el [sistema de permisos](07-permisos.md) puede preguntar cuando hace falta. Preguntar es barato.
- **Sin nadie mirando**, lo que no esté pre-aprobado se niega (o, si configuraste mal, se permite de más). Todo tiene que estar definido antes: allowlist mínima, deny de lo destructivo, topes de turnos y gasto.

Por eso cuanto más a la derecha de la tabla, más conservador hay que ser con el alcance.

## Trade-offs

| Modo | Ventaja | Costo / riesgo |
|---|---|---|
| Interactivo | Máxima flexibilidad, feedback inmediato | No escala; depende de que estés presente |
| Paralelo / background | Varias tareas a la vez sin bloquearte | Multiplica tokens; hay que repartir archivos para no tener conflictos |
| Script headless | Reproducible, versionable, componible con otras CLIs | Sin ida y vuelta: el prompt y los permisos tienen que estar bien de entrada |
| CI / nube | Corre solo en cada PR, horario o evento | Un error de alcance afecta a todo el equipo; credenciales compartidas |

## Guardarraíles por modo

| Guardarraíl | Interactivo | Headless / CI |
|---|---|---|
| Reglas `deny` para lo destructivo (`bq rm`, `DROP`) | Recomendado | **Obligatorio** |
| [Hooks](12-hooks.md) de bloqueo | Recomendado | **Obligatorio** (y revisá que corran: con `--bare` no se cargan automáticamente) |
| `--allowedTools` mínimo + `--permission-mode dontAsk` | — | Sí |
| `--max-turns`, `--max-budget-usd`, timeout del job | — | Sí |
| Credenciales de solo lectura (cuenta de servicio, usuario `readonly`) | Conveniente | Sí |
| Revisión humana antes de mergear lo que generó Claude | Sí | Sí |

## Camino recomendado

1. **Interactivo:** hacé la tarea a mano con Claude varias veces. Anotá qué permisos necesitó y qué salió mal.
2. **Empaquetá:** convertí el procedimiento en una [skill](10-skills.md) y las reglas críticas en [hooks](12-hooks.md).
3. **Script:** corré la skill con `claude -p "/mi-skill"` y permisos explícitos. Verificá que el output sea estable.
4. **CI o nube:** recién ahí colgalo de un PR, un cron o una [rutina](16-automatizacion.md#rutinas-cron-en-la-nube).

## Ver también

- [Automatización](16-automatizacion.md) — headless, GitHub Actions, `/loop`, rutinas, Agent SDK.
- [Paralelismo y worktrees](15-paralelismo-y-worktrees.md) — sesiones en paralelo y background.
- [Multi-agente con Gemini](17-multi-agente-gemini.md) — sumar otro modelo para tareas puntuales.
- [Permisos](07-permisos.md) · [Costos](21-costos.md).
