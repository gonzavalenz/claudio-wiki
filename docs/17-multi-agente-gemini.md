# Multi-agente: delegar tareas chicas a Gemini

> **En 30 segundos:** Claude Code coordina y decide; Gemini (vía Antigravity CLI) hace tareas chicas de solo lectura —segundas opiniones, revisiones mecánicas, resúmenes— que Claude le delega desde la propia sesión con `agy -p`. Un modelo distinto aporta una mirada independiente sin ensuciar tu contexto principal.

## Por qué sumar otro agente

Un [subagent](11-subagents.md) de Claude ya resuelve la mayoría de las delegaciones. Gemini suma valor en un caso puntual: **una segunda opinión de otro modelo**, con otros sesgos. Sirve para detectar cosas que Claude pasa por alto sobre su propio trabajo (términos inconsistentes, links rotos, explicaciones confusas).

| Usá… | Cuando… |
|---|---|
| Inline (Claude solo) | Ya sabés qué hacer y dónde |
| [Subagent](11-subagents.md) | Exploración larga o tareas en paralelo con contexto de Claude |
| Gemini (`agy -p`) | Querés una revisión independiente, de otro modelo, de solo lectura |

## Setup

> **Gemini CLI (`gemini`) ya no sirve para cuentas individuales**: falla con `IneligibleTierError` y pide migrar a Antigravity. El reemplazo es **Antigravity CLI** (`agy`).

1. Instalá Antigravity desde [antigravity.google](https://antigravity.google) y verificá:

```bash
agy --help
agy models          # modelos disponibles (Gemini Flash/Pro, entre otros)
```

2. Probá el modo headless:

```bash
agy -p "Leé GIT.md y resumilo en 3 bullets." --mode plan --model gemini-3.8-flash-medium
```

Flags clave:

| Flag | Para qué |
|---|---|
| `-p "<prompt>"` | Modo no interactivo: corre un prompt e imprime la respuesta |
| `--mode plan` | Solo lectura: lee el repo pero no edita (si le pedís un cambio, devuelve un plan) |
| `--model <id>` | Flash para tareas rápidas; Pro para razonamiento más profundo |
| `--print-timeout 5m` | Corta si tarda demasiado |
| `--output-format json` | Salida estructurada si la vas a procesar con un script |

Antigravity lee `AGENTS.md` de forma nativa, así que conoce las reglas del repo sin configuración extra.

## Cómo se usa desde Claude Code

El repo trae la skill [`delegar-a-gemini`](../.claude/skills/delegar-a-gemini/SKILL.md), con un wrapper que fija modo solo lectura, modelo y timeout:

```bash
.claude/skills/delegar-a-gemini/scripts/gemini.sh "Leé docs/13-mcp.md y marcá afirmaciones que no estén respaldadas por un comando o config concreta."
```

En la práctica le hablás a Claude y él la invoca:

```text
> pasale a Gemini una revisión de términos de docs/10-skills.md y docs/11-subagents.md
> pedile a Gemini segunda opinión sobre models/staging/stg_ventas.sql: ¿hay algo que rompa el incremental?
```

Para revisiones que querés procesar después, guardalas en el buzón:

```bash
.claude/skills/delegar-a-gemini/scripts/gemini.sh -o .agents/inbox/2026-10-02-revision-terminos.md "..."
```

Claude revisa `.agents/inbox/` al empezar a trabajar, incorpora lo que vale la pena y borra el archivo (ver [`AGENTS.md`](../AGENTS.md)).

## Ejemplo: revisión cruzada de un modelo dbt

```text
> Escribí el modelo incremental fct_ventas_diarias. Cuando termines, pasale a Gemini
  el SQL y el schema.yml para que busque problemas con el is_incremental() y la
  unique_key. Traeme sus observaciones y decidí cuáles aplicar.
```

Claude escribe el modelo, delega la revisión (solo lectura), evalúa las observaciones y aplica las que correspondan. Vos ves un solo hilo.

## Trucos y errores comunes

- **El prompt tiene que ser autocontenido.** Gemini no ve tu conversación con Claude: pasale rutas, qué buscar y el formato de respuesta.
- **En headless no puede correr comandos.** Si Gemini intenta un `grep` o `ls`, se lo niegan automáticamente y termina **sin respuesta** (`"response": ""` con `denied_actions` en la salida JSON). El wrapper le indica que solo lea archivos y avisa si la respuesta viene vacía. Nombrale los archivos exactos en vez de pedirle que "busque en todo el repo".
- **Tareas chicas.** Cada llamada tarda ~30–60 s con Flash. Si algo necesita ida y vuelta, no es para Gemini.
- **Solo lectura siempre.** Si los dos agentes editan, se pisan. Gemini propone, Claude aplica.
- **No le creas a ciegas sobre Claude Code.** Gemini puede no conocer comandos recientes; lo que proponga sobre features de Claude Code verificalo contra la doc oficial.
- **Para tareas largas**, pedile a Claude que lo corra en background y siga con otra cosa.

## Ver también

- [Subagents](11-subagents.md) — la alternativa nativa para delegar.
- [Automatización](16-automatizacion.md) — el mismo patrón headless con `claude -p`.
- [`AGENTS.md`](../AGENTS.md) — roles entre Claude Code y Antigravity.
