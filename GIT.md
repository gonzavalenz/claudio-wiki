# Flujo de git

Este documento define cómo se maneja el control de versiones en este repo. Es un flujo simple (GitHub Flow) pensado para ir practicando git de forma genuina, sin la complejidad de modelos como Gitflow. No confundir con `CONTRIBUTING.md`, que habla de convenciones de *contenido* (idioma, formato, dónde va cada cosa), no de proceso.

## Regla principal

**`main` siempre queda estable.** Nadie comitea directo ahí — ni el usuario, ni un agente (ver [AGENTS.md](AGENTS.md)). Todo cambio, grande o chico, entra por una rama y un Pull Request.

## El ciclo

1. **Rama corta desde `main`**, con nombre `tipo/descripcion-corta`:
   - `docs/` — contenido nuevo o editado (capítulos, casos de uso, ejemplos).
   - `fix/` — corrección de algo que está mal (typo, dato erróneo, enlace roto).
   - `feature/` — algo nuevo a nivel repo (una carpeta, una skill, infraestructura).
   - `chore/` — mantenimiento (reorganizar, renombrar, actualizar config).

   Ejemplos: `docs/agregar-capitulo-mcp`, `fix/typo-en-permisos`.

2. **Commits con el estilo actual**: español, en imperativo/infinitivo, una línea (`Agregar`, `Corregir`, `Unificar`, `Completar`...). No se usa Conventional Commits (`feat:`, `fix:`) — se mantiene lo que ya se viene usando en el historial.

3. **Pull Request antes de mergear.** Aunque seas el único autor y revisor, abrir el PR y mirar el diff completo ahí es el punto de control real — a veces se ve algo (un archivo de más, un cambio no intencional) que en el editor no se nota.

4. **Merge con "Squash and merge"** desde GitHub. Cada PR queda como un solo commit prolijo en `main`, sin los commits intermedios de la rama (típicos de ir probando cosas).

5. **Borrar la rama después de mergear.** El repo tiene activado "Automatically delete head branches", así que esto es automático en GitHub — solo falta sincronizar el checkout local (ver comandos abajo).

## Comandos típicos (el ciclo completo)

```bash
# 1. Crear la rama desde main actualizado
git checkout main
git pull
git checkout -b docs/nombre-corto

# 2. Trabajar y comitear
git add archivo.md
git commit -m "Agregar sección sobre X"

# 3. Pushear y abrir el PR
git push -u origin docs/nombre-corto
gh pr create --fill

# 4. Revisar el diff en GitHub, mergear con "Squash and merge"
gh pr merge --squash --delete-branch

# 5. Sincronizar el checkout local
git checkout main
git pull
git branch -d docs/nombre-corto   # por si no se borró sola en el checkout local
```

## Qué no cambia

- No hay CI ni checks automáticos — el PR es una revisión manual, no un gate técnico.
- No se agregan templates de PR ni checklist formales — mantenerlo liviano.
