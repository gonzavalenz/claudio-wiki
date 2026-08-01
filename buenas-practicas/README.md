# Buenas prácticas

Reglas concretas de uso de Claude Code: qué hacer y qué evitar, con el motivo detrás de cada una. No es teoría (eso va en [`docs/`](../docs)) — son recomendaciones accionables que salen de la experiencia real usándolo.

Cada entrada se resume como: **regla → por qué → cuándo aplica**.

## Gestión de `CLAUDE.md`

**Regla:** mantenerlo corto, y sacar de ahí cualquier cosa que se pueda derivar leyendo el código.
**Por qué:** un `CLAUDE.md` largo y desactualizado es peor que no tenerlo — el agente puede seguir instrucciones que ya no son ciertas, y nadie lo termina leyendo ni manteniendo entero.
**Cuándo aplica:** siempre que se esté por agregar algo nuevo, preguntarse primero "¿esto ya se puede inferir del repo?" antes de escribirlo. Ver [05 — Memoria](../docs/05-memoria.md).

**Regla:** si lo que se quiere agregar es un procedimiento de varios pasos para una tarea puntual (no contexto general), convertirlo en una [skill](../docs/08-skills.md) en vez de sumarlo a `CLAUDE.md`.
**Por qué:** una skill se carga solo cuando aplica; un `CLAUDE.md` inflado con procedimientos ocupa contexto en *todas* las sesiones, aplique o no la tarea.
**Cuándo aplica:** cuando la sección que se está por escribir empieza con "para hacer X, seguir estos pasos...".

## Subagentes vs. resolver inline

**Regla:** delegar en un [subagente](../docs/09-subagentes.md) cuando la tarea es exploración abierta (no se sabe de antemano dónde está la respuesta) y resolver inline cuando el destino ya se conoce.
**Por qué:** delegar una búsqueda directa a un subagente agrega overhead de coordinación sin necesidad; no delegar una exploración larga ensucia el contexto principal con resultados intermedios que no aportan una vez resuelta la tarea.
**Cuándo aplica:** antes de lanzar un subagente, preguntarse "¿ya sé dónde/cómo resolver esto?" — si la respuesta es sí, resolver directo.

**Regla:** nunca delegar entendimiento — un subagente necesita todo el contexto relevante en el prompt inicial, no solo la instrucción final.
**Por qué:** un subagente no tiene el historial de la conversación principal; un prompt tipo "arreglá el bug" sin contexto de qué se probó, qué se descartó y qué formato de respuesta se espera produce resultados genéricos o incorrectos.
**Cuándo aplica:** siempre, al armar el prompt para cualquier subagente.

## Permisos y autonomía

**Regla:** empezar con un modo de permisos más restrictivo en un repo nuevo, y ampliar la autonomía a medida que se genera confianza — no partir de máxima autonomía por defecto.
**Por qué:** el costo de confirmar una acción de más es bajo; el costo de una acción no deseada en un contexto todavía desconocido (un `push` mal dirigido, un archivo borrado) puede ser alto y difícil de revertir.
**Cuándo aplica:** al arrancar en un repo o proyecto donde todavía no se conoce el patrón de comportamiento del agente. Ver [07 — Permisos](../docs/07-permisos.md).

**Regla:** ciertas acciones (destructivas, difíciles de revertir, visibles para otros, o que saltean controles de seguridad) siempre se confirman, sin importar cuán autónomo esté configurado el resto de la sesión.
**Por qué:** que se haya aprobado una acción de este tipo una vez no significa que quede aprobada para siempre — la autorización es por alcance, no un cheque en blanco.
**Cuándo aplica:** `push --force`, `reset --hard`, borrar branches/archivos, mandar mensajes o abrir/cerrar PRs, deshabilitar hooks de seguridad.

## Manejo de contexto largo

**Regla:** cortar sesiones que ya cumplieron su propósito en vez de extenderlas indefinidamente hacia un tema nuevo.
**Por qué:** un contexto que crece sin límite encarece cada turno siguiente y diluye la relevancia de lo que ya se acumuló — ver [15 — Costos](../docs/15-costos.md).
**Cuándo aplica:** cuando el tema de la conversación cambió por completo respecto al motivo original de la sesión.

**Regla:** delegar exploraciones largas (leer muchos archivos, probar varias búsquedas) a un subagente en vez de acumularlas en la conversación principal.
**Por qué:** protege el espacio de contexto disponible para razonar sobre el resto de la tarea más adelante en la sesión.
**Cuándo aplica:** cuando se anticipa que investigar algo va a tomar varios pasos intermedios cuyo detalle no hace falta conservar, solo la conclusión.

## Revisión de código generado antes de aceptar cambios

**Regla:** revisar el diff generado por el agente con el mismo criterio que se revisaría el de una persona, especialmente en cambios grandes o en áreas críticas.
**Por qué:** la velocidad de generación no es garantía de corrección; un cambio que "compila" o "no tira error" no necesariamente resuelve bien la tarea o no introduce efectos secundarios no buscados.
**Cuándo aplica:** siempre antes de commitear, y con más rigor cuanto mayor sea el impacto potencial del cambio (producción, datos, seguridad).

---

*Estas reglas se van a seguir sumando y ajustando a medida que aparezcan [casos de uso](../casos-de-uso/) reales que las confirmen, maticen o contradigan.*
