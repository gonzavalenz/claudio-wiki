---
name: delegar-a-gemini
description: Delega una tarea chica y de solo lectura a Gemini (vía Antigravity CLI, `agy -p`) y trae el resultado a la sesión. Usar para segundas opiniones, revisiones de consistencia de términos/links, resúmenes de archivos, borradores cortos o búsquedas puntuales cuando el usuario pide "pasáselo a Gemini", "pedile a Gemini", "segunda opinión de Gemini" o cuando conviene una revisión independiente de un modelo distinto.
---

# Delegar a Gemini

Gemini corre como agente secundario mediante Antigravity CLI en modo headless y **solo lectura** (`--mode plan`): puede leer el repo pero no edita archivos. Claude Code sigue siendo quien decide y aplica cambios (ver `AGENTS.md`).

## Cuándo usarla

- Segunda opinión independiente sobre un documento o un diff.
- Revisión mecánica: términos sin traducir según `CONTRIBUTING.md`, links rotos, inconsistencias entre capítulos.
- Resumir o comparar archivos largos sin gastar el contexto principal.
- Borrador corto (una sección, una tabla) que después Claude revisa y adapta.

No usarla para: cambios de estructura del repo, tareas que necesitan editar archivos, o cualquier cosa que dependa del contexto de esta conversación (Gemini no lo ve).

## Cómo

1. Armá un prompt autocontenido: qué leer (rutas), qué buscar, formato de salida esperado. Gemini no conoce esta conversación.
2. Corré el wrapper desde la raíz del repo:

```bash
.claude/skills/delegar-a-gemini/scripts/gemini.sh "Leé docs/10-skills.md y listá términos de Claude Code traducidos al español (deberían quedar en inglés según CONTRIBUTING.md). Formato: archivo:línea — término — sugerencia."
```

Opciones:
- `-m <modelo>`: por defecto `gemini-3.8-flash-medium` (rápido y barato). Para razonamiento más profundo, `gemini-3.1-pro-high`. Lista completa: `agy models`.
- `-o <archivo>`: además de imprimir, guarda la respuesta. Para revisiones que se procesan después, usá `.agents/inbox/YYYY-MM-DD-tema.md`.
- `-t <timeout>`: por defecto `5m`.

3. Para tareas largas, corrélo en background y seguí trabajando; el resultado llega cuando termina.
4. Si el wrapper falla con "Gemini no devolvió respuesta", casi siempre es porque intentó correr un comando de shell (en headless se niega automáticamente; aparece en `denied_actions`). Achicá la tarea o nombrá los archivos exactos a leer.
5. Tratá la respuesta como sugerencia: verificá antes de aplicar (Gemini puede equivocarse con detalles de Claude Code). Si guardaste en `.agents/inbox/`, borrá el archivo una vez procesado.
