# Cómo sumar contenido

Este repo crece de forma incremental. Antes de agregar o editar contenido, tené en cuenta estas convenciones.

## Idioma

- El texto explicativo va en **español**.
- Los términos técnicos propios de Claude Code se dejan **en inglés, sin traducir**: `skills`, `hooks`, `subagents`, `slash commands`, `MCP`, `agentic loop`, `context window`, etc. No se inventan traducciones (ej: no decir "habilidades" por `skills`, no decir "ganchos" por `hooks`).
- Esto aplica también a nombres de carpetas/archivos cuando refieren a un concepto propio de Claude Code (ej: `ejemplos/skills/`, no `ejemplos/habilidades/`).

## Dónde va cada cosa

- **`docs/`** — contenido conceptual, explicativo. Un capítulo = una idea/tema. Si un capítulo crece mucho, se puede partir en sub-secciones dentro del mismo archivo (con `##`) antes de pensar en dividir el archivo.
- **`buenas-practicas/`** — reglas accionables ("hacé esto", "evitá esto"), no teoría. Cada regla debería poder justificarse con un motivo concreto (una experiencia, un problema real que evita).
- **`casos-de-uso/`** — un caso de uso = un escenario real resuelto de punta a punta: contexto, problema, cómo se resolvió con Claude Code, qué se aprendió. No son teoría, son ejemplos vividos o simulados con detalle suficiente para reproducirlos.
- **`ejemplos/`** — artefactos reutilizables y copiables: `CLAUDE.md` de ejemplo, configuraciones de `hooks`, `skills`, `slash commands`, snippets de `settings.json`, etc. Código/config primero, explicación mínima al lado.
- **`assets/`** — material de referencia que no es Markdown versionable como contenido (HTML standalone, imágenes, diagramas exportados).
- **`context/`** — contexto personal (stack tecnológico de laburo y personal), para orientar ejemplos y casos de uso hacia herramientas concretas en vez de genéricas.

## Formato

- Markdown estándar, encabezados en sentence case.
- Bloques de código con el lenguaje indicado (` ```bash `, ` ```json `, etc.) para que se vea resaltado.
- Preferir ejemplos concretos por sobre descripciones abstractas.
- Enlazar entre documentos relacionados (ej: un caso de uso que use `skills` linkea a `docs/08-skills.md`).

## Plantilla de capítulo (`docs/`)

Cada capítulo sigue la misma forma para que se pueda escanear rápido:

```markdown
# Título

> **En 30 segundos:** 2–3 líneas con la idea central.

## Qué es / cómo funciona
## Cómo se usa              (comandos, rutas, config copiable)
## Ejemplo                  (con el stack de context/stack.md)
## Trucos y errores comunes (los matices no obvios)
## Ver también              (links a otros capítulos y ejemplos)
```

- **Verificar antes de escribir**: comandos, flags, rutas y campos de config se chequean contra la [documentación oficial](https://code.claude.com/docs/en/claude_code_docs_map.md). Lo que no se pudo verificar, no se publica.
- Los capítulos están numerados por orden de lectura y agrupados en 5 partes (ver índice en el [README](README.md)). Si se agrega uno, se actualiza el índice del README y la guía visual de `assets/`.

## Estado de los documentos

Mientras un archivo esté incompleto, se puede marcar arriba del todo con:

```markdown
> 🚧 Borrador — falta completar.
```

y sacar la marca cuando el contenido esté conforme.
