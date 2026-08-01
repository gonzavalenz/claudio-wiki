# Costos y buenas prácticas de uso

## Qué determina el costo de una sesión

El costo de usar Claude Code está determinado principalmente por:

- **Modelo elegido**: los modelos más grandes/capaces cuestan más por token que los más chicos/rápidos (ver [Modelos](03-modelos.md)).
- **Tamaño del contexto**: cuanto más contenido acumula una conversación (archivos leídos, resultados de comandos, historial de idas y vueltas), más caro es cada turno siguiente — porque ese contexto se reprocesa.
- **Cantidad de tools usadas**: cada búsqueda, lectura o comando ejecutado agrega resultado al contexto; tareas que requieren explorar mucho antes de actuar consumen más que tareas donde el destino ya se conoce.
- **Subagentes lanzados**: cada [subagente](09-subagentes.md) corre su propia sesión con su propio consumo — lanzar varios en paralelo multiplica el costo total, aunque protege el contexto de la conversación principal.

## Prácticas para no gastar de más

- **Elegir el modelo según la tarea**, no usar siempre el más grande por defecto — ver [Modelos](03-modelos.md) para el criterio.
- **Delegar exploración pesada a subagentes** en vez de acumularla en el contexto principal: no solo mantiene la conversación más legible, también evita que cada turno siguiente de la conversación principal cargue con resultados de búsquedas que ya cumplieron su función.
- **Dar contexto completo y específico desde el pedido inicial**, para evitar rondas de ida y vuelta que solo sirven para completar información que se podría haber dado de entrada.
- **Cerrar sesiones/tareas que ya cumplieron su propósito** en vez de mantener conversaciones larguísimas abiertas indefinidamente — un contexto que crece sin límite encarece cada turno nuevo, incluso si el tema ya cambió.
- **Usar comandos y skills reutilizables** (ver [Comandos](06-comandos-slash.md) y [Skills](08-skills.md)) para tareas repetitivas, en vez de reexplicar el mismo procedimiento largo cada vez.
- **Acotar el alcance de lo que se le pide explorar**: pedir "buscá en la carpeta X" en vez de "buscá en todo el repo" cuando ya se sabe más o menos dónde está algo.

## Cómo monitorear el uso

- Revisar el consumo asociado a la cuenta/organización con la frecuencia que corresponda al volumen de uso del equipo (diario, semanal), según los mecanismos de reporte que exponga la plataforma de facturación en cada caso.
- Prestar atención a sesiones puntuales inusualmente largas o costosas — suelen ser señal de que convenía cortar el contexto antes, delegar en un subagente, o que la tarea estaba mal acotada desde el pedido inicial.
- Si el equipo automatiza el uso de Claude Code (ver [Arquitecturas de integración](12-arquitecturas-de-integracion.md)), monitorear el costo agregado del pipeline por separado del uso interactivo, ya que suelen tener patrones de consumo muy distintos.
