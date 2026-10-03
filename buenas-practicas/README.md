# Buenas prácticas: los mandamientos

Reglas cortas para sacarle el jugo a Claude Code. Cada una: **regla → por qué → cómo**. La mayoría salen de la [guía oficial de best practices](https://code.claude.com/docs/en/best-practices); los ejemplos son del stack de datos (dbt, BigQuery, Airflow).

> Si te acordás de una sola: **el context window es el recurso escaso**. Casi todas las reglas de abajo son formas de cuidarlo o de no tener que corregir dos veces.

**Índice:** [Contexto](#contexto) · [Prompting y plan](#prompting-y-plan) · [Verificación](#verificación) · [CLAUDE.md](#claudemd) · [Delegación y subagents](#delegación-y-subagents) · [Permisos y seguridad](#permisos-y-seguridad) · [Git](#git) · [Costos](#costos)

---

## Contexto

### 1. `/clear` entre tareas que no tienen nada que ver

- **Por qué:** cada mensaje reenvía toda la conversación. Lo viejo e irrelevante cuesta tokens en cada turno y distrae al modelo ("la sesión cajón de sastre").
- **Cómo:** terminaste el bug del DAG y vas a hacer un modelo dbt → `/rename dag-fix`, `/clear`. Si después necesitás volver: `/resume`.

### 2. Si corregiste dos veces lo mismo, empezá de cero

- **Por qué:** después de dos correcciones fallidas el contexto está lleno de intentos equivocados, y el modelo los sigue "viendo".
- **Cómo:** `/clear` y un prompt nuevo que ya incluya lo que aprendiste ("no uses `MERGE`, la tabla no tiene PK; usá `WRITE_TRUNCATE` sobre la partición"). Una sesión limpia con mejor prompt casi siempre le gana a una larga con parches.

### 3. Mirá cuánto contexto llevás

- **Por qué:** cerca del límite, Claude Code compacta solo y algo se pierde en el resumen. Mejor decidir vos qué conservar.
- **Cómo:** `/context` muestra qué ocupa espacio (archivos, MCP, memoria). Con `/compact conservá la lista de archivos modificados y los comandos de test` resumís con foco. Para una pregunta al paso que no querés que quede en el historial: `/btw`.

---

## Prompting y plan

### 4. Explorar → planificar → implementar → commitear

- **Por qué:** arrancar a codear sin entender lleva a resolver bien el problema equivocado. Rehacer sale más caro que planear.
- **Cómo:** `Shift+Tab` hasta plan mode (o `/plan`), pedile que lea y proponga; revisá el plan (`Ctrl+G` para editarlo en tu editor); recién cuando lo aprobás empieza a editar; al final, commit. Para un cambio de una línea, salteá el plan.

### 5. Sé específico: qué, dónde, cómo se ve terminado

- **Por qué:** "mejorá este modelo" dispara exploración amplia y resultados genéricos. Un pedido preciso lee menos archivos y acierta más.
- **Cómo:** ❌ "arreglá el modelo de ventas" → ✅ "en `models/marts/fct_ventas.sql` hay duplicados por `order_id` desde que se agregó el join con `stg_pagos`. Encontrá la causa, arreglala sin `DISTINCT` y agregá un test `unique` sobre `order_id`."

### 6. Referenciá archivos con `@` y pegá la evidencia real

- **Por qué:** `@ruta` mete el archivo directo en el contexto sin que Claude tenga que buscarlo. El error real vale más que tu descripción del error.
- **Cómo:** `@dags/ingesta/ventas.py` en el prompt; pegá el traceback de Composer tal cual; `Ctrl+V` para pegar un screenshot de Looker Studio; `cat error.log | claude -p "explicá este error"` desde la terminal.

### 7. Corregí temprano con `Esc`

- **Por qué:** si ves que va para otro lado, cada segundo que sigue es trabajo para tirar.
- **Cómo:** `Esc` frena en el momento y conserva lo hecho; escribís la corrección. `Esc Esc` (con el input vacío) o `/rewind` vuelven a un checkpoint anterior de código y/o conversación.

### 8. Para algo grande, que te entreviste primero

- **Por qué:** te hace las preguntas que no te hiciste (edge cases, backfill, idempotencia) antes de que haya código.
- **Cómo:** "Quiero migrar la ingesta de X a incremental. Entrevistame con AskUserQuestion sobre lo difícil y después escribí la spec en `SPEC.md`." Después `/clear` y otra sesión implementa leyendo la spec.

---

## Verificación

### 9. Dale a Claude una forma de verificar su trabajo

- **Por qué:** es lo que más mejora los resultados. Sin un criterio verificable, "terminé" significa "parece razonable", y vos sos el único test.
- **Cómo:** decí qué tiene que pasar: "`dbt build --select fct_ventas+ --target dev` en verde y el dry run debajo de 5 GB", "`uv run pytest tests/test_dag_integrity.py` pasa". Ponelo también en el `CLAUDE.md` como definición de terminado.

### 10. Test primero en bugs

- **Por qué:** un test que reproduce el bug prueba que entendiste el problema y que el fix lo arregla, no que "ya no tira error".
- **Cómo:** "escribí un test que falle con el input de anoche, mostrame que falla, después arreglalo y mostrame que pasa". En dbt: un test singular en `tests/` que hoy devuelve filas.

### 11. No confíes sin revisar el diff

- **Por qué:** la velocidad no es corrección. Un cambio plausible puede tocar algo fuera de alcance o romper un caso borde.
- **Cómo:** `/diff` o `git diff` antes de aceptar. Para revisión independiente: `/code-review` (corre en un subagent con contexto limpio) o el subagent [`revisor-dbt`](../ejemplos/agents/revisor-dbt.md). Checklist: skill [`revision-de-diffs`](../ejemplos/skills/revision-de-diffs/SKILL.md).

---

## CLAUDE.md

### 12. Corto, y solo lo que no se deduce del código

- **Por qué:** se carga en **todas** las sesiones. Si es largo, las reglas importantes se pierden en el ruido y Claude ignora la mitad.
- **Cómo:** por cada línea preguntate *"¿si la saco, Claude se equivoca?"*. Sí van: comandos de test/dry run, convenciones propias, gotchas (filtro de partición obligatorio). No van: obviedades, docs largas, descripciones archivo por archivo. Menos de 200 líneas. Arrancá con `/init`. Ejemplos en [`ejemplos/claude-md/`](../ejemplos/claude-md/README.md).

### 13. Procedimientos → skill; obligaciones → hook

- **Por qué:** una skill se carga solo cuando hace falta; un hook se ejecuta siempre, sin depender de que el modelo se acuerde.
- **Cómo:** "para crear un modelo seguí estos 8 pasos" → skill ([`dbt-nuevo-modelo`](../ejemplos/skills/dbt-nuevo-modelo/SKILL.md)). "Nunca corras `bq rm`" → `deny` + hook ([guardia de BigQuery](../ejemplos/hooks/README.md)). Reglas que aplican solo a ciertas carpetas → `.claude/rules/*.md` con `paths:`.

### 14. Tratá el `CLAUDE.md` como código

- **Por qué:** si Claude repite un error que el archivo ya prohíbe, la regla está mal escrita o perdida.
- **Cómo:** commitealo, revisalo cuando algo sale mal, podalo seguido. Si una regla sigue sin respetarse, marcala con "IMPORTANTE" (solo esa). Lo personal va en `CLAUDE.local.md` o `~/.claude/CLAUDE.md`.

---

## Delegación y subagents

### 15. Investigaciones largas → subagent

- **Por qué:** explorar lee muchos archivos. Un subagent lo hace en su propio context window y te devuelve solo la conclusión.
- **Cómo:** "usá un subagent para averiguar qué DAGs escriben en `raw.ventas` y con qué frecuencia". Si ya sabés dónde está la respuesta, resolvelo directo: delegar tiene overhead.

### 16. No delegues entendimiento

- **Por qué:** el subagent no ve tu conversación. "Arreglá el bug" sin contexto da resultados genéricos.
- **Cómo:** en el pedido (o en el `.md` del subagent) va qué se probó, qué se descartó, qué archivos importan y qué formato de respuesta querés.

### 17. Paralelizá lo independiente

- **Por qué:** tres investigaciones que no dependen entre sí no tienen por qué ir en fila.
- **Cómo:** "en paralelo, con subagents: (1) qué modelos leen `stg_pagos`, (2) qué DAG lo alimenta, (3) qué dashboards usan `fct_ventas`". Para trabajo de código en paralelo: worktrees (`claude -w nombre`). Ver [15 — Paralelismo y worktrees](../docs/15-paralelismo-y-worktrees.md).

---

## Permisos y seguridad

### 18. Allowlist para lo seguro, `deny` para lo irreversible

- **Por qué:** aprobar cada `dbt compile` cansa y terminás aprobando sin leer. Mejor que lo seguro pase solo y lo peligroso no pase nunca.
- **Cómo:** `.claude/settings.json` con `allow` (dry runs, `dbt compile`, `git diff`), `ask` (`dbt build`, `git push`) y `deny` (`bq rm`, leer `.env`). Ejemplo completo en [`ejemplos/settings/`](../ejemplos/settings/README.md). Ojo: se evalúa `deny` → `ask` → `allow` y gana la primera que matchea. `/fewer-permission-prompts` te sugiere una allowlist a partir de tu historial.

### 19. Las reglas en `CLAUDE.md` no son seguridad

- **Por qué:** el `CLAUDE.md` orienta lo que Claude intenta; los permisos y hooks los aplica Claude Code, no el modelo.
- **Cómo:** todo lo que no puede pasar nunca (borrar datos, tocar prod, leer secretos) va en `deny` o en un hook `PreToolUse`, no solo en prosa.

### 20. `bypassPermissions` solo en un contenedor

- **Por qué:** saltea todos los prompts, incluidas escrituras en `.git` y `.claude`. En tu máquina, con credenciales de GCP activas, es una mala apuesta.
- **Cómo:** para menos interrupciones usá `acceptEdits` (`Shift+Tab`) o modo `auto`. `--dangerously-skip-permissions` reservalo para una VM o contenedor descartable.

---

## Git

### 21. Siempre en una rama, commits chicos

- **Por qué:** los checkpoints de Claude solo cubren ediciones hechas con sus tools, no lo que cambia un comando de Bash. Git es tu red de seguridad real.
- **Cómo:** rama por tarea, commit después de cada paso que verificaste. Si algo sale mal, `git diff` / `git restore` además de `/rewind`.

### 22. Que Claude escriba el commit, vos lo aprobás

- **Por qué:** escribe buenos mensajes porque tiene todo el contexto del cambio; pero un `push` o un PR es visible para otros.
- **Cómo:** "commiteá con un mensaje que explique el porqué". `git commit` y `git push` en `ask`. Nunca `push --force` ni `reset --hard` sin que lo pidas vos. Ver [GIT.md](../GIT.md).

---

## Costos

### 23. Modelo y esfuerzo acordes a la tarea

- **Por qué:** el modelo más grande cuesta más por token y el razonamiento extendido se cobra como output.
- **Cómo:** default para el día a día; `/model opus` para arquitectura o debugging difícil; `model: haiku` en subagents mecánicos (listar, buscar, resumir). `/effort low` para tareas simples. Ver [04 — Modelos](../docs/04-modelos.md).

### 24. Preferí el CLI al MCP cuando alcanza

- **Por qué:** cada servidor MCP suma definiciones al contexto; `bq`, `gcloud` y `gh` no suman nada hasta que se usan.
- **Cómo:** MCP para lo que el CLI no da (lineage del manifest, catálogo, OAuth a un SaaS). Deshabilitá en `/mcp` los servers que no estás usando.

### 25. Mirá `/usage` y poné el contexto en la status line

- **Por qué:** lo que no se mide no se cuida. Una sesión abierta todo el día cobra toda la conversación en cada pregunta.
- **Cómo:** `/usage` (alias `/cost`) para la sesión; `/statusline` para ver modelo y % de contexto siempre. Detalle en [21 — Costos](../docs/21-costos.md).

---

## Ver también

- [Cheatsheet](../docs/cheatsheet.md) — comandos y atajos en una página.
- [20 — Flujos de trabajo](../docs/20-flujos-de-trabajo.md) — estas reglas aplicadas a tareas concretas.
- [Ejemplos copiables](../ejemplos/README.md) y [casos de uso](../casos-de-uso/README.md).
