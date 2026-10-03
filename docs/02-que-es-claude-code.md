# Qué es Claude Code y dónde vive

> **En 30 segundos:** Claude Code es el agente de Anthropic para trabajar con código (y con cualquier cosa que se haga desde una terminal). Es un solo motor disponible en varias superficies: CLI, app de escritorio, VS Code, JetBrains, web y móvil. Cambia la interfaz, no el comportamiento: tu `CLAUDE.md`, tus settings y tus servidores MCP valen en todas las superficies locales.

## Qué es

Un modelo Claude + un harness que le da `tools` y maneja el contexto (ver [Fundamentos](01-fundamentos.md)). No sirve solo para programar: también para escribir documentación, investigar un repo, correr builds, analizar logs o armar queries.

## Dónde se usa

| Superficie | Ideal para | Qué tiene |
|---|---|---|
| **CLI** (`claude`) | Trabajo en terminal, scripts, servidores remotos | El set completo de features. Es la única con modo no interactivo (`claude -p`) y Agent SDK |
| **Desktop** (Mac, Windows, Linux) | Revisión visual, varias sesiones en paralelo | Visor de diffs, preview de la app, sesiones paralelas |
| **VS Code / Cursor** | Trabajar sin salir del editor | Diffs inline, `@`-menciones, revisión del plan |
| **JetBrains** (PyCharm, IntelliJ...) | Trabajar dentro de un IDE JetBrains | Corre el CLI en la terminal del IDE + visor de diffs |
| **Web** ([claude.ai/code](https://claude.ai/code)) | Tareas largas que no necesitan mucha supervisión | Corre en la nube, sigue aunque cierres la compu |
| **Móvil** (app de Claude) | Lanzar y monitorear tareas desde el celular | Sesiones en la nube y Remote Control de sesiones locales |

Podés mezclar superficies en el mismo proyecto.

## Dónde corre el código

| Entorno | Dónde se ejecuta | Para qué |
|---|---|---|
| **Local** | Tu máquina | Lo normal. Acceso a tus archivos, credenciales y herramientas (`gcloud`, `bq`, `dbt`) |
| **Cloud** | VMs de Anthropic (o entornos self-hosted de tu organización) | Delegar tareas, trabajar sobre repos que no tenés clonados |
| **Remote Control** | Tu máquina, manejada desde el navegador o el celular | Seguir una sesión local desde otro dispositivo |

> Para el stack de datos, lo habitual es **local**: ahí están tus credenciales de GCP y tu perfil de dbt. Una sesión cloud no tiene acceso a tu `gcloud auth` local.

## Relación con la Claude API y el Agent SDK

- La **Claude API** te da el modelo "crudo": le mandás mensajes, te devuelve texto o pedidos de `tool use`. El loop, las tools y los permisos los programás vos.
- **Claude Code** trae todo eso resuelto: tools probadas, `agentic loop`, permisos, memoria, sesiones.
- El **[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)** expone el mismo harness de Claude Code como librería (Python/TypeScript), para armar tus propios agentes sin reimplementar el loop.

Regla rápida: para trabajar vos día a día, Claude Code. Para meter un agente dentro de un producto o pipeline propio, Agent SDK (ver [Automatización](16-automatizacion.md)).

## Cómo se extiende

| Pieza | Qué es | Cuándo se carga | Capítulo |
|---|---|---|---|
| `CLAUDE.md` | Instrucciones persistentes del proyecto | Siempre, al arrancar | [Memoria](06-memoria.md) |
| `skills` | Procedimientos empaquetados, invocables con `/nombre` | Bajo demanda | [Skills](10-skills.md) |
| `subagents` | Agentes con su propio context window | Cuando se delega | [Subagents](11-subagents.md) |
| `hooks` | Comandos que corren en eventos fijos (antes/después de una tool...) | Siempre, de forma determinística | [Hooks](12-hooks.md) |
| `MCP` | Conexión a servicios externos (BigQuery, Jira, Slack...) | Nombres al inicio, schemas bajo demanda | [MCP](13-mcp.md) |
| `plugins` | Paquetes que agrupan todo lo anterior | Al instalarlos | [Plugins](14-plugins.md) |

## Ejemplo: qué superficie usar para qué

- Refactor de un DAG de Airflow con tests locales → **CLI** o **VS Code**, en local.
- Revisar con calma un diff grande de modelos dbt → **Desktop** o **VS Code** (visor de diffs).
- "Investigá por qué este repo viejo de ingestas usa dos versiones de pandas" y dejarlo corriendo → **Web**.
- Chequear desde el celular si terminó la sesión que dejaste corriendo → **Remote Control** o app móvil.

## Trucos y errores comunes

- **La extensión de VS Code trae su propio CLI** para el panel de chat. Para correr `claude` en la terminal integrada igual necesitás instalar el CLI.
- **El plugin de JetBrains no trae CLI**: corre `claude` en la terminal del IDE. Si no está en el `PATH`, muestra "Cannot launch Claude Code".
- **Las sesiones son por superficie**: Desktop, web y VS Code tienen cada una su lista de sesiones (Desktop puede retomar una sesión del CLI).
- **No es un autocompletado**: no sugiere la línea siguiente, resuelve tareas completas de varios pasos.

## Ver también

- [Fundamentos](01-fundamentos.md)
- [Instalación y primeros pasos](03-instalacion.md)
- [Arquitecturas de integración](18-arquitecturas-de-integracion.md)
