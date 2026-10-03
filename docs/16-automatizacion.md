# Automatización: Claude Code sin nadie mirando

> **En 30 segundos:** `claude -p "prompt"` corre Claude Code de forma no interactiva: lee stdin, escribe stdout y sale con un exit code, como cualquier herramienta Unix. Sobre eso se arman scripts, pipes, jobs de CI con GitHub Actions y tareas programadas (`/loop` en la sesión, rutinas en la nube). Como nadie aprueba permisos sobre la marcha, todo lo que Claude pueda hacer tiene que estar autorizado de antemano.

## Qué es y cómo funciona

| Forma | Dónde corre | Para qué |
|---|---|---|
| `claude -p` (headless) | Tu máquina, un script, un runner de CI | Tareas puntuales y repetibles, pipes con otras CLIs |
| GitHub Actions (`claude-code-action`) | Runners de GitHub | Responder a `@claude` en PRs/issues, revisar PRs, reportes con cron |
| `/loop` | Tu sesión abierta | Polling corto: "fijate cada 10 minutos si terminó el DAG" |
| Tareas programadas de Desktop | Tu máquina, sin sesión abierta | Cron local con acceso a tus archivos |
| Rutinas (`/schedule`) | Nube de Anthropic | Cron, webhooks o eventos de GitHub, con tu laptop apagada |
| Agent SDK | Tu propia app Python/TypeScript | Construir un agente propio con el motor de Claude Code |

La regla de oro: **automatizá algo recién cuando ya lo hiciste a mano en modo interactivo** y el resultado es predecible.

## Cómo se usa: modo headless

```bash
claude -p "¿Qué hace el módulo dags/ingesta_ventas.py?"
```

### Flags que más se usan con `-p`

| Flag | Para qué |
|---|---|
| `--output-format text\|json\|stream-json` | Texto plano (default), JSON con `result`, `session_id` y costo, o eventos en streaming |
| `--json-schema '<schema>'` | Con `--output-format json`, fuerza una salida estructurada en el campo `structured_output` |
| `--allowedTools "Read,Bash(git diff *)"` | Tools que corren sin pedir permiso (sintaxis de [permisos](07-permisos.md)) |
| `--disallowedTools "Bash(bq rm *)"` | Reglas de deny para esa corrida |
| `--permission-mode dontAsk\|acceptEdits\|auto` | Base de permisos. `dontAsk` niega todo lo que no esté pre-aprobado: ideal para CI |
| `--max-turns N` | Tope de turnos del loop agéntico |
| `--max-budget-usd X` | Tope de gasto en dólares (incluye subagents) |
| `--model sonnet` | Modelo de la corrida |
| `--append-system-prompt "…"` | Agregar instrucciones sin perder el comportamiento por defecto |
| `--bare` | Arranca sin cargar hooks, skills, plugins, MCP, memoria ni `CLAUDE.md` del entorno. Recomendado para scripts y CI reproducibles (requiere `ANTHROPIC_API_KEY`) |
| `--mcp-config archivo.json` | Servers MCP explícitos para esa corrida |
| `--continue` / `--resume <id>` | Seguir una conversación anterior |

Exit code `0` si salió bien, distinto de cero si falló: los scripts pueden ramificar con eso. Dentro del prompt podés invocar skills del proyecto: `claude -p "/revisar-modelo-dbt fct_ventas"`.

### Pipes con Unix

```bash
# Explicar un error de build
cat dbt_build.log | claude -p "explicá en 3 líneas la causa raíz de este error" > causa.txt

# Revisar el diff de la rama contra main
git diff main -- models/ | claude -p "listá modelos con joins que puedan duplicar filas. Formato: archivo: motivo"

# Extraer datos estructurados y procesarlos con jq
claude -p "Listá los DAGs en dags/ con su schedule" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"dags":{"type":"array","items":{"type":"object","properties":{"dag_id":{"type":"string"},"schedule":{"type":"string"}},"required":["dag_id","schedule"]}}},"required":["dags"]}' \
  | jq '.structured_output.dags'
```

El stdin está limitado a 10 MB: para logs más grandes, filtrá antes o pasale la ruta del archivo.

## Ejemplo 1: resumen diario de fallas de DAGs de Airflow (Cloud Composer)

`scripts/resumen_fallas_dags.sh`:

```bash
#!/bin/bash
set -euo pipefail

gcloud logging read \
  'resource.type="cloud_composer_environment" AND severity>=ERROR' \
  --freshness=1d --limit=300 --format=json \
| claude -p --bare \
    --model sonnet \
    --max-turns 3 \
    --append-system-prompt "Sos on-call de data engineering. Respondé en español." \
    "Agrupá estos errores de Airflow por DAG y task. Para cada grupo: cantidad, primer y último timestamp, causa probable en una línea y si parece transitorio (reintentar) o requiere fix. Ordená por impacto. Si no hay errores, decilo." \
> "reportes/fallas_$(date +%F).md"
```

- El log entra por stdin, así que Claude **no necesita** permisos de Bash ni de GCP: el script hace la parte con credenciales y Claude solo analiza.
- `--bare` lo hace reproducible: no depende de hooks ni plugins de quien lo corre. Ojo: en modo bare no se usa tu login de suscripción, necesita `ANTHROPIC_API_KEY` en el entorno; si lo corrés con tu suscripción, sacá `--bare`.
- Lo podés colgar de un cron local, de un job de CI o de una [tarea programada](#tareas-programadas).

## Ejemplo 2: revisar PRs de dbt en CI con GitHub Actions

### Setup rápido

En una sesión dentro del repo:

```text
/install-github-app
```

Instala la GitHub App de Claude en el repo, guarda el secret (`ANTHROPIC_API_KEY`, o `CLAUDE_CODE_OAUTH_TOKEN` si usás tu suscripción) y abre un PR con los workflows. Con eso, mencionar `@claude` en un PR o issue ya funciona. Requiere `gh` autenticado y permisos de admin en el repo; solo github.com.

### Workflow que revisa solo cambios en `models/`

`.github/workflows/revision-dbt.yml`:

```yaml
name: Revisión de modelos dbt
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
    paths:
      - "models/**"

jobs:
  revisar:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Revisá los modelos dbt modificados en este PR.
            Obtené el diff con: git diff origin/${{ github.base_ref }}...HEAD -- models/
            Buscá: joins que dupliquen filas respecto del grano, PK sin tests unique/not_null,
            select *, refs hardcodeadas en vez de ref()/source(), incrementales sin unique_key
            o sin filtro is_incremental().
            Dejá un comentario inline por cada problema, con qué pasaría en producción.
            Si no hay problemas, no comentes nada.
          claude_args: |
            --max-turns 15
            --allowedTools "Read,Grep,Glob,Bash(git diff *),mcp__github_inline_comment__create_inline_comment"
```

- Con `prompt`, la action corre en **modo automatización** (no espera un `@claude`).
- `--allowedTools` acota lo que puede hacer y, además, es lo que habilita la tool de comentarios inline.
- Las reglas del equipo van en el `CLAUDE.md` del repo: la action lo lee en cada corrida.
- Si ya tenés una skill de revisión en `.claude/skills/`, podés pasar `prompt: "/revisar-modelo-dbt"` directamente.
- Para revisiones automáticas sin mantener un workflow, también existe el producto [Code Review](https://code.claude.com/docs/en/code-review) y el comando `/code-review`.

## Tareas programadas

### `/loop`: repetir algo mientras la sesión está abierta

```text
/loop 10m fijate en Composer si terminó el DAG backfill_eventos y avisame si alguna task falló
/loop revisá si el PR #231 tiene checks en rojo
/loop 20m /revisar-modelo-dbt fct_ventas
```

- Con intervalo (`s`, `m`, `h`, `d`) corre a cadencia fija; sin intervalo, Claude elige cuándo volver a mirar y puede cortar solo cuando termina.
- Solo corre **mientras Claude Code está abierto y ocioso**. `Esc` frena un loop auto-regulado; "cancelá el loop del deploy" borra uno fijo.
- Las tareas recurrentes expiran a los 7 días.
- Para un recordatorio único: "en 45 minutos fijate si pasaron los tests de integración".

### Rutinas: cron en la nube

```text
/schedule todos los días hábiles a las 8 revisá los issues de Linear con label "datos" abiertos ayer y armá un resumen
```

Una rutina es un prompt + repos + conectores que corre en la infraestructura de Anthropic, con disparadores por **horario**, **API** (POST a un endpoint) o **eventos de GitHub**. Corre aunque tu máquina esté apagada. Se gestionan en [claude.ai/code/routines](https://claude.ai/code/routines) o con `/schedule`. Está en *research preview*, para planes Pro, Max, Team y Enterprise, con intervalo mínimo de 1 hora.

Ojo: corre con un clon fresco del repo, **sin** tus archivos locales, sin tus skills de `~/.claude/skills/` y sin tus plugins; lo que necesite tiene que estar commiteado en el repo o ser un conector. Y no pide permisos: todo lo que haga sale con tu identidad de GitHub y tus conectores.

### Cuál elegir

| | `/loop` | Tarea de Desktop | Rutina (nube) |
|---|---|---|---|
| Necesita máquina prendida | Sí | Sí | No |
| Necesita sesión abierta | Sí | No | No |
| Acceso a archivos locales | Sí | Sí | No (clon fresco) |
| Intervalo mínimo | 1 minuto | 1 minuto | 1 hora |

Para cron "clásico" también podés usar un `schedule` en GitHub Actions con la misma action de arriba.

## Agent SDK

Si querés construir tu propio agente (un bot de on-call que mira alertas, un servicio que valida contratos de datos), el **Claude Agent SDK** te da el mismo loop agéntico, tools, permisos, hooks, subagents y MCP de Claude Code como librería de Python (`pip install claude-agent-sdk`) o TypeScript (`npm install @anthropic-ai/claude-agent-sdk`). Lee también los `.claude/` del proyecto, así que tus skills y `CLAUDE.md` funcionan igual.

La diferencia con `claude -p` es el control: en vez de parsear JSON de un subproceso, iterás mensajes tipados y podés aprobar tools con callbacks propios. Para scripts y CI, `claude -p` alcanza; el SDK conviene cuando el agente es parte de una aplicación. Se autentica con API key (no con login de claude.ai). Arrancá por el [quickstart oficial](https://code.claude.com/docs/en/agent-sdk/quickstart).

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    async for message in query(
        prompt="Revisá dags/ingesta_ventas.py y listá tasks sin retries configurados.",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob"]),
    ):
        if isinstance(message, ResultMessage):
            print(message.subtype)


asyncio.run(main())
```

## Trucos y errores comunes

- **Pasá los datos por stdin en vez de darle permisos.** `gh pr diff 231 | claude -p "…"` no necesita que Claude pueda correr `gh`.
- **`--allowedTools` con espacio antes del `*`**: `Bash(git diff *)` matchea `git diff …`; `Bash(git diff*)` también matchea `git diff-index`.
- **En `-p` no hay a quién preguntar.** Lo que no esté pre-aprobado se niega. En CI combiná `--permission-mode dontAsk` con un `--allowedTools` mínimo.
- **Ponele techo a todo:** `--max-turns`, `--max-budget-usd` y `timeout-minutes` en el workflow. Un agente sin límite en CI es una factura sin límite.
- **Repos que no controlás:** sin `--bare`, `claude -p` corre los hooks de `.claude/settings.json` y conecta los servers de `.mcp.json` del repo sin preguntar, aunque nunca hayas confiado en esa carpeta.
- **OAuth de MCP no funciona en headless**: autenticá esos servers antes en una sesión interactiva.
- **Secrets**: nunca en el workflow ni en el repo. `ANTHROPIC_API_KEY` como secret de GitHub; para varios repos, secret de organización con una API key (el token OAuth queda atado a la suscripción de quien lo generó).
- **`--output-format json` incluye `total_cost_usd`**: logealo para saber cuánto cuesta cada corrida automatizada.
- **`/loop` no sobrevive a cerrar la terminal.** Si tiene que correr de verdad, usá una rutina, una tarea de Desktop o Actions.

## Ver también

- [Permisos](07-permisos.md) — reglas y modos de permiso, clave para correr sin supervisión.
- [Hooks](12-hooks.md) — guardarraíles que también aplican en headless.
- [Paralelismo y worktrees](15-paralelismo-y-worktrees.md) — sesiones en background con `claude --bg`.
- [Arquitecturas de integración](18-arquitecturas-de-integracion.md) — cómo encaja cada forma en el flujo del equipo.
- [Costos](21-costos.md).
- Documentación oficial: [Headless / CLI](https://code.claude.com/docs/en/headless) · [GitHub Actions](https://code.claude.com/docs/en/github-actions) · [Tareas programadas](https://code.claude.com/docs/en/scheduled-tasks) · [Rutinas](https://code.claude.com/docs/en/routines) · [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).
