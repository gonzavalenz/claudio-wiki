# Modelos: cuál usar para qué

Claude Code no está atado a un único modelo — corre sobre distintos modelos de la familia Claude, y la elección de cuál usar es un trade-off entre velocidad, capacidad de razonamiento y costo.

## Familia de modelos y trade-offs

En términos generales, dentro de una misma generación conviven modelos con distinto tamaño/capacidad:

- **Modelos más grandes/capaces** (ej. la línea "Opus"): mejor razonamiento en tareas ambiguas, multi-paso, o que requieren entender un sistema complejo antes de actuar. Más lentos y más caros por token.
- **Modelos intermedios** (ej. la línea "Sonnet"): el balance por defecto para la mayoría del trabajo de desarrollo día a día — buena capacidad de razonamiento sin el costo/latencia del modelo más grande.
- **Modelos más chicos/rápidos** (ej. la línea "Haiku"): mucho más rápidos y baratos, pensados para tareas acotadas y bien definidas donde no hace falta razonamiento profundo.

El trade-off no es solo "mejor vs. peor": un modelo más grande no compensa un prompt mal armado o falta de contexto, y un modelo más chico bien dirigido puede resolver perfectamente una tarea simple más rápido y más barato que uno grande.

## Cuándo conviene un modelo más chico/rápido vs. uno más grande

**Conviene un modelo más chico/rápido cuando:**
- La tarea está bien acotada y es mecánica (renombrar algo en varios archivos, generar un stub siguiendo un patrón ya definido, resumir un resultado).
- Se van a correr muchas iteraciones seguidas (ej. un subagente que se lanza en paralelo varias veces) y el costo/latencia acumulada importa.
- Ya se sabe exactamente qué hay que hacer — el "pensar la estrategia" ya lo hizo una persona o un modelo más grande antes.

**Conviene un modelo más grande cuando:**
- La tarea requiere entender un sistema completo antes de tocar nada (debugging de un bug no evidente, diseño de una arquitectura, revisión de código con juicio).
- Hay ambigüedad real en lo que se pide y hace falta buen criterio para resolverla sin supervisión constante.
- El costo de un error es alto (cambios en producción, decisiones difíciles de revertir) y vale la pena pagar más por mayor probabilidad de acierto a la primera.

Regla práctica: empezar con el modelo intermedio por defecto, subir a uno más grande cuando la tarea lo amerite por complejidad, y bajar a uno más chico para trabajo repetitivo/mecánico o para [subagentes](09-subagentes.md) que corren tareas acotadas en paralelo.

## Cómo se elige/cambia el modelo en Claude Code

El modelo activo se puede fijar o cambiar según el flujo de trabajo (por sesión, por subagente, o como configuración por defecto del proyecto/usuario). Al lanzar un [subagente](09-subagentes.md) especializado, también se puede indicar qué modelo debería usar ese subagente en particular — no todos los pasos de una tarea necesitan el mismo modelo.

Ver `/help` dentro de una sesión para la forma exacta de cambiar de modelo en la versión que estés usando, ya que la interfaz puede variar.
