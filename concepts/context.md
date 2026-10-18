# Context

> verificado: 2026-10-18 · fuentes: [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Context window (Claude Code)](https://code.claude.com/docs/en/context-window), [Prompt caching (Claude Code)](https://code.claude.com/docs/en/prompt-caching), [Best practices](https://code.claude.com/docs/en/best-practices), [model-config](https://code.claude.com/docs/en/model-config), [Copilot CLI context](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management), [Gemini CLI commands](https://geminicli.com/docs/reference/commands)

La context window es todo lo que el modelo ve al generar una respuesta: es su *working memory*. Es finita, y a medida que se llena el modelo pierde precisión (*context rot*). Es el recurso más importante que hay que administrar.

## Cómo funciona

- **Sin memoria entre requests**: en cada turno el harness reenvía todo. Eso incluye el system prompt, las tool definitions, la memoria (`CLAUDE.md`), el historial, los tool results y el mensaje nuevo.
- **Attention budget**: cada token compite por atención. Por eso más contexto no es automáticamente mejor.
- **Estrategias** (*context engineering*):

| Estrategia | Qué hace |
|---|---|
| Compaction | Resume la conversación y sigue a partir del resumen. |
| Tool result clearing | Descarta outputs viejos de tools. Es la forma más liviana. |
| Notas externas | El estado vive en archivos, no en el chat. |
| Subagents | Trabajan con contexto limpio y devuelven solo un resumen. |
| Just-in-time | Guarda referencias (paths, URLs) y carga el contenido recién cuando lo necesita. |

- **Prompt caching**: el prefijo repetido del prompt (tools → system → mensajes) se cobra mucho más barato. Cambia lo que **pagás** por esos tokens, no si **ocupan** la ventana. Cualquier cambio en el prefijo invalida el cache desde ese punto en adelante.

Los tamaños de ventana y los precios cambian seguido. Consultalos en [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) y [model-config](https://code.claude.com/docs/en/model-config).

## En Claude Code

| Comando | Uso |
|---|---|
| `/context` | Ver qué está ocupando la ventana. |
| `/clear` | Contexto vacío. No cuesta nada. Para volver: `/resume`. |
| `/compact [foco]` | Resumir. Es caro si el cache está frío. |
| `/rewind` | Volver a un checkpoint. Reusa el cache; es mejor que compactar para descartar un camino. |
| `/btw` | Pregunta lateral que no entra al historial. |
| `/usage` | Consumo y uso del cache. |

- **Auto-compaction**: primero limpia tool outputs viejos y después resume. El umbral se ajusta con `/autocompact <tokens>` o el setting `autoCompactWindow`.
- **Qué sobrevive a una compaction**: el `CLAUDE.md` raíz, las reglas sin `paths:`, la auto memory y el plan. **No sobreviven** las instrucciones dadas en el chat, las reglas con `paths:` ni los `CLAUDE.md` anidados (estos últimos se recargan cuando se vuelve a tocar un archivo que los dispara).
- **Invalidan el cache**: cambiar de modelo o de effort (en la mayoría de los modelos), activar fast mode, agregar o quitar un MCP o un plugin con MCP (si sus tools no están diferidos), denegar un tool entero, hacer `/compact`, acumular muchas imágenes y actualizar Claude Code.
- **No lo invalidan**: editar archivos, invocar skills (salvo las que fijan otro `model`), `/rewind` y lanzar subagents. Editar `CLAUDE.md` tampoco, pero el cambio recién aplica después de `/clear`, `/compact` o un reinicio.

## En otras herramientas

- **Copilot CLI**: compacta solo al ~80% de la ventana. Tiene `/compact` y `/context`. `no probado`
- **Gemini CLI**: `/compress` resume y `/clear` reinicia. `no probado`

## Errores comunes

- **Sesión "kitchen sink"**: tareas que no tienen relación, mezcladas en la misma conversación. Solución: `/clear` entre tareas.
- **Corregir lo mismo más de dos veces**: el contexto ya está contaminado. Mejor `/clear` y un prompt mejor.
- **Reglas dichas en el chat**: se pierden al compactar. Las reglas persistentes van en la [memory](memory.md).
- **Cambiar de modelo a mitad de tarea**: se pierde el cache.
- **Volcar logs o tests enteros en la sesión principal**: filtrarlos con un [hook](hooks.md) o mandarlos a un [subagent](subagents.md).
- **Creer que el cache achica la ventana**: no la achica, solo abarata.

## Ver también

[agent](agent.md) · [memory](memory.md) · [subagents](subagents.md)
