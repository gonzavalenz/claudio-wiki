# Memory

> verificado: 2026-10-18 · fuentes: [Memory (Claude Code)](https://code.claude.com/docs/en/memory), [agents.md](https://agents.md/), [Copilot custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions), [Antigravity rules](https://antigravity.google/docs/rules)

Son archivos Markdown que el agent carga al iniciar cada sesión, así no tenés que repetir convenciones, comandos y reglas. Son **contexto que el modelo intenta seguir**, no configuración que se haga cumplir.

## Cuándo usarla y cuándo no

| Contenido | Dónde va |
|---|---|
| Build, test, layout del repo, convenciones: lo que importa en *todas* las sesiones | memory |
| Procedimiento de varios pasos | [skill](skills.md) |
| Regla para una sola parte del código | regla con alcance por path |
| Algo que se tiene que cumplir sí o sí | [hook](hooks.md) o [permisos](tools-and-permissions.md) |

Cuándo agregar algo a memory:
- El agent repite el mismo error.
- Corregís lo mismo en sesiones distintas.
- Una persona nueva en el proyecto necesitaría ese mismo dato.

## Cómo funciona

- **Jerarquía de alcances**: organización → usuario → proyecto → subdirectorio. Los archivos se **concatenan**; ninguno reemplaza a otro. Si dos instrucciones chocan, el modelo puede seguir cualquiera de las dos.
- **`AGENTS.md`** es el formato abierto para estas instrucciones: Markdown sin campos obligatorios. Lo leen Claude Code, Copilot, Antigravity, Codex, Cursor y otros. Si hay varios, gana el más cercano al archivo que se está editando.
- **Auto memory**: el propio agent escribe notas para sesiones futuras.

## En Claude Code

| Alcance | Archivo |
|---|---|
| Usuario | `~/.claude/CLAUDE.md` |
| Proyecto | `./CLAUDE.md` o `./.claude/CLAUDE.md` |
| Local (no versionado) | `./CLAUDE.local.md` |
| Por path | `.claude/rules/*.md` con frontmatter `paths:` (globs) |

- **Orden de carga**:
  - Se cargan los archivos del cwd y de todos los directorios padres, de la raíz hacia abajo, así que el más cercano se lee último.
  - Los de subdirectorios se cargan recién cuando se toca un archivo ahí.
- **Imports**:
  - Con `@ruta`, hasta 4 niveles.
  - Lo importado también se carga al inicio, así que no ahorra contexto.
- **`AGENTS.md`**:
  - Se lee nativamente (v2.1.277+), pero **solo si no hay** `CLAUDE.md`, `.claude/CLAUDE.md` ni `CLAUDE.local.md` en el cwd o más arriba. `~/.claude/CLAUDE.md` no cuenta.
  - Si hay ambos, usá `@AGENTS.md` dentro de `CLAUDE.md` (no lo duplica).
  - Otra opción: cambiar el comportamiento en `/config` → *Project instructions*.
- **Tamaño**: menos de 200 líneas por archivo.
- **Auto memory** (activada por default):
  - Vive en `~/.claude/projects/<proyecto>/memory/`, con un índice en `MEMORY.md` (se cargan sus primeras 200 líneas o 25 KB, lo que ocurra primero).
  - Es solo de esa máquina.
  - Se maneja con `/memory`.
- **Comandos**:
  - `/init` genera `CLAUDE.md` y además migra `.cursorrules` y `copilot-instructions.md`.
  - `/memory` lista y edita los archivos.
  - `/context` muestra qué se cargó.
- **Después de `/compact`**: ver [context](context.md#en-claude-code).

## En otras herramientas

- **Copilot**:
  - `.github/copilot-instructions.md`, más `.github/instructions/*.instructions.md` con `applyTo:` para alcance por path.
  - También lee `AGENTS.md`.
  - `no probado`
- **Antigravity**:
  - `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md` (con `trigger:` obligatorio; sin él, la regla se descarta).
  - `no probado`

Para un repo que usan varias herramientas: un solo `AGENTS.md` como fuente, y `CLAUDE.md` con `@AGENTS.md`.

## Errores comunes

- **Agregar un `CLAUDE.md` o un `CLAUDE.local.md` a un repo que dependía de `AGENTS.md`**: Claude deja de leer `AGENTS.md`.
- **Escribir "leé AGENTS.md" en vez de `@AGENTS.md`**: solo lo lee si decide abrirlo.
- **Archivos largos o contradictorios**: las reglas se diluyen.
- **Reglas de seguridad en memory**: se pueden ignorar.

## Ver también

[context](context.md) · [skills](skills.md) · [hooks](hooks.md)
