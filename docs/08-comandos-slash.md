# Slash commands y atajos: `/`, `!`, `@` y el teclado

> **En 30 segundos:** escribí `/` para ver todos los `slash commands` disponibles (built-in, skills, plugins y MCP). Los custom commands ahora **son skills**: un archivo en `.claude/commands/x.md` o `.claude/skills/x/SKILL.md` crea `/x`. Y hay cinco atajos que conviene tener en los dedos: `Shift+Tab` (modo), `Esc` (frenar), `Esc Esc` (rewind), `!` (shell) y `@` (archivos).

## Built-ins más útiles

Un comando solo se reconoce al **principio** del mensaje; lo que sigue son sus argumentos.

### Sesión y contexto

| Comando | Para qué |
|---|---|
| `/clear [nombre]` | Conversación nueva con contexto vacío. La anterior se recupera con `/resume` |
| `/compact [instrucciones]` | Resume la conversación para liberar contexto |
| `/context` | Qué está ocupando el context window |
| `/resume [sesión]` | Volver a otra conversación (por nombre, ID o con selector) |
| `/rename <nombre>` | Nombrar la sesión actual |
| `/branch [nombre]` | Bifurcar la conversación para probar otro camino |
| `/rewind` | Volver código y/o conversación a un checkpoint (alias `/undo`, `/checkpoint`) |
| `/btw <pregunta>` | Pregunta al costado, no entra al historial |
| `/export [archivo]` | Exportar la conversación como texto |

### Modelo y modo

| Comando | Para qué |
|---|---|
| `/model [modelo]` | Cambiar modelo (y esfuerzo, con flechas) |
| `/effort [nivel]` | Cambiar el esfuerzo de razonamiento |
| `/fast` | Fast mode de Opus |
| `/plan [tarea]` | Entrar en plan mode, opcionalmente arrancando con una tarea |
| `/permissions` | Ver y editar reglas allow/ask/deny |
| `/sandbox` | Activar el sandbox de Bash |

### Configuración del proyecto

| Comando | Para qué |
|---|---|
| `/init` | Generar o mejorar el `CLAUDE.md` |
| `/memory` | Editar `CLAUDE.md` y gestionar la auto memory |
| `/config` | Panel de settings (tema, modelo, editor vim, etc.) |
| `/mcp` | Gestionar servidores MCP y su autenticación |
| `/skills` | Listar skills (con `t` ordena por tokens) |
| `/hooks` | Ver la configuración de hooks |
| `/plugin` | Instalar y gestionar plugins |
| `/statusline [descripción]` | Configurar la status line |
| `/add-dir <ruta>` | Dar acceso a otra carpeta en esta sesión |

### Revisar y diagnosticar

| Comando | Para qué |
|---|---|
| `/diff` | Ver los cambios del working tree, incluidos los de Claude |
| `/code-review` (alias `/review`) | Revisar el diff (o un PR) buscando bugs; `--fix` aplica los hallazgos |
| `/security-review` | Revisar el diff de la rama buscando vulnerabilidades |
| `/simplify` | Revisar el código cambiado y simplificarlo |
| `/usage` | Costo de la sesión y uso del plan (`/cost`, `/stats` son alias) |
| `/status` | Versión, modelo, cuenta, conectividad |
| `/doctor` | Diagnóstico de instalación y configuración |
| `/help` | Ayuda y lista de comandos |

### Trabajo en paralelo y automatización

| Comando | Para qué |
|---|---|
| `/tasks` | Ver trabajo en segundo plano (comandos y subagents) |
| `/loop [intervalo] [prompt]` | Repetir un prompt mientras la sesión está abierta |
| `/schedule` | Crear rutinas que corren en la nube con un cron |
| `/batch <instrucción>` | Cambios grandes partidos en unidades que corren en worktrees separados |

La lista completa depende de tu versión, plan y plataforma: `/` en la sesión es la fuente de verdad.

## Custom commands = skills

Los custom commands se **unificaron con las skills**. Las dos formas crean `/deploy` y funcionan igual:

| Formato | Ruta | Comentario |
|---|---|---|
| Command (formato viejo, sigue andando) | `.claude/commands/deploy.md` | Un solo archivo |
| Skill (recomendado) | `.claude/skills/deploy/SKILL.md` | Carpeta con archivos de soporte; Claude la puede usar sola si es relevante |

Van en `.claude/` del proyecto (compartidos vía git) o en `~/.claude/` (personales). Si hay una skill y un command con el mismo nombre, gana la skill. Un archivo en `.claude/commands/dbt/nuevo.md` se invoca como `/dbt:nuevo`.

Ejemplo, `.claude/commands/revisar-modelo.md`:

```markdown
---
description: Revisa un modelo dbt contra las convenciones del repo
argument-hint: [nombre-del-modelo]
---

Revisá el modelo $ARGUMENTS:

1. Que respete las convenciones de nombres del CLAUDE.md.
2. Que la PK tenga tests unique y not_null en su schema.yml.
3. Corré `dbt build --select $ARGUMENTS` y reportá el resultado.

No edites nada: solo listá problemas y sugerencias.
```

Uso: `/revisar-modelo fct_pedidos`. `$ARGUMENTS` es todo lo que pasaste; `$0`, `$1`... son argumentos individuales. Para todo lo demás (frontmatter, cuándo Claude la invoca sola, archivos de soporte) ver [Skills](10-skills.md).

## Atajos de teclado clave

| Atajo | Qué hace |
|---|---|
| `Shift+Tab` | Cambia el modo de permisos: auto → manual → accept edits → plan |
| `Esc` | Frena a Claude en el acto. Conserva lo hecho; podés redirigir |
| `Esc` `Esc` | Con el input vacío: abre el menú de rewind. Con texto: borra el borrador (se recupera con `↑`) |
| `Ctrl+C` | Interrumpe; con nada corriendo, borra el input; dos veces, sale |
| `Ctrl+R` | Búsqueda inversa en el historial de prompts |
| `↑` / `↓` | Historial de prompts |
| `Ctrl+G` | Editar el prompt (o el plan) en tu editor de texto |
| `Ctrl+V` (`Cmd+V` en iTerm2) | Pegar una imagen del portapapeles (captura de un dashboard, un error) |
| `Ctrl+B` | Mandar a segundo plano un comando o agente que está corriendo |
| `Ctrl+O` | Ver el transcript detallado (cada tool call) |
| `Ctrl+T` | Mostrar/ocultar la lista de tareas de Claude |
| `Ctrl+S` | Guardar el borrador a un costado y volver a traerlo |
| `Option+P` / `Alt+P` | Cambiar de modelo |
| `Option+T` / `Alt+T` | Activar/desactivar extended thinking |
| `\` + `Enter` / `Shift+Enter` / `Ctrl+J` | Nueva línea en el prompt |
| `?` (input vacío) | Panel de atajos |

### Prefijos del prompt

| Prefijo | Qué hace | Ejemplo |
|---|---|---|
| `/` | Comando o skill | `/compact` |
| `!` | Modo shell: corre el comando directo, sin pasar por Claude. Comando y output entran al contexto y Claude responde | `! dbt test --select stg_pedidos` |
| `@` | Mencionar un archivo con autocompletado | `explicá @models/marts/fct_pedidos.sql` |

Mientras Claude trabaja, podés **escribir una corrección y apretar `Enter`**: queda en cola y la lee entre tool calls, sin necesidad de frenarlo.

## Trucos y errores comunes

- **Tab completa** comandos y rutas; también podés escribir `/` en el medio de un prompt para completar un comando.
- **`!` es ideal para darle contexto real**: `! bq show --schema analytics.fct_pedidos` le pasa el schema sin que tenga que pedirlo. Ojo: todo el output entra al contexto.
- **Imágenes**: pegá una captura del dashboard de Looker Studio con `Ctrl+V` y preguntá "¿por qué este gráfico muestra un salto el 3/9?".
- **Nombres de comandos**: cortos, una responsabilidad por comando, sin pisar built-ins. Si un comando empieza a necesitar varios pasos y archivos de soporte, pasalo a skill.
- **Comandos removidos** que todavía aparecen en guías viejas: `/vim` (ahora en `/config` → Editor mode), `/pr-comments` (pedíselo directo a Claude), `/ultraplan` (usá plan mode).
- **`/agents`** ya no abre un editor interactivo: pedile a Claude que cree el subagent o editá `.claude/agents/` (ver [Subagents](11-subagents.md)).

## Ver también

- [Skills](10-skills.md) — cómo armar tus propios comandos
- [Contexto](05-contexto.md) — `/clear`, `/compact`, `/context`, `/resume`
- [Plan mode y checkpoints](09-plan-mode-y-checkpoints.md) — `Esc`, `/rewind`, `/plan`
- [Cheatsheet](cheatsheet.md)
