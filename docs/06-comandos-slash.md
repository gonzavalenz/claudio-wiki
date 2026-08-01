# Comandos: los atajos con `/`

## Qué son

Los **slash commands** son atajos que invocan un procedimiento predefinido escribiendo `/nombre` en vez de escribir la instrucción completa en texto libre. Sirven para no reescribir (ni reexplicar) la misma tarea recurrente cada vez.

Algunos son built-in del propio Claude Code (control del entorno: sesión, configuración, ayuda); otros son [skills](08-skills.md) invocables por comando, y otros pueden ser comandos custom definidos por el usuario o el proyecto.

## Built-ins más comunes

- `/help` — ayuda sobre cómo usar Claude Code.
- `/init` — analiza el repo actual y genera (o sugiere mejoras a) un `CLAUDE.md`.
- `/login` — autenticación de la cuenta.
- `/fast` — activa el modo de salida más rápida (en modelos que lo soportan).

(La lista completa y actualizada de comandos built-in se consulta con `/help` dentro de una sesión — varía según versión.)

## Cómo crear slash commands propios

Un slash command custom es, en esencia, un prompt guardado con un nombre. Se define como un archivo Markdown en la carpeta de comandos del proyecto o del usuario, con las instrucciones que se quieren ejecutar cada vez que se invoca `/nombre-del-comando`. Puede tomar argumentos, referenciar archivos del proyecto, o encadenar instrucciones más largas de las que se querrían tipear a mano cada vez.

Es el mecanismo más simple de "empaquetar" una instrucción repetida — para algo más elaborado (con procedimientos de varios pasos, scripts asociados, o que necesita cargarse solo cuando aplica) conviene una [skill](08-skills.md) en vez de un comando simple.

## Buenas prácticas para nombrarlos y documentarlos

- **Nombre corto y sin ambigüedad**: el nombre del comando debería dejar claro qué hace sin necesitar leer la descripción (`/deploy`, `/code-review`, no `/hacer-cosas`).
- **Una responsabilidad por comando**: si un comando termina haciendo tres cosas distintas según el contexto, probablemente conviene dividirlo en comandos separados o convertirlo en una skill con lógica propia.
- **Evitar duplicar nombres con built-ins**: revisar que el nombre elegido no pise un comando ya existente.
- **Documentar el propósito donde el equipo lo vea**: si el comando es específico del proyecto, dejar una referencia en `CLAUDE.md` o en este mismo repo (ver [`ejemplos/slash-commands/`](../ejemplos/slash-commands/)) para que no dependa de la memoria de quien lo creó.
