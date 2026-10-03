# Costos

> **En 30 segundos:** Claude Code cobra por tokens. Cada mensaje reenvía toda la conversación (cacheada, pero se cobra igual), así que lo que más gasta es **contexto largo**, no la pregunta en sí. Medilo con `/usage` y la status line; ahorrá con `/clear`, el modelo justo, subagents para lo verboso y CLI antes que MCP.

## Qué es / cómo funciona

### Cómo se cobra

| Si usás... | Cómo pagás | Dónde mirás |
|---|---|---|
| Suscripción (Pro, Max, Team, Enterprise) | Incluido en el plan, con límites por ventana de 5 horas y semanal. Pasado el límite, *usage credits* si están habilitados | `/usage` (barras del plan) |
| API key (Claude Console) | Por token, a precio de lista | `/usage` (estimado) y la página Usage de la Console (lo real) |
| Google Cloud (Agent Platform / Vertex), Bedrock, Foundry | Por token, a tu cuenta de la nube | Billing del proveedor (Claude Code no le reporta a Anthropic) |

Referencia oficial: en empresas, el promedio ronda los **USD 13 por developer por día activo** (USD 150–250 por mes), y el 90 % queda debajo de USD 30 por día.

### Qué gasta tokens

- **El contexto entero, en cada request.** Cada mensaje y cada tanda de resultados de tools manda toda la conversación. El prompt caching lo abarata (lee a tarifa de cache), pero una pregunta de una línea en una sesión abierta todo el día "carga" todo el día.
- **Cache misses.** Después de una pausa más larga que la vida del cache (1 hora en suscripción; 5 minutos por API o usando usage credits), el primer mensaje reprocesa todo el contexto a precio completo.
- **Thinking.** El razonamiento extendido se cobra como output y puede ser decenas de miles de tokens por request.
- **Subagents, workflows y agent teams.** Cada uno hace sus propias requests. Los agent teams usan ~7x más tokens que una sesión normal.
- **Lo que leés.** Archivos enteros, logs, salidas de comandos largas: todo queda en el contexto.
- **MCP.** Las definiciones de tools se cargan diferidas (solo nombres hasta que se usan), pero cada server suma algo; un CLI (`bq`, `gcloud`, `gh`) no suma nada hasta que se corre.
- **`/compact`.** Lee toda la conversación para resumirla: es una request grande. `/clear` no cuesta nada.
- **Cosas que corren solas.** `/loop`, tareas programadas y goals mandan el contexto completo en cada disparo. En background hay un consumo chico (resúmenes para `--resume`, sugerencias de prompt): típicamente menos de USD 0,04 por sesión.

## Cómo se usa

### `/usage` (alias `/cost` y `/stats`)

Muestra el costo estimado de la sesión, tokens por modelo, estadísticas del prompt cache y, en planes de suscripción, las barras de límite y un desglose de qué consumió (skills, subagents, MCP). El monto en dólares es un **estimado a precio de lista** calculado localmente; se resetea con `/clear`. Para suscriptores, ese monto no es lo que pagás: mirá las barras.

### Status line con costo y contexto

`/statusline` y describí lo que querés ("modelo, % de contexto y costo"), o armala a mano en `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

`~/.claude/statusline.sh` (`chmod +x`):

```bash
#!/bin/bash
input=$(cat)
modelo=$(jq -r '.model.display_name' <<<"$input")
ctx=$(jq -r '.context_window.used_percentage // 0 | floor' <<<"$input")
costo=$(jq -r '.cost.total_cost_usd // 0' <<<"$input")
limite5h=$(jq -r '.rate_limits.five_hour.used_percentage // empty | floor' <<<"$input")

linea="[$modelo] ctx ${ctx}% | \$$(printf '%.2f' "$costo")"
[ -n "$limite5h" ] && linea="$linea | 5h ${limite5h}%"
echo "$linea"
```

Campos útiles que recibe el script: `cost.total_cost_usd`, `context_window.used_percentage`, `rate_limits.five_hour.used_percentage` / `seven_day` (planes de suscripción), `model.display_name`, `effort.level`.

### Topes en automatización

```bash
claude -p "revisá los modelos cambiados" --max-turns 15 --max-budget-usd 2
```

`--max-budget-usd` corta cuando el gasto estimado llega al tope (incluye subagents). Solo en modo `-p`.

## Ejemplo

Misma tarea, dos formas:

| ❌ Caro | ✅ Barato |
|---|---|
| Sesión abierta desde la mañana con 4 temas mezclados | `/clear` entre temas, `/rename` para retomar si hace falta |
| "Fijate por qué falla el DAG" + Claude lee 40 archivos en la sesión principal | "Usá un subagent para investigar..." → vuelve solo la conclusión |
| Pegar un log de 10.000 líneas | `grep -n ERROR composer.log \| tail -50` y pegar eso (o un hook que filtre) |
| Opus con esfuerzo máximo para renombrar columnas | Modelo default, `/effort low` |
| 5 servers MCP conectados "por las dudas" | Solo los que usás hoy; `bq`/`gcloud` por Bash |
| Corregir 5 veces el mismo error en la misma sesión | A la segunda, `/clear` y mejor prompt |

## Trucos y errores comunes

- **`/clear` entre tareas** es el ahorro número uno. `/rename` antes para poder volver con `/resume`.
- **`/context`** te muestra qué está comiendo el context window (archivos, MCP, memoria, skills).
- **`CLAUDE.md` corto**: se carga en cada sesión. Lo específico, a skills (se cargan solo cuando se usan). `/skill-doctor` muestra cuánto contexto ocupa cada skill.
- **Modelo por tarea**: default para el día a día, `opus` para lo difícil, `model: haiku` en subagents mecánicos. Cambiar a Opus también cambia los subagents que heredan el modelo.
- **Bajá el esfuerzo** con `/effort` en tareas simples: el thinking se cobra como output.
- **Prompts específicos**: "mejorá el repo" dispara lectura masiva; "agregá un test unique a `order_id` en `fct_ventas.yml`" lee dos archivos.
- **Corregí temprano** con `Esc`: cada paso en la dirección equivocada se paga dos veces (ir y deshacer).
- **No dejes la sesión idle una hora y volvé con una pregunta chica**: el cache expiró y reprocesa todo. Si es otro tema, `/clear`.
- **Instrucciones de compactación** en `CLAUDE.md` ("al compactar, conservá la lista de archivos modificados y los comandos de test") para que `/compact` no pierda lo importante.
- **El otro costo: BigQuery.** Que Claude corra `bq query` sin mirar cuesta más que los tokens. Allowlist para `--dry_run`, confirmación para lo real ([guardia de BigQuery](../ejemplos/hooks/README.md)) y `BIGQUERY_MAXIMUM_BYTES_BILLED` en el [MCP](../ejemplos/mcp/README.md).

## Ver también

- [05 — Contexto](05-contexto.md) · [04 — Modelos](04-modelos.md) · [11 — Subagents](11-subagents.md) · [16 — Automatización](16-automatizacion.md)
- [Buenas prácticas → Costos](../buenas-practicas/README.md#costos) · [Cheatsheet](cheatsheet.md)
- Doc oficial: [Manage costs effectively](https://code.claude.com/docs/en/costs) · [Status line](https://code.claude.com/docs/en/statusline)
