# Subagentes: delegar sin ensuciar la conversación principal

## Qué es un subagente

Un **subagente** es una instancia separada del agente, con su propio historial y su propia ventana de contexto, que se lanza para resolver una tarea puntual y devuelve un resultado final a la conversación principal — sin que todos los pasos intermedios que dio (búsquedas, lecturas, intentos fallidos) queden ocupando espacio en el contexto principal.

La conversación principal solo ve el **resumen/resultado final** que devuelve el subagente, no todo el proceso que usó para llegar ahí.

## Por qué protege el contexto principal

El contexto de una conversación es limitado, y todo lo que ocupa espacio ahí (resultados de búsquedas largas, contenido de archivos leídos, intentos que no funcionaron) reduce la capacidad de razonar sobre el resto de la tarea más adelante en la sesión.

Si una tarea requiere explorar mucho (leer 20 archivos para entender cómo funciona algo, probar varias búsquedas hasta encontrar lo que se busca), delegarla a un subagente evita que esa exploración "ensucie" el contexto principal: el subagente hace el trabajo pesado en su propio espacio, y la conversación principal solo recibe la conclusión.

## Cuándo conviene delegar vs. resolver inline

**Conviene un subagente cuando:**
- La tarea es una pregunta de investigación/exploración abierta que va a tomar varias búsquedas o lecturas ("¿dónde está implementado X?", "¿qué opciones tenemos para Y?").
- El resultado que importa es la conclusión, no el camino recorrido para llegar a ella.
- Se pueden lanzar varias exploraciones independientes en paralelo (varios subagentes a la vez, cada uno con una pregunta distinta).
- Se quiere una "segunda opinión" independiente, que no esté sesgada por el razonamiento ya hecho en la conversación principal (ej: una revisión de código a ciegas).

**Conviene resolver inline (sin subagente) cuando:**
- El destino ya se conoce (un archivo o símbolo puntual) — ahí alcanza con una búsqueda directa, no hace falta delegar.
- La tarea depende paso a paso de decisiones que se van tomando en la conversación principal (no es independiente).
- Es una tarea corta: el costo de armar el contexto para un subagente (explicarle qué tiene que hacer, por qué, qué se probó ya) puede ser mayor que resolverlo directo.

Regla práctica: **no delegar entendimiento**. Un subagente no tiene el contexto de toda la conversación previa — hay que darle todo lo que necesita para trabajar de forma autónoma (qué se busca, qué se descartó ya, qué formato de respuesta se espera). Un prompt tipo "arreglá el bug" sin contexto produce resultados genéricos o directamente incorrectos.

## Agentes especializados vs. general-purpose

Los subagentes pueden ser:

- **General-purpose**: sin un rol predefinido, para tareas de investigación o ejecución multi-paso que no encajan en una categoría específica.
- **Especializados**: con un rol, herramientas y comportamiento predefinidos para un tipo de tarea recurrente (ej: un agente de exploración de código de solo lectura, un agente de revisión de código, un agente de documentación). Suelen ser más rápidos y consistentes que un general-purpose para su tarea específica, porque no tienen que "adivinar" el enfoque correcto.

Como referencia, en Claude Code existen (entre otros) agentes como **Explore** (búsqueda de código rápida, de solo lectura, para localizar dónde está algo) y **Plan** (diseño de estrategias de implementación sin escribir código todavía) — cada uno pensado para un tipo de tarea puntual, en vez de usar siempre un agente genérico.

## Ejecución en paralelo vs. en segundo plano

Los subagentes se pueden lanzar:

- **En paralelo**: varias tareas independientes a la vez, cuando ninguna depende del resultado de la otra.
- **En segundo plano (background)**: la conversación principal sigue mientras el subagente trabaja, y se recibe una notificación cuando termina — sin quedarse esperando ni "adivinar" el resultado antes de que llegue.

La clave es no simular ni anticipar el resultado de un subagente que todavía no terminó: si se lanzó en background, su resultado llega como una notificación aparte, nunca como algo que se escribe de antemano.
