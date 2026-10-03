# Skills: procedimientos que Claude carga solo cuando hacen falta

> **En 30 segundos:** una skill es una carpeta con un `SKILL.md` (frontmatter + instrucciones) que le enseña a Claude a hacer una tarea concreta. Claude ve siempre el nombre y la `description` de cada skill, pero el cuerpo se carga recién cuando la usás (vos con `/nombre` o Claude solo si la `description` matchea). Es la forma más barata de tener procedimientos largos sin inflar `CLAUDE.md`.

## Qué es y cómo funciona

Una skill es un procedimiento empaquetado: "cómo revisamos un modelo dbt", "cómo hacemos un backfill en Airflow", "cómo generamos el reporte de costos de BigQuery". Se crea una vez y después se invoca con `/nombre`, o Claude la usa solo cuando lo que pedís coincide con su `description`.

**Skills y slash commands son lo mismo.** Un archivo en `.claude/commands/deploy.md` y una skill en `.claude/skills/deploy/SKILL.md` crean el mismo `/deploy`. Los `commands/` viejos siguen andando, pero para cosas nuevas conviene la skill: admite archivos de soporte y más campos de frontmatter.

### Progressive disclosure: por qué una skill casi no cuesta contexto

La skill se carga en tres niveles:

| Nivel | Qué se carga | Cuándo |
|---|---|---|
| 1. Listado | `name` + `description` (+ `when_to_use`) | Siempre, en cada turno, para que Claude sepa que existe |
| 2. Cuerpo | Todo el `SKILL.md` | Cuando vos o Claude la invocan |
| 3. Archivos de soporte | `reference.md`, `scripts/`, ejemplos | Solo si el `SKILL.md` le indica a Claude que los lea o ejecute |

Consecuencia práctica: podés tener una referencia de 400 líneas sobre convenciones de BigQuery en un `reference.md` y no paga nada hasta que se usa. Lo que sí pagás siempre es la `description`, así que mantenela corta y precisa.

### Skill vs `CLAUDE.md` vs subagent vs hook

| Necesitás… | Usá |
|---|---|
| Un dato que Claude tiene que saber **siempre** en el repo (comandos de build, convenciones) | [`CLAUDE.md`](06-memoria.md) |
| Un procedimiento que se usa **a veces** ("cómo hacer X") | Skill |
| Que una tarea ruidosa corra **aislada** y vuelva solo el resumen | [Subagent](11-subagents.md) (o skill con `context: fork`) |
| Que algo pase **sí o sí**, sin depender de que el modelo se acuerde | [Hook](12-hooks.md) |

Regla práctica: si una sección de `CLAUDE.md` empezó a parecer un paso a paso, movela a una skill.

## Cómo se usa

### Dónde viven

| Ubicación | Ruta | Alcance |
|---|---|---|
| Personal | `~/.claude/skills/<nombre>/SKILL.md` | Todos tus proyectos en esta máquina |
| Proyecto | `.claude/skills/<nombre>/SKILL.md` | Este repo. Commitealo y la tiene todo el equipo |
| Plugin | `<plugin>/skills/<nombre>/SKILL.md` | Donde el [plugin](14-plugins.md) esté habilitado, como `/plugin:nombre` |
| Organización | `.claude/skills/` dentro del directorio de managed settings | Todos los usuarios donde la org lo despliegue |

Si el mismo nombre existe en varios lados, gana: organización > personal > proyecto. Las de plugin no chocan porque van con prefijo (`/mi-plugin:revisar`).

En monorepos, Claude Code también levanta `.claude/skills/` de directorios padres hasta la raíz del repo, y las de subcarpetas (`apps/x/.claude/skills/`) se cargan la primera vez que Claude toca un archivo ahí.

### Estructura de una skill

```text
.claude/skills/revisar-modelo-dbt/
├── SKILL.md            # obligatorio: frontmatter + instrucciones
├── checklist.md        # referencia larga, se lee solo si hace falta
└── scripts/
    └── bytes_estimados.sh   # se ejecuta, no se carga al contexto
```

Recomendación oficial: `SKILL.md` por debajo de 500 líneas; lo demás, a archivos de soporte referenciados desde el `SKILL.md` ("para el checklist completo, leé `[checklist.md](checklist.md)`").

### Frontmatter

Todos los campos son opcionales; `description` es el que importa. Los nombres de campo van en minúscula con guiones y tienen que estar escritos exacto: un campo mal escrito se ignora **sin error**.

| Campo | Para qué |
|---|---|
| `name` | Nombre del comando. Si no está, se usa el nombre de la carpeta |
| `description` | Qué hace y cuándo usarla. Claude decide con esto si la carga. Se trunca a 1.536 caracteres junto con `when_to_use`: lo importante, primero |
| `when_to_use` | Frases disparadoras o ejemplos de pedidos. Se suma a la `description` |
| `disable-model-invocation: true` | Solo vos la invocás con `/nombre`. Para cosas con efectos (deploy, backfill, mandar mensajes) |
| `user-invocable: false` | Solo Claude la usa; no aparece en el menú `/`. Para conocimiento de fondo |
| `allowed-tools` | Tools pre-aprobadas **durante el turno** en que se invoca (ej. `Bash(dbt compile *)`) |
| `disallowed-tools` | Tools que se sacan mientras la skill está activa |
| `argument-hint`, `arguments` | Pista de argumentos en el autocompletado y argumentos con nombre (`$modelo`) |
| `model`, `effort` | Modelo / nivel de esfuerzo mientras corre la skill |
| `context: fork` + `agent` | Correr la skill en un subagent aislado (`agent: Explore`, `Plan`, `general-purpose` o uno tuyo) |
| `paths` | Globs: Claude la carga automáticamente solo al trabajar con archivos que matchean |
| `hooks` | [Hooks](12-hooks.md) que se registran al invocar la skill |

Ojo si vas a subir la skill a claude.ai o a la Skills API: ahí solo se aceptan `name`, `description`, `license`, `compatibility`, `metadata` y `allowed-tools`, y cualquier otro campo da error al subir.

### Sustituciones útiles dentro del cuerpo

| Variable | Qué inserta |
|---|---|
| `$ARGUMENTS` | Todo lo que escribiste después de `/nombre` |
| `$0`, `$1`… | Argumentos por posición |
| `${CLAUDE_SKILL_DIR}` | La carpeta de la skill (para llamar a sus scripts sin depender del cwd) |
| `${CLAUDE_PROJECT_DIR}` | Raíz del proyecto |

Y la más potente: **inyección de contexto dinámico**. Una línea que empieza con `` !`comando` `` se ejecuta **antes** de que Claude lea la skill, y su salida reemplaza la línea. Así la skill llega con datos reales, no con "andá a buscar".

### Cómo se dispara

- **Vos:** `/revisar-modelo-dbt fct_ventas`.
- **Claude:** cuando tu pedido matchea la `description`. Para verificar qué ve, preguntale `What skills are available?` o abrí `/skills`.

## Ejemplo

Skill de proyecto para revisar un modelo dbt antes de abrir el PR:

```markdown
---
name: revisar-modelo-dbt
description: Revisa un modelo dbt (SQL + YAML) antes de abrir un PR - granularidad, joins que duplican filas, tests faltantes y bytes escaneados en BigQuery. Usar cuando el usuario pide revisar, validar o "dejar listo" un modelo en models/.
argument-hint: "[nombre_del_modelo]"
allowed-tools: Bash(dbt compile *) Bash(bq query --dry_run *) Bash(git diff *)
---

## Cambios actuales en models/

!`git diff HEAD -- models/`

## Qué hacer

1. Compilá el modelo: `dbt compile --select $0`.
2. Estimá bytes escaneados con `bq query --dry_run --use_legacy_sql=false` sobre el SQL compilado en `target/compiled/`.
3. Revisá con el checklist de [checklist.md](checklist.md): grano declarado, joins 1:N, `select *`, filtros de partición, `unique` + `not_null` sobre la PK.
4. Reportá: problemas bloqueantes primero (archivo:línea + qué pasaría en prod), después sugerencias.
```

Para una skill de revisión genérica ya armada, mirá [`ejemplos/skills/revision-de-diffs/SKILL.md`](../ejemplos/skills/revision-de-diffs/SKILL.md).

### Skill que corre aislada en un subagent

```markdown
---
name: investigar-dag
description: Investiga cómo funciona un DAG de Airflow y qué tablas toca
context: fork
agent: Explore
---

Investigá el DAG $ARGUMENTS:
1. Encontrá el archivo en dags/ y los operadores que usa.
2. Listá tablas de BigQuery que lee y escribe.
3. Devolvé un resumen con rutas de archivo concretas.
```

Con `context: fork` el subagent **no ve tu conversación** (ojo: no confundir con `/subtask`, el *fork* de [subagents](11-subagents.md), que sí la hereda): el cuerpo de la skill tiene que ser una tarea autocontenida. Si la skill son solo "lineamientos" sin tarea, el subagent vuelve sin nada útil.

## Evaluar e iterar una skill

Que una skill se dispare no significa que funcione. El método oficial es comparar contra una línea base:

1. Juntá 3–5 pedidos realistas (y 2–3 que **no** deberían dispararla).
2. Corré cada uno en una sesión **nueva** con la skill y otra vez con la skill apagada (`"skillOverrides": {"revisar-modelo-dbt": "off"}` en settings).
3. Compará: ¿se disparó cuando debía? ¿el resultado es mejor que sin skill?

Para automatizarlo existe el plugin **skill-creator**:

```text
/plugin install skill-creator@claude-plugins-official
```

Después pedile `evaluate my revisar-modelo-dbt skill with skill-creator`. Arma casos en `evals/evals.json`, corre cada caso en un subagent limpio, compara con y sin skill, hace A/B entre versiones y propone mejoras a la `description` midiendo cuándo se dispara y cuándo no. También sirve para crear skills nuevas desde cero.

## Trucos y errores comunes

- **La `description` es el 80% del trabajo.** Escribila con las palabras que usarías al pedirlo ("revisá el modelo", "validá el dbt") y con el caso de uso principal primero. Si no se dispara, el problema casi siempre está ahí.
- **Si se dispara de más:** hacé la `description` más específica o poné `disable-model-invocation: true`.
- **YAML roto = skill sin metadata.** La skill igual responde a `/nombre`, pero Claude nunca la elige sola. `claude plugin validate .claude/skills` encuentra frontmatter que no parsea; `claude --debug` muestra el error.
- **El `---` tiene que ser la primera línea** del archivo, o todo se toma como contenido.
- **El cuerpo queda en el contexto** el resto de la sesión y no se relee. Escribí instrucciones que valgan para toda la tarea ("corré los tests después de cada edición"), no pasos de una sola vez. Después de un `/compact` solo se conservan los primeros ~5.000 tokens de cada skill: lo crítico, arriba.
- **`allowed-tools` dura un turno** y no restringe nada: **pre-aprueba** esas tools, que corren sin pedirte permiso. Revisá el `allowed-tools` de skills de repos ajenos antes de correr Claude ahí, porque se aplica incluso en carpetas no confiadas.
- **Un comando `` !` `` que falla aborta toda la skill.** Si esperás exit code 1 (un check que encuentra problemas), agregale `|| true`.
- **Si una regla tiene que cumplirse siempre**, no la dejes en la skill: pasala a un [hook](12-hooks.md).
- **Demasiadas skills se comen el presupuesto del listado** (1% del context window). `/skill-doctor` te muestra cuánto cuesta cada una y cuáles nunca usaste; poné las de baja prioridad en `"name-only"` vía `skillOverrides`.
- **Las skills se recargan solas** al editarlas en `~/.claude/skills/` o `.claude/skills/`; si creaste la carpeta `skills/` después de arrancar la sesión, corré `/reload-skills`.
- **Skills incluidas:** Claude Code trae skills listas como `/code-review`, `/simplify`, `/batch`, `/loop`, `/debug` y `/run`/`/verify`. Si creás una skill con el mismo nombre, reemplaza a la incluida.

## Ver también

- [Subagents](11-subagents.md) — `context: fork` y el campo `skills` de un subagent.
- [Hooks](12-hooks.md) — para reglas que no pueden depender del modelo.
- [Plugins](14-plugins.md) — empaquetar y compartir skills con el equipo.
- [Memoria y `CLAUDE.md`](06-memoria.md) — qué va siempre cargado.
- [`ejemplos/skills/`](../ejemplos/skills/) — skills copiables.
- Documentación oficial: [Skills](https://code.claude.com/docs/en/skills) · [Agent Skills (estándar abierto)](https://agentskills.io).
