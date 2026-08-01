# MCP: conectar herramientas y datos externos

## Qué es el Model Context Protocol y qué problema resuelve

**MCP (Model Context Protocol)** es un protocolo abierto que define una forma estándar para que un agente como Claude Code se conecte a herramientas y fuentes de datos externas — bases de datos, APIs internas, sistemas de tickets, servicios de la nube, etc. — sin que cada integración tenga que reinventarse desde cero.

El problema que resuelve: sin un estándar, cada vez que se quiere que el agente hable con un sistema externo (una base de datos, un servicio interno de la empresa) hay que escribir una integración ad hoc. Con MCP, cualquier sistema que exponga un **servidor MCP** queda automáticamente disponible como un conjunto de tools más para el agente, con el mismo mecanismo de conexión sin importar qué sistema sea.

Un **servidor MCP** expone un conjunto de capacidades (tools, recursos, prompts) que Claude Code puede usar como si fueran herramientas nativas, una vez conectado.

## Cómo se configura un servidor MCP en Claude Code

En términos generales, conectar un servidor MCP implica:

1. Tener (o levantar) el servidor MCP correspondiente al sistema que se quiere conectar (puede ser un servidor ya publicado por un tercero, o uno propio).
2. Declarar esa conexión en la configuración de Claude Code (a nivel de proyecto o de usuario, según si la integración es específica de un repo o de uso general) — típicamente indicando cómo arrancar/ubicar el servidor y qué credenciales usar.
3. Una vez conectado, las tools que expone ese servidor quedan disponibles en la sesión igual que cualquier otra tool — sujetas al mismo [sistema de permisos](07-permisos.md) para confirmar acciones antes de ejecutarlas.

Las credenciales de acceso a sistemas externos (tokens, API keys) deben tratarse con el mismo cuidado que cualquier secreto — no deberían terminar commiteadas en el repo (ver convenciones de `.gitignore`).

## Ejemplos de MCP servers útiles para equipos de datos

- **Bases de datos** (Postgres, BigQuery, Snowflake, etc.): permitir que el agente consulte schemas o corra queries de solo lectura para entender datos reales al resolver una tarea, sin tener que copiar y pegar resultados a mano.
- **Sistemas de tickets/proyecto** (Jira, Linear, GitHub Issues): que el agente pueda leer o actualizar el estado de una tarea directamente relacionada con el trabajo que está haciendo.
- **Almacenamiento de objetos / data lakes**: consultar o explorar estructura de datos sin salir de la sesión.
- **Observabilidad** (dashboards, logs): que el agente pueda mirar métricas o logs relevantes al diagnosticar un problema, en vez de depender de que se los pegue una persona.

Como con cualquier integración que da acceso a sistemas reales, conviene empezar con el servidor MCP en modo de solo lectura o alcance acotado, y ampliar permisos a medida que se confía en el patrón de uso — misma lógica que en [Permisos](07-permisos.md).
