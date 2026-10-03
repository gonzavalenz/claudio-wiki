# Fundamentos: LLM, agente y agentic loop

> **En 30 segundos:** un LLM solo predice texto. Claude Code es un *agente*: el mismo modelo, envuelto en un programa (el *harness*) que le da `tools` para leer, editar y ejecutar cosas en tu máquina, y que le devuelve el resultado de cada acción para que decida el paso siguiente. Ese ciclo es el `agentic loop`. Lo que más limita a un agente no es la inteligencia del modelo, sino el `context window`.

## LLM vs. agente

| | LLM "a secas" (chat) | Agente (Claude Code) |
|---|---|---|
| Qué hace | Recibe texto, devuelve texto | Recibe una tarea y actúa hasta resolverla |
| Ve tu código | Solo lo que le pegues | Lo busca y lo lee solo |
| Ejecuta cosas | No | Sí: comandos, tests, `git`, `dbt`, `bq`... |
| Verifica | No sabe si lo que dijo funciona | Corre el test, lee el error, corrige |
| Tu rol | Copiar y pegar entre pasos | Dar contexto, dirigir y revisar |

El modelo detrás es el mismo. La diferencia la pone el **harness**: la capa que le da herramientas al modelo y administra qué contexto ve.

## El agentic loop

Según la documentación oficial, el loop tiene tres fases que se mezclan entre sí:

1. **Juntar contexto**: buscar archivos, leer código, mirar `git status`, leer errores.
2. **Actuar**: editar archivos, correr comandos.
3. **Verificar**: correr tests o el comando que corresponda y ver si funcionó.

Se repite hasta que la tarea está resuelta. Cada uso de una tool devuelve información nueva que alimenta la siguiente decisión. Vos también sos parte del loop: podés interrumpir en cualquier momento (`Esc`) o mandar una corrección mientras trabaja (ver [Plan mode y checkpoints](09-plan-mode-y-checkpoints.md)).

## Las tools: lo que lo hace agente

| Categoría | Qué puede hacer |
|---|---|
| Archivos | Leer, editar, crear, renombrar |
| Búsqueda | Encontrar archivos por patrón, buscar contenido con regex |
| Ejecución | Correr comandos de shell, tests, `git`, servidores |
| Web | Buscar en la web, leer documentación, buscar mensajes de error |
| Code intelligence | Ver errores de tipos, ir a definiciones (requiere plugins de code intelligence) |

Además tiene tools para lanzar [subagents](11-subagents.md), hacerte preguntas y orquestar trabajo. Todo lo demás ([skills](10-skills.md), [MCP](13-mcp.md), [hooks](12-hooks.md), [plugins](14-plugins.md)) son capas que se suman encima de este loop.

## Qué ve Claude cuando arranca

Cuando corrés `claude` en una carpeta, tiene acceso a:

- **Tu proyecto**: la carpeta y subcarpetas (y otras rutas si lo autorizás).
- **Tu terminal**: cualquier comando que vos podrías correr.
- **Tu estado de git**: rama actual, cambios sin commitear, commits recientes.
- **Tu `CLAUDE.md`** y la **auto memory** (ver [Memoria](06-memoria.md)).
- **Las extensiones que configures**: MCP, skills, subagents.

Lo que **no** ve: la conversación de sesiones anteriores. Cada sesión arranca con un `context window` nuevo. Lo que tiene que sobrevivir entre sesiones va en `CLAUDE.md`.

## Ejemplo: un test de dbt que falla

Le pedís:

```text
el test not_null de fct_pedidos.cliente_id está fallando en dev. Encontrá por qué y arreglalo.
```

Lo que hace el loop, vuelta por vuelta:

1. Corre `dbt test --select fct_pedidos` para ver el error real.
2. Lee `models/marts/fct_pedidos.sql` y el `schema.yml`.
3. Sigue el `ref()` hasta `stg_pedidos.sql` y ve que hay un `LEFT JOIN` a clientes.
4. Corre una query con `bq query` para contar cuántas filas quedan con `cliente_id` nulo.
5. Propone el cambio (filtrar, o cambiar el join), lo edita.
6. Vuelve a correr `dbt test --select fct_pedidos` para confirmar.

No le dijiste qué archivos abrir ni qué comandos correr: eso lo resuelve el loop. Vos aportás lo que no está en el código (por ejemplo, "los pedidos sin cliente son pedidos de prueba, se pueden filtrar").

## Trucos y errores comunes

- **Delegá, no dictes.** Dale el objetivo y el contexto que solo vos sabés; dejá que él elija los pasos. "El checkout falla con tarjetas vencidas, el código está en `src/payments/`" rinde más que una lista de 10 pasos.
- **Dale una forma de verificar.** Es lo que más mejora el resultado: un test, un `dbt build --select`, una query de control, un output esperado. Sin verificación, el agente entrega algo *plausible*, no algo *correcto*.
- **Es una conversación.** Si el primer intento no es lo que querías, no arranques de cero: corregí ("no, el problema está en el manejo de la sesión").
- **El context window es el recurso escaso.** Cada archivo leído y cada output de comando lo ocupa. Sesiones largas y mezcladas rinden peor. Ver [Contexto](05-contexto.md).
- **Claude Code te puede enseñar a usarlo.** Preguntale "¿cómo configuro un hook?" o "¿cómo debería armar mi CLAUDE.md?".

## Ver también

- [Qué es Claude Code y dónde vive](02-que-es-claude-code.md)
- [Contexto: el recurso que más hay que cuidar](05-contexto.md)
- [Permisos](07-permisos.md) — cuánto puede hacer solo
- [Plan mode y checkpoints](09-plan-mode-y-checkpoints.md)
