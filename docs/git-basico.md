# Git básico (y cómo se usa en este repo)

Esta es una guía personal para entender git desde cero: los conceptos generales primero, y después cómo se aplican concretamente acá. Para la convención específica de este repo (nombres de rama, cuándo abrir PR, cómo mergear) la referencia es [GIT.md](../GIT.md) — acá no se duplica esa parte, solo se explica el porqué de cada pieza.

## Qué es git

Git es un sistema de control de versiones: guarda el historial completo de cambios de un proyecto como una serie de "fotos" (commits), no como un solo archivo que se va pisando. Eso permite volver atrás, comparar versiones, y que varias personas (o agentes) trabajen en paralelo sin pisarse.

## Los conceptos clave

### Repository (repo)

La carpeta del proyecto con todo su historial de cambios guardado en `.git/`. `claudio-wiki` es un repo.

### Commit

Una "foto" de cómo está el proyecto en un momento dado, con un mensaje que explica qué cambió. Los commits se encadenan: cada uno sabe cuál es su commit anterior, y esa cadena es el historial.

```bash
git add archivo.md      # marca el archivo como "listo para el próximo commit" (staging area)
git commit -m "Agregar sección sobre X"   # crea el commit con lo que está en staging
```

La **staging area** (lo que hace `git add`) es un paso intermedio: podés modificar 5 archivos pero elegir con `git add` cuáles de esos cambios entran en el próximo commit. Es útil para armar commits prolijos en vez de "un commit = todo lo que tocaste esa tarde".

### Branch (rama)

Un puntero móvil a un commit. Cuando creás una rama nueva, estás diciendo "a partir de acá, quiero una línea de commits separada de `main`". Eso permite trabajar en algo sin afectar la rama principal hasta que esté listo.

```bash
git branch                          # lista ramas locales
git checkout -b feature/algo        # crea y cambia a una rama nueva
git checkout main                   # vuelve a main
```

En este repo, `main` es la rama estable — nadie comitea ahí directo (ver [GIT.md](../GIT.md)).

### Remote (origin)

Tu copia local del repo vive en tu disco. GitHub tiene otra copia. `origin` es el nombre por default que git le da a esa copia remota. `push` y `pull` son cómo se sincronizan:

```bash
git push origin feature/algo   # sube tus commits locales a GitHub
git pull                       # trae commits nuevos de GitHub a tu rama local
```

Si nunca pusheaste una rama nueva, hace falta `-u` la primera vez (`git push -u origin feature/algo`) para que git recuerde la asociación y después alcance con `git push` a secas.

### Merge

Combinar los commits de una rama en otra. Cuando un Pull Request se aprueba y se mergea, eso es exactamente esto: los commits de tu rama pasan a formar parte de `main`.

Hay variantes de merge (regular merge, squash, rebase) que difieren en cómo queda el historial resultante — ver más abajo cómo lo define este repo.

## Pull Requests (PR)

Un PR no es un concepto de git puro, sino de GitHub (y plataformas similares): es la propuesta de "tomá los commits de mi rama y sumalos a `main`", con una vista del diff completo para revisar antes de integrar. Es el punto de control real antes de que algo quede en la rama estable.

## Cómo se usa todo esto en este repo

La convención puntual (nombres de rama, mensajes de commit, squash merge) está en [GIT.md](../GIT.md) — no se repite acá. La idea general es:

1. Rama corta desde `main` con prefijo (`docs/`, `fix/`, `feature/`, `chore/`).
2. Commits en español, imperativo, una línea.
3. PR obligatorio antes de mergear — incluso siendo el único autor, porque ver el diff completo en GitHub es donde se nota lo que en el editor pasa desapercibido.
4. **Squash and merge**: todos los commits de la rama se colapsan en uno solo prolijo al entrar a `main`. Por eso en el historial de `main` no vas a ver los commits intermedios de "prueba", "ajuste", etc. de cada rama.
5. La rama se borra sola después de mergear (está configurado en GitHub).

### Worktrees

Un detalle que no está en `GIT.md` pero que conviene entender: además de tu checkout normal en `/Users/gonza/workspace/claudio`, las sesiones de Claude Code a veces trabajan en un **worktree** — una copia separada del mismo repo, en otra carpeta (`.claude/worktrees/...`), pero atada a la misma base de git (comparten el historial, no son repos distintos).

Esto existe para que una sesión de Claude Code pueda tener una rama propia "afuera" sin arriesgar pisar lo que vos tenés abierto en tu checkout principal — por eso, por ejemplo, una sesión en un worktree no puede ejecutar comandos de git contra `/Users/gonza/workspace/claudio` directamente. Cuando el trabajo en el worktree termina y su rama ya se mergeó, lo único que falta es sincronizar tu checkout principal:

```bash
git checkout main
git pull
git branch -d nombre-de-la-rama   # por si quedó localmente
```
