# Reglas para agentes

Wiki técnica personal sobre coding agents. Antes de crear o editar contenido, leé [DESIGN.md](DESIGN.md): ahí están el objetivo, la estructura, la plantilla y los agentes del proyecto.

## Usuario

Ingeniero y arquitecto de datos, trabaja con Python. Usa GCP en el laburo, pero no en esta máquina: los ejemplos deben ser agnósticos o locales (Python, DuckDB, SQLite), salvo que pida otra cosa.

## Reglas

- **Texto mínimo.** Nada de relleno ni redundancia. Si la documentación oficial ya lo explica bien, se enlaza.
- **Español técnico.** Los términos de la industria quedan en inglés (`skill`, `hook`, `context window`, etc.).
- **Verificar.** Toda afirmación técnica tiene que tener una fuente primaria. Si no se pudo verificar, se dice.
- **Challengear.** Si un pedido del usuario parece mala idea, decirlo con el motivo antes de ejecutarlo.
- **Preguntas al usuario** van en [PREGUNTAS.md](PREGUNTAS.md), no en el chat. Una vez respondidas e incorporadas, se borran de ese archivo.
- **Git**: rama + PR según [GIT.md](GIT.md). Nunca commit ni push a `main`, ni merge sin pedido explícito.
- **Cambios estructurales** (carpetas, `DESIGN.md`, agentes): se proponen al usuario antes de aplicarlos.
