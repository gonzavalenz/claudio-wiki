# Plan mode, interrupciones y checkpoints

> **En 30 segundos:** separá *pensar* de *hacer*. En **plan mode** (`Shift+Tab` o `/plan`) Claude explora y propone un plan sin tocar tu código; vos lo aprobás o lo corregís. Mientras trabaja, `Esc` lo frena sin perder lo hecho. Y si algo sale mal, `Esc Esc` o `/rewind` vuelven código y/o conversación a un punto anterior. Ojo: los checkpoints solo cubren ediciones de archivos de Claude, **no** comandos de Bash ni efectos remotos.

## Plan mode

En plan mode Claude lee archivos, corre comandos para explorar y escribe un plan, pero **no edita tu código** hasta que lo apruebes.

**Cómo entrar:**

| Forma | Cuándo |
|---|---|
| `Shift+Tab` hasta ver `⏸ plan mode on` | En medio de una sesión |
| `/plan migrá los modelos de ventas a incremental` | Entrar y arrancar con una tarea en un solo paso |
| `claude --permission-mode plan` | Arrancar la sesión ya planificando |
| `"permissions": { "defaultMode": "plan" }` en `.claude/settings.json` | Que el proyecto arranque siempre en plan mode |

**Cuando el plan está listo**, te pregunta cómo seguir:

- **Sí, y usar auto mode** (o *auto-accept edits* si auto no está disponible): aprueba y empieza a editar.
- **Sí, aprobar ediciones a mano**: aprueba y te pide confirmación de cada edición.
- **No, seguir planificando**: te quedás en plan mode y le decís qué cambiar.

Con `Ctrl+G` abrís el plan en tu editor y lo modificás directamente antes de aprobar. Para salir sin aprobar, `Shift+Tab` de nuevo.

### Cuándo vale la pena

| Usá plan mode | Pedilo directo |
|---|---|
| No tenés claro el enfoque | El cambio se describe en una oración |
| El cambio toca varios archivos | Un typo, un log, renombrar una variable |
| No conocés el código | Ya sabés exactamente qué hay que hacer |
| Un error es caro (prod, migraciones de datos) | El error es trivial de revertir |

Regla de la documentación oficial: **si podés describir el diff en una oración, salteá el plan.**

> Con el modelo `opusplan`, el plan lo hace Opus y la ejecución Sonnet (ver [Modelos](04-modelos.md)).

## Flujo recomendado: explorar → planificar → implementar → commitear

**1. Explorar** (en plan mode):

```text
leé models/staging/ventas/ y dags/ingesta_ventas.py. Entendé cómo llegan los datos de ventas a BigQuery y qué modelos los consumen.
```

**2. Planificar** (en plan mode):

```text
quiero pasar fct_ventas a incremental con merge por venta_id, particionado por fecha_venta. ¿Qué archivos cambian? ¿Cómo hago el backfill? Armá un plan.
```

Revisá el plan, corregilo con `Ctrl+G` o pidiendo cambios.

**3. Implementar** (aprobás el plan):

```text
implementá el plan. Corré dbt build --select fct_ventas+ y arreglá lo que falle.
```

**4. Commitear**:

```text
commiteá con un mensaje descriptivo y abrí un PR
```

## Pedirle que te pregunte antes

Para tareas grandes o ambiguas, que te entreviste antes de planificar:

```text
quiero armar un pipeline de data quality para las tablas raw de ventas. Entrevistame en detalle usando la tool AskUserQuestion: implementación, casos borde, alertas, tradeoffs. No hagas preguntas obvias. Cuando terminemos, escribí la spec completa en SPEC.md.
```

Después arrancá una **sesión nueva** para implementar la spec: contexto limpio, enfocado solo en ejecutar.

## Interrumpir y redirigir

| Acción | Qué pasa |
|---|---|
| `Esc` | Frena en el acto (cancela la tool que estaba corriendo). Lo hecho hasta ahí queda. Esperá tu siguiente instrucción |
| Escribir y `Enter` mientras trabaja | El mensaje queda en cola y Claude lo lee apenas terminan las tool calls en curso, sin frenar |
| "Deshacé eso" | Claude revierte sus cambios |
| `Esc` `Esc` / `/rewind` | Menú para volver a un checkpoint |

Corregí temprano: cuanto antes lo frenás cuando se va por las ramas, menos contexto se ensucia.

## Checkpoints y `/rewind`

Cada prompt que mandás crea un **checkpoint** con el estado de los archivos antes de que Claude los toque. Se guardan con la sesión (siguen disponibles si la retomás con `--resume`) y se conservan los últimos 100 por sesión.

Abrí el menú con `/rewind` o `Esc` `Esc` (con el input vacío), elegí el mensaje y la acción:

| Opción | Código | Conversación |
|---|---|---|
| Restore code and conversation | Vuelve atrás | Vuelve atrás |
| Restore conversation | Queda como está | Vuelve atrás |
| Restore code | Vuelve atrás | Queda como está |
| Summarize from here | — | Resume desde ese punto hacia adelante |
| Summarize up to here | — | Resume lo anterior a ese punto |

Al restaurar la conversación, el prompt original vuelve al input para que lo reenvíes o lo edites. Si hiciste `/clear` en este mismo proceso, el menú también ofrece volver a la sesión anterior.

### Qué NO restaura

| No se deshace | Por qué / qué hacer |
|---|---|
| Archivos cambiados por **comandos Bash** (`rm`, `mv`, `cp`, scripts, `dbt` escribiendo en `target/`) | Solo se rastrean las ediciones de las tools de archivos de Claude |
| **Efectos remotos**: tablas creadas o borradas en BigQuery, un `dbt run` contra prod, un deploy, un push | No hay snapshot posible. Se controla con [permisos](07-permisos.md) |
| Ediciones de **subagents** (salvo skills forkeadas en foreground) | Revertilas con git |
| Cambios que hiciste vos a mano o desde otra sesión | No los ve |
| Archivos con symlinks o hard links | Se saltean con un aviso |

**Los checkpoints no reemplazan a git.** Son un "deshacer" local de la sesión; el historial permanente va en commits.

## Ejemplo: probar algo arriesgado sin miedo

```text
probá reescribir int_clientes_deduplicados usando QUALIFY ROW_NUMBER() en vez del self-join y compará los resultados con la versión actual
```

Si el resultado no te convence: `Esc Esc` → elegís ese prompt → **Restore code and conversation**. Volvés al punto anterior con el código y el contexto limpios. Si querés conservar las dos líneas de trabajo, usá `/branch` antes de probar.

## Trucos y errores comunes

- **Commiteá antes de lo arriesgado.** Los checkpoints no cubren lo que se haga por Bash; un commit sí.
- **Plan aprobado = sesión con nombre**: aceptar un plan le pone a la sesión un título basado en el plan (si no la nombraste antes).
- **El plan sobrevive a `/compact`**: se relee del disco después de compactar.
- **Plan mode también agrega overhead.** Para cambios chicos y claros, pedilo directo.
- **Después de dos correcciones fallidas**, no sigas parchando: `/rewind` al punto previo o `/clear` y un prompt mejor.
- **Los mensajes que mandaste mientras trabajaba no crean checkpoint propio**: para deshacerlos, rebobiná al prompt que inició ese turno.
- **En plan mode Claude puede correr comandos para explorar**: los de solo lectura no preguntan; el resto depende de tu configuración (con auto mode disponible, los revisa el clasificador).

## Ver también

- [Permisos](07-permisos.md) — modos y reglas
- [Contexto](05-contexto.md) — resumir y bifurcar sesiones
- [Modelos](04-modelos.md) — `opusplan` y esfuerzo
- [Flujos de trabajo](20-flujos-de-trabajo.md)
- [Git básico](git-basico.md)
