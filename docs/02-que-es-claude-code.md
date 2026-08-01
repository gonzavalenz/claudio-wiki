# Qué es Claude Code y dónde vive

Claude Code es el agente de Anthropic para trabajar con código: un LLM de la familia Claude, envuelto en un programa que le da acceso a herramientas (leer/escribir archivos, correr comandos de shell, buscar en el repo, usar `git`, navegar la web, etc.) y lo hace operar como agente siguiendo el [agentic loop](01-fundamentos.md).

No es un producto único con una sola interfaz: es la misma "capa de agente" disponible en varios lugares, según cómo quieras trabajar.

## Dónde se usa

- **CLI (terminal)**: `claude` corriendo directamente en la terminal, dentro de la carpeta del proyecto. Es la forma más flexible — funciona en cualquier repo, se puede scriptear, encadenar con otras herramientas, y correr en CI.
- **Extensiones de IDE**: integraciones para VS Code y JetBrains que muestran el agente dentro del editor, con acceso al contexto del archivo abierto y a los diffs propuestos directamente en la interfaz del IDE.
- **App de escritorio**: cliente nativo (Mac/Windows) para usar Claude Code sin depender de la terminal.
- **Web (claude.ai/code)**: versión web para trabajar con el agente desde el navegador, útil cuando no tenés el entorno local a mano.

Todas estas superficies comparten el mismo motor de agente — cambia la interfaz, no el comportamiento de fondo (herramientas, permisos, memoria, etc. funcionan igual conceptualmente).

## Relación con la Claude API

Claude Code se apoya en los modelos Claude expuestos por la **Claude API** (la API de Anthropic), pero no es simplemente "un cliente de la API": la API te da acceso al modelo crudo (le mandás mensajes, te devuelve texto o pedidos de `tool use`), mientras que Claude Code ya viene con:

- Un conjunto de herramientas ya implementadas y probadas (sistema de archivos, shell, búsqueda, git, web, etc.).
- El bucle agéntico ya armado (no hay que programarlo vos).
- Un sistema de permisos, memoria y configuración de proyecto listo para usar.

Si estás construyendo tu propio agente desde cero usando la API directamente, ver el [Claude Agent SDK](https://docs.anthropic.com) es el camino equivalente para no reimplementar el loop agéntico a mano. Claude Code, en cambio, es la herramienta ya terminada para usar día a día como asistente de desarrollo.

## Qué lo distingue de un asistente de autocompletado

Ver [Fundamentos](01-fundamentos.md#por-qué-claude-code-es-un-agente-y-no-un-autocompletado) para el detalle, pero en resumen: un autocompletado sugiere la próxima línea dentro de un archivo; Claude Code entiende una tarea completa, explora el proyecto, ejecuta acciones reales, y puede trabajar de forma semi-autónoma varios pasos seguidos antes de necesitar a alguien mirando.
