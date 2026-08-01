# Memoria: que no haya que reexplicar el proyecto cada vez

## `CLAUDE.md` de proyecto vs. memoria de usuario/global

El mecanismo principal y estándar de memoria en Claude Code es el archivo **`CLAUDE.md`**: un archivo Markdown que se carga automáticamente al arrancar una sesión en ese repo, con contexto que el agente debería tener siempre presente.

Existen distintos niveles:

- **`CLAUDE.md` de proyecto** (en la raíz del repo, versionado con git): contexto compartido por todo el equipo — arquitectura, comandos de build/test, convenciones del repo. Se genera/actualiza con `/init` (ver [Instalación](04-instalacion.md)) y se va editando a mano a medida que cambia el proyecto.
- **Memoria de usuario/global** (a nivel de la cuenta o la máquina, no del repo): preferencias personales de cómo trabajar, que aplican sin importar en qué proyecto se esté — por ejemplo, cómo preferís que se te comuniquen los resultados, o convenciones que usás siempre independientemente del repo.

La diferencia clave es el alcance: lo que es cierto para *todo el equipo en este repo* va en el `CLAUDE.md` del proyecto; lo que es una preferencia *tuya, en cualquier repo*, va en la configuración de usuario.

## Qué conviene guardar ahí y qué no

**Conviene guardar:**
- Comandos de build/test/lint específicos del proyecto (los que no son obvios mirando el `package.json`/`Makefile` a simple vista).
- Convenciones de estilo o arquitectura que no se infieren solo leyendo el código.
- Contexto de negocio necesario para tomar buenas decisiones (ej. "este servicio no puede tener downtime, cualquier cambio de schema necesita migración backward-compatible").
- Instrucciones de comportamiento que se repiten seguido y no son evidentes ("preferimos commits chicos", "nunca hacer `force push` a `main`").

**No conviene guardar:**
- Cualquier cosa que ya se puede derivar leyendo el código o la estructura del repo (duplica información y se desactualiza).
- Historial de cambios o decisiones puntuales de una tarea específica — eso vive en el historial de git, no en la memoria persistente.
- Contenido tan largo que nadie lo termina leyendo/manteniendo. Un `CLAUDE.md` de miles de líneas deja de cumplir su función.

Regla práctica compartida con [skills](08-skills.md): si es información que aplica *siempre*, va en `CLAUDE.md`; si es un procedimiento que aplica *a veces*, mejor una skill.

## Cómo se actualiza y cuándo revisarla

`CLAUDE.md` no se mantiene solo — hay que revisarlo cuando:

- El agente repite el mismo error o falta de contexto en varias sesiones seguidas (señal de que falta algo ahí).
- Cambia algo estructural del proyecto (nueva convención, nuevo comando de build, deprecación de algo viejo) y el archivo quedó desactualizado.
- Se nota que se está reexplicando lo mismo en el prompt de cada sesión nueva — eso es exactamente lo que `CLAUDE.md` debería estar absorbiendo.

Se puede editar a mano en cualquier momento, o pedirle al propio agente que proponga una actualización en base a lo que acaba de aprender sobre el proyecto en la sesión actual.

> **Nota:** algunos productos o entornos que corren sobre Claude Code pueden ofrecer, además de `CLAUDE.md`, sistemas de memoria persistente adicionales (por ejemplo, memoria estructurada por tipo de dato que persiste entre sesiones más allá del repo actual). Eso no es parte del comportamiento estándar de Claude Code en todos lados — si tu entorno lo tiene, conviene documentar acá cómo funciona específicamente, en vez de asumir que aplica igual en cualquier instalación.
