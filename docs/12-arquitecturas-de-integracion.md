# Arquitecturas de integración

## Formas de integrar Claude Code en un flujo de trabajo de equipo

Más allá del uso interactivo en la terminal, Claude Code se puede integrar de varias formas en el flujo de trabajo de un equipo:

- **Uso interactivo local**: una persona corre `claude` en su máquina, dentro de un repo, y trabaja de ida y vuelta con el agente. Es el modo por defecto y el más flexible.
- **Scripts/automatizaciones puntuales**: invocar Claude Code desde un script para una tarea específica y bien definida (ej. generar un resumen, correr una migración de código repetitiva sobre varios archivos), sin sesión interactiva.
- **CI/CD**: correr Claude Code como parte de un pipeline (ej. revisar un PR automáticamente, generar sugerencias sobre un diff) — acá el agente corre sin nadie mirando en tiempo real, por lo que la configuración de [permisos](07-permisos.md) tiene que ser explícita de antemano (no hay quién confirme acciones sobre la marcha).
- **Agentes de fondo / background**: tareas largas que corren en paralelo a otro trabajo y notifican cuando terminan, en vez de bloquear a la persona que las lanzó (ver [Subagents](09-subagents.md)).

## Claude Code como parte de un pipeline vs. uso interactivo

La diferencia clave entre ambos modos es **quién y cuándo confirma las acciones riesgosas**:

- **Uso interactivo**: hay una persona presente que puede aprobar o rechazar acciones sobre la marcha. El sistema de permisos puede apoyarse en esa presencia (preguntar cuando haga falta).
- **Uso en pipeline**: no hay nadie mirando en el momento. Todo lo que el agente pueda necesitar hacer tiene que estar pre-autorizado explícitamente (allowlist) o el pipeline tiene que fallar de forma segura ante cualquier acción no contemplada, en vez de quedar esperando una confirmación que nunca va a llegar.

Por eso, correr Claude Code en CI exige ser mucho más conservador con el alcance de lo que se le permite hacer, comparado con una sesión interactiva donde el costo de "preguntar" es bajo.

## Trade-offs de cada arquitectura

| Arquitectura | Ventaja | Costo/riesgo |
|---|---|---|
| Interactivo local | Máxima flexibilidad, feedback inmediato, permisos ajustables sobre la marcha | No escala a tareas masivas/repetitivas, depende de que haya una persona presente |
| Script puntual | Reproducible, se puede versionar y reusar | Requiere definir bien el alcance de antemano, sin margen de ida y vuelta |
| CI/CD | Corre automáticamente en cada cambio, sin intervención manual | Requiere permisos pre-configurados con cuidado; un error de alcance puede afectar a todo el equipo |
| Background/paralelo | No bloquea el trabajo principal mientras se resuelve algo largo | Hay que diseñar bien cómo y cuándo se reporta el resultado, para no perderlo ni fabricarlo antes de tiempo |

Regla práctica: empezar siempre en modo interactivo para entender cómo se comporta el agente en una tarea nueva, y recién automatizar (script o CI) una vez que ese comportamiento es predecible y confiable.
