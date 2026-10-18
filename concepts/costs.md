# Costs

> verificado: 2026-10-18 · fuentes: [Pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Costs (Claude Code)](https://code.claude.com/docs/en/costs), [Prompt caching (Claude Code)](https://code.claude.com/docs/en/prompt-caching), [Statusline](https://code.claude.com/docs/en/statusline), [Commands](https://code.claude.com/docs/en/commands), [Antigravity credits](https://antigravity.google/docs/cli/credits)

El costo de un agent son tokens: input (todo el contexto, en cada turno), output (incluido el thinking) y escrituras y lecturas de cache. En un plan de suscripción, el límite son los rate limits; con API key, la factura.

## Cómo funciona

- **Input domina**: en cada turno se reenvía todo el contexto. Una sesión larga paga su historial una y otra vez. → [context](context.md)
- **Output cuesta ~5x el input** en los modelos Claude. El thinking se cobra como output; en los modelos 5.5 y Fable no se puede apagar, solo se baja con `/effort`.
- **Prompt caching**: leer del cache cuesta ~0,1x el input (0,05x en Opus/Sonnet 5.5; 0,025x en Fable/Mythos 5.1). Escribir cuesta 1,25x con TTL de 5 min, o 2x con TTL de 1 h. El cache de 5 min se amortiza con 1 hit y el de 1 h con 2.
- **Multiplicadores**: cada [subagent](subagents.md) o teammate es otro contexto que se paga. Agent teams con teammates en plan mode consumen ~7x. → [multi-agent](multi-agent.md)
- **Modelo**: las diferencias de precio entre tiers son grandes (Haiku < Sonnet < Opus < Fable). Los precios cambian seguido: consultalos en [Pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- **Batch API**: −50% para lo que no necesita respuesta inmediata. No aplica al uso interactivo.

Referencia de Anthropic para Claude Code en enterprise: ~US$13 por dev y día activo, y el 90% queda por debajo de US$30 por día.

## En Claude Code

| Herramienta | Qué muestra |
|---|---|
| `/usage` | Costo estimado de la sesión, hit ratio del cache (solo la conversación principal) y, en planes pagos, el consumo por skill, subagent y MCP |
| `/context` | Qué ocupa la ventana |
| Statusline | `cost.total_cost_usd`, `context_window.used_percentage`, `rate_limits.*` (solo Pro/Max), en vivo y sin consumir tokens |
| `claude -p --output-format json` | `total_cost_usd` (estimación del cliente) |

- **TTL del cache**: con suscripción, la conversación principal usa 1 h; con API key, 5 min. La suscripción baja a 5 min al consumir usage credits. Subagents, teammates y compaction usan 5 min por defecto. Se configura con `promptCacheTtl` y `subagentPromptCacheTtl`.
- **Por qué sube el consumo en sesiones largas**: el contexto crece, el cache falla después de las pausas, y se suman scheduled tasks, check-ins de `/goal` y subagents.

## En otras herramientas

- **Antigravity CLI**: `/credits` y `/usage`, con los créditos en la statusline. `no probado`

## Errores comunes

- **Retomar una sesión enorme después de una pausa larga**: el cache expiró y se repaga todo el contexto. Mejor `/clear` o una sesión nueva.
- **Usar Opus para todo**: para subagents mecánicos, `model: haiku`.
- **Cambiar de modelo o de effort a mitad de una tarea**: invalida el cache. Las excepciones están en [context](context.md).
- **MCPs y plugins habilitados que no se usan**: suman contexto en cada turno.
- **Comparar modelos por precio por token**: el tokenizer de 4.7+ genera ~30% más tokens para el mismo texto.

## Ver también

[context](context.md) · [multi-agent](multi-agent.md) · [practices](../practices.md)
