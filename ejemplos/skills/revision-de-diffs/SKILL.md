---
name: revision-de-diffs
description: Revisar un diff antes de commitear o aceptar cambios (propios o generados por el agente) siguiendo un checklist consistente. Usar cuando el usuario pide "revisá esto", "hacé code review", "fijate si está bien antes de commitear", o como paso final de cualquier tarea que haya modificado código.
---

# Revisión de diffs antes de commitear

## Cuándo se dispara

- El usuario pide explícitamente revisar, auditar o hacer code review de un cambio.
- Como último paso de una tarea que modificó código, antes de dar la tarea por terminada o de commitear.
- Antes de aceptar un cambio grande o en un área crítica del proyecto (ver [buenas-practicas](../../../buenas-practicas/README.md)).

## Cómo hacer la revisión

1. **Mirar el diff completo**, no solo los archivos que parecen más relevantes a simple vista. Usar `git diff` (o el equivalente en curso, ej. cambios staged con `git diff --staged`).
2. Revisar cada archivo modificado contra este checklist:

   - **Correctness**: ¿el cambio hace lo que dice que hace? ¿Hay algún caso borde obvio que no está contemplado (input vacío, lista con un solo elemento, valores `null`)?
   - **Alcance**: ¿el diff toca solo lo necesario para la tarea pedida, o se coló una refactorización, un cambio de estilo, o un archivo no relacionado? Si hay algo fuera de alcance, señalarlo en vez de commitearlo junto.
   - **Seguridad**: ¿el cambio introduce algo como una query armada por concatenación de strings, un secreto hardcodeado, o una dependencia nueva sin justificación clara?
   - **Tests**: si el proyecto tiene tests, ¿el cambio los rompe? ¿Necesita un test nuevo que no se agregó?
   - **Consistencia de estilo**: ¿el código nuevo sigue las convenciones ya existentes en el archivo/proyecto (nombres, estructura, manejo de errores), o introduce un patrón distinto sin razón?
   - **Reversibilidad**: si algo de esto sale mal en producción, ¿es fácil de revertir? Si no lo es, marcarlo explícitamente como algo que amerita más cuidado antes de aceptar.

3. Si el diff es grande, dividir la revisión por archivo o por unidad lógica en vez de intentar juzgarlo todo de una sola pasada.

## Cómo reportar el resultado

- Si no hay problemas: decirlo explícitamente ("revisé el diff, no encontré problemas") — no dar el visto bueno por omisión.
- Si hay problemas: listarlos ordenados de más a menos importante, cada uno con el archivo/línea concreto y qué pasaría si no se corrige (no solo "esto está mal", sino el escenario de falla).
- No mezclar la revisión con cambios nuevos no pedidos: si se detecta algo fuera del alcance original, mencionarlo aparte en vez de arreglarlo directamente sin avisar.

## Qué hacer si se encuentra un problema

- Problemas menores de estilo: señalarlos, pero no bloquear el commit por eso solo.
- Problemas de correctness o seguridad: señalarlos como bloqueantes y proponer el fix antes de continuar.
- Si no se está seguro de si algo es un problema real o una decisión de diseño intencional: preguntar en vez de asumir y corregir sin contexto.
