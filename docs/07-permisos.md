# Permisos: cuánta autonomía le das

> **En 30 segundos:** dos capas. El **modo de permisos** (se cambia con `Shift+Tab`) define la base: qué hace sin preguntar. Las **reglas** `allow` / `ask` / `deny` en `settings.json` ajustan herramienta por herramienta. `deny` gana siempre. Los permisos los hace cumplir Claude Code, no el modelo: escribir "no hagas push" en `CLAUDE.md` es un pedido; una regla `deny` es una barrera.

## Modos de permisos

| Modo | Qué corre sin preguntar | Para qué |
|---|---|---|
| `default` (se muestra como **Manual**) | Solo lecturas | Revisar cada acción: código sensible, repo desconocido |
| `acceptEdits` | Lecturas, edición de archivos y comandos de filesystem comunes (`mkdir`, `touch`, `mv`, `cp`, `rm`, `sed`) dentro del proyecto | Iterar revisando los cambios después con `git diff` |
| `plan` | Lecturas y exploración. **No edita** tu código hasta que apruebes el plan | Explorar y planificar antes de tocar nada (ver [Plan mode](09-plan-mode-y-checkpoints.md)) |
| `auto` | Todo, pero un modelo clasificador revisa cada acción en segundo plano y bloquea lo riesgoso | Tareas largas, menos interrupciones |
| `dontAsk` | Solo lo pre-aprobado; todo lo que preguntaría, se rechaza | CI y scripts con allowlist exacta |
| `bypassPermissions` | Todo | **Solo** en contenedores o VMs aislados |

Desde la versión 2.1.283, las sesiones interactivas en terminal y VS Code **arrancan en `auto`** si tu cuenta y modelo lo soportan; si no, en Manual.

**Cambiar de modo:**

- `Shift+Tab` cicla: `auto` → `default` → `acceptEdits` → `plan` → `auto`. La barra de estado muestra el modo activo (`⏸ manual mode on`, `⏵⏵ accept edits on`, `⏸ plan mode on`, `⏵⏵ auto mode on`).
- Al lanzar: `claude --permission-mode plan`.
- Fijar tu propio modo por defecto en settings (ejemplo): `"permissions": { "defaultMode": "acceptEdits" }`.

> `auto` reduce interrupciones pero **no garantiza seguridad**. Usalo cuando confiás en la dirección general de la tarea, no como reemplazo de revisar operaciones sensibles.

## Qué pide aprobación (en Manual)

| Tipo | Pregunta | "Sí, y no preguntar de nuevo" |
|---|---|---|
| Lecturas, `grep`, búsqueda | No (dentro del proyecto) | — |
| Comandos Bash | Sí, salvo un set de solo lectura (`ls`, `cat`, `head`, `grep`, `wc`, `git status`...) | Permanente para ese comando en el repo |
| Editar archivos | Sí | Hasta que termine la sesión |
| WebFetch | Sí, salvo dominios de documentación pre-aprobados | Permanente para ese dominio |

Las aprobaciones permanentes se guardan en `.claude/settings.local.json` en la raíz del repo.

## Reglas: `allow`, `ask`, `deny`

Formato: `Herramienta` o `Herramienta(especificador)`.

```json
{
  "permissions": {
    "allow": [
      "Bash(dbt compile *)",
      "Bash(dbt build --select *)",
      "Bash(dbt test *)",
      "Bash(sqlfluff lint *)",
      "Bash(uv run pytest *)",
      "Bash(bq show *)",
      "Bash(bq ls *)"
    ],
    "ask": [
      "Bash(bq query *)",
      "Bash(git push *)"
    ],
    "deny": [
      "Bash(bq rm *)",
      "Read(./.env)",
      "Read(./secrets/**)"
    ]
  }
}
```

**Orden de evaluación: `deny` → `ask` → `allow`.** Gana la primera que matchea, sin importar cuál es más específica. Por eso `ask: Bash(bq query *)` pregunta también en `bq query --dry_run ...` aunque haya un `allow` más específico.

### Sintaxis que hay que conocer

| Regla | Matchea |
|---|---|
| `Bash` | Todos los comandos (como `deny`, saca la tool por completo) |
| `Bash(dbt test)` | Exactamente `dbt test` |
| `Bash(dbt test *)` | `dbt test`, `dbt test --select x`... |
| `Bash(git log *)` vs. `Bash(git *)` | Solo `git log` vs. **cualquier** comando git |
| `Bash(ls *)` vs. `Bash(ls*)` | `ls -la` pero no `lsof` vs. ambos (el espacio cuenta) |
| `Read(./.env)` | Leer `.env` en la carpeta actual |
| `Edit(/models/**)` | Editar dentro de `models/` (relativo a la raíz del proyecto en settings de proyecto) |
| `Read(//Users/vos/claves/**)` | Ruta absoluta (doble barra) |
| `Read(~/.ssh/**)` | Ruta desde tu home |
| `WebFetch(domain:docs.getdbt.com)` | Fetch a ese dominio |
| `mcp__bigquery__*` | Todas las tools del servidor MCP `bigquery` |

Claude Code entiende operadores de shell: `Bash(dbt test *)` **no** aprueba `dbt test && rm -rf target/`. Cada subcomando tiene que matchear por su cuenta.

### `/permissions`

Abre un diálogo para ver, agregar y quitar reglas, indicando de qué archivo viene cada una. Funciona incluso mientras Claude está trabajando.

## Dónde van los settings (jerarquía)

| Prioridad | Archivo | Para qué | ¿Va a git? |
|---|---|---|---|
| 1 (máxima) | Managed settings (los despliega IT) | Políticas de la organización. No se pueden pisar | — |
| 2 | Flags de línea de comando | Una sola sesión | — |
| 3 | `.claude/settings.local.json` | Tus ajustes en este repo | No (va al `.gitignore`) |
| 4 | `.claude/settings.json` | Reglas compartidas del equipo | Sí |
| 5 | `~/.claude/settings.json` | Tus preferencias en todos los repos | — |

Dos matices clave:

- **Las listas se combinan**, no se pisan: los `allow` de usuario y de proyecto se suman.
- **Un `deny` en cualquier nivel no lo destraba ningún `allow`** de otro nivel.

Las reglas `allow` de un `.claude/settings.json` de proyecto solo se aplican después de que aceptás el diálogo de confianza del repo.

## Sandbox

El sandbox es un límite que impone el sistema operativo sobre los comandos de shell que corre Claude: qué carpetas puede escribir y a qué dominios de red puede salir. Funciona en macOS, Linux y WSL2 (no en Windows nativo). Está apagado por defecto.

```text
/sandbox
```

O en settings: `"sandbox": { "enabled": true }`. En el modo *auto-allow*, los comandos que corren dentro del sandbox no piden aprobación; los `deny` y los `ask` con comando específico (como `Bash(git push *)`) se siguen respetando.

Permisos y sandbox se complementan: los permisos deciden qué tools puede usar; el sandbox limita lo que un comando puede alcanzar aunque se haya colado algo (por ejemplo, un prompt injection en un archivo que leyó).

## Ejemplo: configuraciones por situación

| Situación | Configuración |
|---|---|
| Repo nuevo o crítico, querés ver todo | `claude --permission-mode default` |
| Refactor de modelos dbt que vas a revisar con `git diff` | `acceptEdits` + allowlist de `dbt` y `sqlfluff` |
| Tarea larga y conocida, pocas interrupciones | `auto` |
| Explorar un repo de ingestas heredado | `claude --permission-mode plan` |
| Job de CI que solo corre tests | `claude -p "corré los tests" --permission-mode dontAsk --allowedTools "Bash(uv run pytest *)" "Read"` |
| Ejecución desatendida | `--dangerously-skip-permissions` **solo** dentro de un contenedor |

## Trucos y errores comunes

- **Poné el `*` después del subcomando.** `Bash(git log *)` limita a `git log`; `Bash(git *)` habilita cualquier git, incluido `push`.
- **Las reglas de Bash no son una barrera infalible.** `deny: Bash(git push *)` no matchea `git -C . push`. Para restricciones que tienen que cumplirse sí o sí, combiná con sandbox o un [hook](12-hooks.md) `PreToolUse`.
- **Un archivo `.claudeignore` no tiene efecto**: para que no lea secretos, usá `deny` con `Read(...)`.
- **Una barra no es ruta absoluta**: `Read(/secrets/**)` en settings de usuario apunta a `~/.claude/secrets/**`. Para absoluta, `//`.
- **`/fewer-permission-prompts`** escanea tus sesiones y propone una allowlist de comandos de solo lectura para `.claude/settings.json`. Muy útil después de la primera semana.
- **Los checkpoints no deshacen efectos remotos**: un `bq rm`, un `DELETE` en BigQuery o un deploy no se revierten con `/rewind`. Eso se controla con permisos, no con checkpoints.
- **Confirmá siempre** lo destructivo o visible para otros: `git push --force`, `reset --hard`, borrar tablas, crear PRs, mandar mensajes. El costo de confirmar es bajo; el de un error, alto.
- **Ampliá la autonomía de a poco**: empezá restrictivo en un repo nuevo y abrí a medida que conocés cómo trabaja.

## Ver también

- [Plan mode y checkpoints](09-plan-mode-y-checkpoints.md)
- [Hooks](12-hooks.md) — bloquear acciones con lógica propia
- [Automatización](16-automatizacion.md) — permisos en `claude -p` y CI
- [Paralelismo y worktrees](15-paralelismo-y-worktrees.md)
