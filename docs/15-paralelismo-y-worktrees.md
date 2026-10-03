# Paralelismo y worktrees: varias tareas a la vez sin pisarse

> **En 30 segundos:** para trabajar en paralelo tenés dos niveles. Dentro de una sesión, Claude delega a [subagents](11-subagents.md). Entre sesiones, corrés varios `claude` a la vez, cada uno en su propio **git worktree** (`claude -w nombre`) para que ninguno edite los archivos del otro. Para despachar y monitorear muchas sesiones desde una pantalla está `claude agents`.

## Qué es y cómo funciona

El problema de correr dos sesiones de Claude sobre la misma carpeta: las dos editan los mismos archivos, una rompe lo que la otra está probando y los diffs se mezclan.

Un **git worktree** resuelve eso: es otro directorio de trabajo, con su propia rama y sus propios archivos, que comparte el historial y el remoto con tu checkout principal. Dos sesiones en dos worktrees nunca se pisan los archivos; después mergeás las ramas como siempre.

### Las opciones, de menor a mayor escala

| Opción | Qué es | Cuándo |
|---|---|---|
| **Subagents** | Workers dentro de una sesión; devuelven un resumen | Investigar varias cosas a la vez, aislar output ruidoso |
| **`/subtask`** | Un subagent que hereda toda tu conversación y corre en background | Una tarea lateral que necesita todo el contexto actual |
| **`claude -w <nombre>`** | Una sesión en su propio worktree | Dos o tres features/bugs en paralelo que manejás vos |
| **Agent view (`claude agents`)** | Una pantalla para despachar y vigilar sesiones en background. *Research preview* | Varias tareas independientes que querés "tirar" y revisar después |
| **`/batch <instrucción>`** | Skill incluida: parte un cambio grande en 5–30 unidades, cada una en un subagent con su worktree | Migraciones masivas y mecánicas |
| **Agent teams** | Varias sesiones coordinadas por un líder, con tareas compartidas. Experimental, apagado por defecto | Trabajo que necesita que los workers se hablen entre sí |

## Cómo se usa

### Una sesión por worktree con `--worktree`

```bash
claude --worktree fix-ingesta-ventas     # o: claude -w fix-ingesta-ventas
```

Claude Code crea `.claude/worktrees/fix-ingesta-ventas/` en la raíz del repo, en una rama nueva `worktree-fix-ingesta-ventas` que sale de la rama por defecto del remoto (normalmente `main`). En otra terminal:

```bash
claude -w modelo-dim-clientes
```

Y ya tenés dos sesiones aisladas. Otras variantes:

```bash
claude -w                       # nombre generado automáticamente
claude -w "#231"                # worktree a partir del PR #231 (comillas por el #)
claude -w fix-ingesta --tmux    # además abre una sesión de tmux para el worktree
```

Al salir, si el worktree no tiene cambios se borra solo; si tiene trabajo, Claude te pregunta si conservarlo y te imprime el comando para retomarlo (`claude --worktree <nombre> --resume`).

También podés pedírselo en medio de una sesión: "trabajá en un worktree".

### Preparar el entorno de cada worktree

Un worktree es un checkout limpio: no tiene tu `.venv`, ni tu `.env`, ni `target/` de dbt.

- **Archivos gitignoreados que necesitás copiar** (`.env`, credenciales locales): listalos en `.worktreeinclude` en la raíz del repo, con sintaxis de `.gitignore`.

  ```text
  .env
  .env.local
  ```

- **Dependencias:** pedile a Claude que las instale al empezar, o hacelo vos (`uv sync`, `pip install -r requirements.txt`, `dbt deps`).
- **Agregá `.claude/worktrees/` a tu `.gitignore`** para que no aparezcan como archivos sin trackear.
- Si querés que los worktrees salgan de tu rama actual (con commits sin pushear) en vez de `main`, en settings: `{"worktree": {"baseRef": "head"}}`.

### Worktrees a mano

Para salir de una rama existente o ubicar el worktree fuera del repo:

```bash
git worktree add ../datos-fix-dag -b fix/dag-ventas     # rama nueva
git worktree add ../datos-revision feature/nuevo-modelo  # rama existente
cd ../datos-fix-dag && claude

git worktree list
git worktree remove ../datos-fix-dag
```

### Sesiones en background con agent view

```bash
claude agents                                            # abre la pantalla de agentes
claude --bg "investigá por qué falla el test test_dedupe_ventas"
claude --bg --name backfill-plan "proponé un plan de backfill para raw.eventos de septiembre"
claude --agent revisor-dbt --bg "revisá los modelos tocados en la rama feature/costos"
```

En agent view escribís un prompt y `Enter` despacha una sesión nueva; `Espacio` espía la última salida y te deja responder; `Enter` o `→` te mete en la sesión completa; `←` vuelve a la tabla. Desde una sesión normal, `/bg` (o `←` con el prompt vacío) la manda a background.

Las sesiones en background **se mueven solas a un worktree propio antes de editar archivos**, y al terminar commitean y pushean su rama (nunca a `main`, nunca force-push), salvo que tu `CLAUDE.md` diga que de git te encargás vos.

### Subagents en paralelo y con worktree

```text
Usá subagents en paralelo, cada uno en su propio worktree, para agregar tests de pytest a los tres DAGs de dags/ingesta/.
```

O fijalo en el subagent con `isolation: worktree` en su frontmatter. Y para cambios masivos:

```text
/batch migrá todos los DAGs de dags/ de PythonOperator con provide_context a la TaskFlow API (@task)
```

`/batch` investiga, propone un plan con las unidades de trabajo, y cuando lo aprobás lanza un subagent por unidad, cada uno en su worktree, que implementa, corre tests y publica su cambio.

## Ejemplo: una mañana con tres frentes abiertos

```bash
# Terminal 1: bug urgente en producción
claude -w fix-dup-ventas
> El DAG ingesta_ventas duplica filas desde el PR #231. Encontrá la causa, arreglalo y agregá un test.

# Terminal 2: feature nueva
claude -w dim-clientes-scd2
> Convertí dim_clientes en un snapshot SCD2 de dbt. Primero proponé el plan.

# Terminal 3 (o agent view): tarea larga que no necesita supervisión
claude --bg --name auditoria-costos "Listá los 20 modelos dbt que más bytes escanean según bq query --dry_run y proponé mejoras de partición/cluster. Solo lectura."
```

Mientras tanto vos revisás el plan de la terminal 2. Cuando el bug está listo, revisás el diff de esa rama, abrís el PR y cerrás la sesión.

## Trucos y errores comunes

- **Paralelo multiplica tokens.** Diez sesiones gastan cuota más o menos diez veces más rápido que una. Empezá con 2–3.
- **Dividí por archivos, no por "temas".** Aunque cada sesión tenga su worktree, si dos ramas tocan el mismo modelo vas a tener conflictos al mergear. Asigná a cada sesión un conjunto de archivos distinto.
- **Los worktrees no comparten `.venv` ni `target/`**: cada uno necesita su setup. Sumá el comando de setup a `CLAUDE.md` para que Claude lo corra solo.
- **Lo que sí comparten:** el `.git`, los plugins de scope project, las aprobaciones de permisos ("no preguntar de nuevo" se guarda en el checkout principal) y las skills/agentes de `.claude/` si el worktree no tiene su propia carpeta.
- **Hooks en worktrees:** `$CLAUDE_PROJECT_DIR` sigue apuntando al checkout principal; si tu hook necesita el directorio del worktree, leé el campo `cwd` del JSON de entrada.
- **Corridas `claude -p -w` no se limpian solas**: borrá esos worktrees con `git worktree remove` (y `git worktree unlock` si git se queja).
- **Agent view borra el worktree al borrar la sesión**: commiteá antes de borrar una sesión que editó archivos.
- **Agent teams** se habilitan con `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` en el `env` de settings. Gastan bastante más que subagents y no aíslan con worktrees: probalos solo para trabajo que realmente necesita coordinación entre workers.
- **¿Querés otro modelo como segunda opinión en paralelo?** Ver [Multi-agente con Gemini](17-multi-agente-gemini.md).

## Ver también

- [Subagents](11-subagents.md) — paralelismo dentro de una sesión, forks, `isolation: worktree`.
- [Automatización](16-automatizacion.md) — correr Claude sin supervisión: headless, CI, tareas programadas.
- [Git básico](git-basico.md) — ramas y merges, para integrar lo que sale de cada worktree.
- [Costos](21-costos.md) — cuánto suma trabajar en paralelo.
- Documentación oficial: [Worktrees](https://code.claude.com/docs/en/worktrees) · [Agentes en paralelo](https://code.claude.com/docs/en/agents) · [Agent view](https://code.claude.com/docs/en/agent-view).
