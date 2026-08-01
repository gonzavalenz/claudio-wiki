# Hooks: reglas que no dependen de que el modelo se acuerde

## Qué es un hook y en qué eventos se puede enganchar

Un **hook** es un comando (script, binario, lo que sea ejecutable) que Claude Code corre automáticamente cuando ocurre un evento determinado durante la sesión — sin que el modelo tenga que "decidir" hacerlo ni acordarse de hacerlo.

Eventos típicos en los que se puede enganchar un hook:

- Antes o después de que se use una tool determinada (ej. antes de correr un comando de `Bash`, después de editar un archivo).
- Al terminar una tarea o una sesión.
- Cuando se dispara una confirmación de permisos (ver [Permisos](07-permisos.md)).

El hook recibe información sobre lo que está por pasar (o lo que acaba de pasar) y puede, según el tipo de evento, permitir la acción, bloquearla, o simplemente registrar/notificar algo.

## Diferencia entre pedirle algo al modelo en `CLAUDE.md` y forzarlo con un hook

Esta es la distinción más importante del capítulo:

- **`CLAUDE.md`** (ver [Memoria](05-memoria.md)) es una instrucción que el modelo *lee y trata de seguir*. Es una fuerte sugerencia de comportamiento, pero sigue dependiendo de que el modelo la recuerde y la aplique correctamente en cada situación — no hay garantía dura.
- **Un hook** es código que se ejecuta *siempre*, en el evento que corresponda, sin pasar por el criterio del modelo. Si el hook bloquea una acción, esa acción no se ejecuta, sin importar qué haya "decidido" el modelo.

En otras palabras: `CLAUDE.md` es una convención; un hook es una regla forzada a nivel de sistema. Si algo es realmente crítico ("nunca se puede pushear directo a `main`", "todo commit tiene que pasar el linter antes"), un hook lo garantiza de una forma que una instrucción en texto no puede.

## Casos de uso típicos

- **Validaciones**: correr un linter o un check de formato automáticamente antes de aceptar una edición, y rechazarla si no pasa.
- **Bloqueos duros**: impedir que se ejecute un comando específico (ej. `git push --force` a una rama protegida) sin importar el contexto de la conversación.
- **Notificaciones**: avisar por otro canal (ej. un mensaje) cuando termina una tarea larga o una sesión en background.
- **Registro/auditoría**: dejar un log de qué comandos se ejecutaron durante una sesión, útil en equipos que necesitan trazabilidad de lo que un agente hizo.

Regla práctica: si la respuesta a "¿qué pasa si el modelo se olvida de esto una vez?" es "sería un problema serio", esa regla probablemente merece un hook y no solo una línea en `CLAUDE.md`.
