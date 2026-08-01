# Skills: empaquetar conocimiento y procedimientos

## Qué es una skill

Una **skill** es un procedimiento empaquetado y reutilizable: un conjunto de instrucciones (y opcionalmente scripts o recursos) que le enseña a Claude Code cómo encarar un tipo de tarea específico, para no tener que reexplicarlo cada vez.

Se invocan con `/nombre-de-la-skill` (igual que un [slash command](06-comandos-slash.md)) o automáticamente, cuando la descripción de la skill matchea con lo que el usuario está pidiendo.

## Skill vs. `CLAUDE.md`

Son complementarios, no lo mismo:

| | `CLAUDE.md` | Skill |
|---|---|---|
| Alcance | Contexto permanente del proyecto (se carga siempre) | Procedimiento puntual (se carga solo cuando aplica) |
| Contenido típico | Arquitectura, comandos de build/test, convenciones del repo | Una tarea concreta con pasos definidos ("cómo hacer X") |
| Cuándo conviene | Info que el agente necesita saber *siempre* que trabaja en el repo | Info que solo hace falta *a veces*, y sería ruido tenerla cargada todo el tiempo |

Regla práctica: si estás por agregar a `CLAUDE.md` una sección larga que describe un procedimiento paso a paso para una tarea específica (no información general del proyecto), probablemente eso debería ser una skill en vez de vivir en `CLAUDE.md`. Mantiene `CLAUDE.md` corto y la skill se carga solo cuando hace falta.

## Cuándo conviene crear una skill propia

- Hay una tarea que se repite (deploy, revisar cierto tipo de PR, generar cierto tipo de reporte) y cada vez hay que reexplicar los mismos pasos.
- El procedimiento tiene pasos específicos del equipo/proyecto que no son obvios por el código (ej: "antes de mergear a `main`, correr este script de validación que no está en el pipeline de CI").
- Se quiere que el comportamiento sea consistente entre distintas personas del equipo que usan Claude Code sobre el mismo repo.

No conviene crear una skill para algo que se resuelve mejor con una instrucción de una sola vez, o que ya se puede derivar leyendo el código del proyecto.

## Ejemplos de buenos casos de uso

- Un checklist de revisión de código específico del equipo (más allá de lo que hace un linter).
- Un procedimiento de release/deploy con pasos que no están automatizados en CI.
- Una guía de cómo generar cierto tipo de reporte o migración que sigue siempre la misma estructura.
- Convenciones de un dominio específico (ej: cómo escribir queries SQL siguiendo el estilo del equipo de datos) que aplican en varios repos, no solo en uno.

Ver [`ejemplos/skills/`](../ejemplos/skills/) para skills concretas de referencia (se van a ir sumando).
