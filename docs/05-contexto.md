# Contexto: el recurso que más hay que cuidar

> **En 30 segundos:** el `context window` es todo lo que Claude "tiene en la cabeza" en una sesión: tu conversación, cada archivo que leyó, cada output de comando, `CLAUDE.md`, skills y el system prompt. Cuando se llena, rinde peor y cuesta más. Regla de oro: **una tarea por sesión**, `/clear` entre tareas, `/compact` con instrucciones cuando la tarea es larga, y `/context` para ver qué lo está ocupando.

## Qué ocupa el context window

| Se carga al arrancar | Se va sumando mientras trabaja |
|---|---|
| System prompt | Cada mensaje tuyo y cada respuesta |
| `CLAUDE.md` (usuario, proyecto, local) y rules sin `paths:` | Cada archivo que lee (el contenido completo, aunque en pantalla veas solo "Read") |
| Auto memory (`MEMORY.md`, primeras 200 líneas o 25 KB) | Cada output de comando (`dbt build`, `bq query`, logs...) |
| Nombres de tools MCP (los schemas se cargan bajo demanda) | Rules con `paths:` y `CLAUDE.md` de subcarpetas, cuando toca archivos que matchean |
| Descripciones de una línea de las skills | El cuerpo de una skill cuando se usa |
| Info del entorno y snapshot de git | Lo que agregan los hooks |

Lo que **no** ocupa tu contexto: el trabajo de un [subagent](11-subagents.md). Corre en su propio context window y solo te devuelve el resumen.

## Los comandos clave

| Comando | Qué hace | Cuándo |
|---|---|---|
| `/context` | Muestra el uso actual como grilla de colores, por categoría, con sugerencias. Lista qué `CLAUDE.md` y archivos de memoria se cargaron | Cuando sentís la sesión "pesada" o algo no carga |
| `/clear` | Conversación nueva, contexto vacío. La anterior queda guardada (se recupera con `/resume`) | **Al cambiar de tarea** |
| `/compact [instrucciones]` | Reemplaza el historial por un resumen estructurado | En una tarea larga, antes de que se llene |
| `/rewind` → *Summarize from here / up to here* | Resume solo una parte de la conversación | Para comprimir un tramo de debugging largo y conservar el resto |
| `/btw <pregunta>` | Pregunta al costado: responde con lo que ya sabe y **no se agrega al historial** | "¿Cómo se llamaba ese macro?" sin ensuciar el contexto |
| `/usage` | Costo de la sesión y uso del plan (`/cost` es alias) | Control de gasto |

### `/compact` con instrucciones

Claude Code compacta solo cuando se acerca al límite, pero decide él qué es importante. Si lo hacés vos, elegís qué sobrevive:

```text
/compact conservá la lista de modelos dbt modificados, los comandos de test que usamos y la decisión de usar merge en vez de insert_overwrite
```

También podés dejar en `CLAUDE.md` una sección de instrucciones de compactación:

```markdown
## Compact Instructions
Al compactar, conservá siempre la lista completa de archivos modificados y los comandos de test.
```

### Qué sobrevive a una compactación

| Se recupera | Se pierde (queda resumido) |
|---|---|
| `CLAUDE.md` de la raíz y rules sin `paths:` (se releen del disco) | Instrucciones que diste solo en el chat |
| Auto memory | Outputs completos de comandos y razonamiento intermedio |
| El plan escrito en plan mode | Rules con `paths:` y `CLAUDE.md` de subcarpetas (se recargan cuando vuelve a tocar esos archivos) |
| Hasta 5 archivos leídos/editados recientes | Detalle de lo que hayan inyectado los hooks |
| Skills invocadas (recortadas a 5.000 tokens c/u) | La lista de descripciones de skills |

Conclusión: **si una regla tiene que sobrevivir, va en `CLAUDE.md`, no en el chat.**

## Sesiones: retomar y bifurcar

Cada sesión se guarda localmente (en `~/.claude/projects/`) y queda atada a la carpeta.

```bash
claude --continue            # (-c) retoma la última conversación de esta carpeta
claude --resume              # (-r) selector de sesiones
claude --resume vista-ventas # retoma una sesión por nombre
claude -n vista-ventas       # arranca una sesión ya con nombre
```

Dentro de una sesión:

| Comando | Qué hace |
|---|---|
| `/rename vista-ventas` | Pone nombre a la sesión (para encontrarla después) |
| `/resume` | Cambia a otra conversación |
| `/branch [nombre]` | Copia la conversación hasta acá y te mueve a la copia; la original queda intacta |

En el selector de `/resume`: `Space` previsualiza, `Ctrl+R` renombra, `Ctrl+B` filtra por rama de git, `Ctrl+A` muestra todos los proyectos.

## Ejemplo: un día con dos tareas

```text
# Tarea 1: nuevo modelo incremental
/rename incremental-pedidos
... trabajo, tests, commit ...

# Cambio de tarea: no sigas en la misma conversación
/clear
/rename fix-dag-ventas
el DAG ingesta_ventas falló anoche con un 403 en el GCS sensor, revisá los logs en logs/ y decime la causa
```

Al día siguiente, `claude --resume incremental-pedidos` te devuelve a la primera tarea con todo su contexto.

## Señales de contexto degradado

- Repite errores que ya le corregiste o "se olvida" de una instrucción que diste hace rato.
- Le corregiste lo mismo **más de dos veces**.
- Mezcla detalles de una tarea anterior con la actual.
- Las respuestas se vuelven lentas y genéricas.
- `/context` o la status line muestran el contexto muy lleno.

Qué hacer: si la tarea sigue, `/compact` con instrucciones. Si está contaminada de intentos fallidos, `/clear` y un prompt nuevo mejor, que incluya lo que aprendiste. Una sesión limpia con buen prompt casi siempre le gana a una larga con correcciones acumuladas.

## Monitorear con la status line

La status line es una barra configurable debajo del prompt. La forma más rápida:

```text
/statusline mostrá el modelo y el porcentaje de contexto usado con una barra de progreso
```

O a mano, en `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

El script recibe un JSON por stdin con campos como `model.display_name` y `context_window.used_percentage` (requiere `jq` instalado).

## Trucos y errores comunes

- **Una tarea, una sesión.** La "sesión cajón de sastre" (empezás con un modelo, preguntás algo de Airflow, volvés al modelo) es el error más común.
- **Poné nombre antes de `/clear`** (`/rename` o `/clear nombre-de-la-anterior`) para encontrarla después en `/resume`.
- **Investigaciones grandes, a un subagent**: "usá subagents para investigar cómo se cargan las tablas raw de ventas". Los archivos que lea no ocupan tu contexto.
- **Acotá lo que pedís leer**. "Investigá el repo" sin límites puede leer cientos de archivos. Decí dónde mirar.
- **Cuidado con outputs gigantes**: un `bq query` sin `LIMIT` o un log completo de Airflow entran enteros al contexto. Pedí `head`, filtros o resúmenes.
- **`!comando` también ocupa contexto**: el comando que corrés con `!` y su output entran a la conversación.
- **Dos terminales con la misma sesión** mezclan los mensajes en un solo historial. Para probar otra idea, usá `/branch` o `claude --continue --fork-session`.
- **Más context window no es mejor contexto.** Aunque el modelo tenga 1M tokens, una sesión enfocada rinde más.

## Ver también

- [Memoria](06-memoria.md) — lo que tiene que sobrevivir entre sesiones
- [Plan mode y checkpoints](09-plan-mode-y-checkpoints.md) — `/rewind` y resumir partes de la conversación
- [Subagents](11-subagents.md) — investigar sin gastar tu contexto
- [Paralelismo y worktrees](15-paralelismo-y-worktrees.md) — varias sesiones a la vez
- [Costos](21-costos.md)
