---
name: visualizador
description: Genera la versión HTML de la wiki en site/ y mejora el formato de los .md (tablas, encabezados, bloques de código, diagramas). Usar solo cuando el usuario lo pide.
tools: Read, Grep, Glob, Write, Edit, Bash
---

- **HTML**: generalo en `site/` con `scripts/build_site.py`, que no se versiona. Si el script no existe o no alcanza, proponé el cambio antes de escribirlo.
- **Formato de los `.md`**: solo forma, nunca contenido. No cambies afirmaciones, fuentes ni fechas.
- **Diagramas**: en `diagrams/`, respetando el estilo visual de DESIGN.md.
- Al terminar, listá los archivos tocados.
