# Flujos de trabajo para el día a día

## Flujos típicos

**Explorar código.** Antes de tocar nada, entender qué existe: dónde está implementado algo, cómo se relacionan las piezas, qué convenciones ya sigue el proyecto. Para exploraciones abiertas o que van a tomar varias búsquedas, conviene delegarlas en un [subagente](09-subagentes.md) de solo lectura en vez de hacerlo inline y ensuciar el contexto principal.

**Planear antes de implementar.** Para tareas no triviales, conviene separar "decidir el enfoque" de "escribirlo": primero acordar la estrategia (qué archivos van a cambiar, qué approach se va a seguir, qué alternativas se descartan y por qué) y recién después ejecutar. Esto evita reescribir trabajo por haber arrancado con el enfoque equivocado.

**Revisar diffs.** Antes de aceptar un cambio generado por el agente, mirar el diff igual que se miraría el de una persona — sobre todo en cambios grandes o en áreas críticas del código. La velocidad de generación no reemplaza la revisión.

**Debugging.** Encarar un bug como una investigación: reproducir el problema, explorar las partes del código involucradas, formular una hipótesis, verificarla, y recién ahí aplicar el fix — en vez de pedir "arreglalo" a ciegas y esperar que adivine bien a la primera.

## Cuándo usar modo plan vs. ejecución directa

- **Modo plan** (diseñar el approach antes de escribir código): conviene en tareas grandes, ambiguas, o donde un error de enfoque sale caro de deshacer — cambios de arquitectura, refactors amplios, features con varias formas válidas de resolverse. Permite alinear el "qué vamos a hacer" antes de gastar tiempo en el "cómo", y da lugar a corregir el rumbo sin haber tocado código todavía.
- **Ejecución directa** (sin planificación explícita previa): tiene sentido en tareas chicas, bien definidas, o mecánicas, donde el enfoque es obvio y plantearlo aparte sería más trabajo que la tarea en sí (un fix puntual, un cambio de una línea, generar un archivo siguiendo un patrón ya establecido).

Regla práctica: si al leer el pedido en voz alta hay más de una forma razonable de resolverlo, conviene planear primero. Si solo hay una forma obvia, ir directo a ejecutar.

## Cómo iterar con el agente de forma eficiente

- **Dar contexto completo desde el pedido inicial**, no de a gotas — ahorra vueltas de ida y vuelta innecesarias.
- **Cortar tareas grandes en pasos verificables**: es más fácil corregir el rumbo después de un paso chico que después de una tarea enorme hecha de punta a punta con el enfoque equivocado.
- **Aprovechar la exploración en paralelo** (varios [subagentes](09-subagentes.md) investigando cosas independientes a la vez) en vez de secuencial, cuando las preguntas no dependen entre sí.
- **Ajustar el nivel de autonomía** (ver [Permisos](07-permisos.md)) según cuánta confianza ya se tiene en el comportamiento del agente en ese repo puntual — no hace falta confirmar todo siempre, ni tampoco delegar todo sin mirar desde el día uno.
- **Cerrar el loop con verificación real**: correr los tests, revisar el diff, probar la funcionalidad — no asumir que "compiló" o "no tiró error" significa que está bien resuelto.
