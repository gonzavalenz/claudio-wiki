# Subagents: delegar sin ensuciar la conversación principal

> **En 30 segundos:** un subagent es otra instancia de Claude con su propio context window, su propio system prompt y sus propias tools. Hace el trabajo ruidoso (buscar, leer logs, correr tests) aparte y te devuelve solo el resumen. Claude Code trae algunos listos (Explore, Plan, general-purpose) y vos podés definir los tuyos como archivos Markdown en `.claude/agents/`.

## Qué es y cómo funciona

Cuando Claude delega, arranca un subagent con:

- **Su system prompt** (el cuerpo del archivo del agente, no el de Claude Code).
- **El mensaje de delegación** que escribe Claude.
- **`CLAUDE.md` y el git status** (salvo Explore y Plan, que los saltean para ser rápidos).
- **Las skills precargadas** en su campo `skills`, si tiene.

Lo que **no** ve: tu conversación, los archivos que ya se leyeron, las skills que ya invocaste. Todo lo que necesite saber tiene que ir en el prompt de delegación. La excepción es un *fork* (ver más abajo), que hereda la conversación completa.

Cuando termina, a tu conversación vuelve solo el resultado final. Las 40 lecturas de archivos y los 3 intentos fallidos quedan en el contexto del subagent.

### Subagents incluidos

| Subagent | Tools | Para qué lo usa Claude |
|---|---|---|
| **Explore** | Solo lectura (sin Write/Edit) | Buscar y entender código. Claude le pide un nivel: *quick*, *medium* o *very thorough* |
| **Plan** | Solo lectura | Investigar el repo mientras estás en [plan mode](09-plan-mode-y-checkpoints.md) |
| **general-purpose** | Todas las disponibles para subagents | Tareas de varios pasos que exploran **y** modifican |

Hay otros auxiliares (`statusline-setup`, `claude-code-guide`) que Claude usa solo.

## Cómo se usa

### Pedirle a Claude que delegue

No hace falta sintaxis especial:

```text
Usá un subagent para correr la suite de pytest y devolveme solo los tests que fallan con su error.
```

```text
Investigá en paralelo, con subagents separados, los DAGs de ingesta, los modelos de staging y los tests de dbt.
```

Para **forzar** un subagent concreto, mencionalo con `@` (elegilo en el typeahead o escribí `@agent-revisor-dbt`). Para que **toda la sesión** corra como ese agente: `claude --agent revisor-dbt`.

### Crear un subagent propio

Un subagent es un `.md` con frontmatter YAML. El cuerpo es su system prompt.

| Ubicación | Alcance |
|---|---|
| `.claude/agents/` | Este repo (commitealo para el equipo) |
| `~/.claude/agents/` | Todos tus proyectos |
| `agents/` de un [plugin](14-plugins.md) | Donde el plugin esté habilitado |
| `--agents '{...json...}'` | Solo esa sesión (útil para scripts) |

La forma más fácil de crearlo es pedírselo a Claude ("creá un subagent en `.claude/agents/` que…") y después revisar el archivo. En versiones recientes `/agents` ya no abre un asistente: solo te recuerda estas rutas.

Claude Code detecta cambios en esos archivos sin reiniciar, salvo cuando la carpeta `agents/` no existía al arrancar la sesión.

### Frontmatter

Solo `name` y `description` son obligatorios. Ojo: acá los campos compuestos van en **camelCase** (`disallowedTools`, `maxTurns`), al revés que en skills.

| Campo | Para qué |
|---|---|
| `name` | Identificador único (sin `:`) |
| `description` | Cuándo delegarle. Agregá "Usar proactivamente…" si querés que Claude lo use sin que se lo pidas |
| `tools` | Allowlist de tools (`Read, Grep, Glob, Bash`). Si no está, hereda todas |
| `disallowedTools` | Denylist sobre lo heredado (`Write, Edit`, o `mcp__github` para sacar un server MCP entero) |
| `model` | `sonnet`, `opus`, `haiku`, un ID completo o `inherit` |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | Tope de turnos; si lo alcanza, devuelve un resultado marcado como parcial |
| `skills` | Skills que se inyectan **completas** al arrancar |
| `mcpServers` | Servers MCP solo para este subagent |
| `hooks` | Hooks que corren solo mientras el subagent está activo |
| `memory` | `user`, `project` o `local`: un directorio de memoria propio que persiste entre sesiones |
| `isolation: worktree` | Trabaja en un [git worktree](15-paralelismo-y-worktrees.md) temporal propio |
| `background: true` | Corre siempre en background |
| `effort`, `color`, `omitClaudeMd` | Esfuerzo, color en la UI, arrancar sin `CLAUDE.md` |

## Ejemplo: revisor de modelos dbt

`.claude/agents/revisor-dbt.md`:

```markdown
---
name: revisor-dbt
description: Revisa modelos dbt nuevos o modificados (SQL + YAML) buscando errores de granularidad, joins que duplican filas, tests faltantes y consultas caras en BigQuery. Usar proactivamente después de crear o editar archivos en models/.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
---

Sos un revisor senior de modelos dbt sobre BigQuery. No editás archivos: solo reportás.

Para cada modelo que te pasen:

1. Leé el SQL y su YAML. Identificá el grano declarado (una fila por qué).
2. Revisá cada join: ¿puede ser 1:N y duplicar filas respecto del grano?
3. Verificá que la PK tenga tests `unique` y `not_null`.
4. Buscá `select *`, tablas hardcodeadas en vez de `ref()`/`source()` y filtros que no usan la columna de partición.
5. En modelos `incremental`, revisá `is_incremental()`, `unique_key`, `partition_by` y `cluster_by`.
6. Corré `dbt compile --select <modelo>` y estimá costo con `bq query --dry_run --use_legacy_sql=false` sobre el SQL compilado.

Antes de empezar, consultá tu memoria por problemas recurrentes de este repo. Al terminar, guardá en memoria los patrones nuevos que encontraste.

Formato de respuesta:
- BLOQUEANTE / SUGERENCIA, con `archivo:línea`, qué está mal y qué pasaría en producción.
- Bytes estimados por modelo.
- Si no encontraste nada, decilo explícitamente.
```

Uso:

```text
@agent-revisor-dbt revisá fct_ventas y dim_clientes, que toqué hoy
```

Con `memory: project`, el subagent guarda lo que aprende en `.claude/agent-memory/revisor-dbt/` (versionable), así cada revisión arranca sabiendo los errores típicos del repo.

## Cómo escribir el prompt de delegación

El subagent arranca en blanco. Un "arreglá el bug" produce resultados genéricos. Un buen prompt incluye:

```text
Objetivo: encontrar por qué el DAG ingesta_ventas duplica filas en raw.ventas desde el 12/09.
Contexto: el DAG está en dags/ingesta_ventas.py; el cambio sospechoso es el PR #231 (cambió el write_disposition).
Ya descartado: no es el source, el archivo de GCS tiene filas únicas.
Alcance: solo lectura, no toques archivos ni corras nada contra prod.
Devolvé: causa probable, archivo:línea y un fix propuesto en menos de 15 líneas.
```

Qué buscar, qué ya sabés, qué se descartó, límites y **formato de la respuesta**. Si una regla de `CLAUDE.md` es crítica para la tarea, repetila en el prompt.

## Paralelo, background y forks

- **Paralelo:** varias tareas independientes a la vez ("investigá A, B y C en paralelo"). Cada una vuelve con su resumen y Claude los sintetiza.
- **Background:** en sesiones interactivas los subagents corren en background por defecto: seguís trabajando y el resultado llega como notificación. `Ctrl+B` manda a background una tarea que está corriendo. `/tasks` lista lo que está corriendo (y lo que terminó hace poco).
- **Fork (`/subtask <tarea>`):** un subagent que **hereda toda la conversación**. Útil cuando explicarle el contexto a un subagent nuevo sería demasiado largo. Comparte el prompt cache con tu sesión, así que es más barato que uno nuevo.
- **Retomar:** un subagent custom o general-purpose que terminó se puede continuar ("seguí esa revisión y ahora mirá los tests"). Explore y Plan no se pueden retomar.
- Límites por defecto: hasta 3 niveles de subagents anidados y 20 corriendo a la vez.

Para varias **sesiones** en paralelo (no subagents dentro de una), ver [Paralelismo y worktrees](15-paralelismo-y-worktrees.md).

## Cuándo sí y cuándo no

| Delegá a un subagent cuando… | Resolvé en la conversación principal cuando… |
|---|---|
| La tarea genera mucho output que no vas a volver a mirar (logs, tests, búsquedas) | Necesitás ida y vuelta frecuente |
| Querés limitar tools (un revisor de solo lectura) | Las fases comparten mucho contexto (planear → implementar → testear) |
| Es autocontenida y alcanza con un resumen | Es un cambio chico y puntual |
| Querés una revisión "a ciegas", sin el sesgo de tu conversación | La latencia importa: un subagent nuevo tarda en juntar contexto |

Para una pregunta sobre algo que ya está en la conversación, usá `/btw`: ve todo tu contexto, no usa tools y no queda en el historial.

## Trucos y errores comunes

- **No delegues entendimiento.** Si vos no sabés qué querés, el subagent tampoco. Delegá tareas, no decisiones.
- **Cada subagent gasta tokens propios.** Cinco subagents en paralelo son cinco veces el consumo, y si cada uno devuelve un informe largo, igual te llena el contexto. Pedí resúmenes cortos.
- **Las descripciones cuestan contexto siempre.** Si la suma de las `description` de tus subagents pasa los 15.000 tokens, Claude Code avisa al arrancar. Detalle al cuerpo, no a la descripción.
- **Archivos que se ignoran en silencio:** sin `name`, con `name` pero sin `description`, YAML roto, o `---` que no está en la primera línea. Corré `claude plugin validate .claude/agents` o `claude --debug`.
- **Los subagents en background tienen menos tools** (por ejemplo, no pueden preguntarte con `AskUserQuestion`). Si un subagent depende de algo fuera de ese set, va a fallar distinto en foreground y background.
- **`disallowedTools: Bash(git push *)` saca Bash entero.** Para bloquear solo un comando, usá una regla `deny` en [permisos](07-permisos.md), que aplica también a subagents.
- **Las ediciones de un subagent en background no entran en los checkpoints**: `/rewind` no las deshace, usá git.
- **Subagent barato para explorar:** definí tu propio `Explore` en `.claude/agents/` con `model: haiku` y reemplaza al incluido.

## Ver también

- [Skills](10-skills.md) — `context: fork` (la skill pone la tarea) vs campo `skills` (el subagent pone el rol).
- [Paralelismo y worktrees](15-paralelismo-y-worktrees.md) — varias sesiones, agent view, `/batch`.
- [Hooks](12-hooks.md) — `SubagentStart` / `SubagentStop` y hooks en el frontmatter del agente.
- [Multi-agente con Gemini](17-multi-agente-gemini.md) — cuando conviene una segunda opinión de otro modelo.
- [Costos](21-costos.md) — cuánto suma delegar.
- Documentación oficial: [Subagents](https://code.claude.com/docs/en/sub-agents).
