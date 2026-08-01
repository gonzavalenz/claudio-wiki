# Estructura de proyecto para sacarle el jugo

## Qué archivos/carpetas ayudan a que Claude Code sea más efectivo en un repo

Claude Code funciona en cualquier repo sin configuración previa, pero rinde notablemente mejor cuando el proyecto tiene ciertos elementos:

- **`CLAUDE.md`** en la raíz (ver [Memoria](05-memoria.md)): contexto persistente del proyecto, para no reexplicar lo mismo cada sesión.
- **Carpeta de configuración del proyecto** (`.claude/` o equivalente) con `settings.json` versionado: permisos, comandos custom y skills compartidas por todo el equipo (ver [Permisos](07-permisos.md)).
- **Comandos de build/test/lint estándar y descubribles** (`package.json`, `Makefile`, etc.): cuanto más convencional la forma de correr tests o levantar el proyecto, menos tiene que adivinar el agente.
- **Convenciones de código consistentes**: un repo con un estilo homogéneo es más fácil de "leer" correctamente por el agente que uno con varios estilos mezclados sin explicación.

## Organización recomendada de `CLAUDE.md`, skills y comandos dentro de un proyecto

Una estructura típica y ordenada:

```
mi-proyecto/
├── CLAUDE.md                     # Contexto permanente del proyecto
├── .claude/
│   ├── settings.json              # Permisos y config compartida (versionado)
│   ├── settings.local.json        # Permisos personales (gitignored)
│   ├── skills/                    # Skills específicas del proyecto
│   └── commands/                  # Slash commands custom del proyecto
└── ...
```

Principios detrás de esta organización:

- Lo que es **compartido por el equipo** (contexto, skills, comandos, permisos base) va versionado en el repo.
- Lo que es **personal** (allowlist propia, preferencias individuales) va en un archivo separado y gitignored, para que no choque entre distintas personas del equipo.
- `CLAUDE.md` se mantiene corto y de alto nivel; los procedimientos largos y puntuales van como [skills](08-skills.md) separadas, no todo amontonado en el mismo archivo.

## Errores comunes de estructura que confunden al agente

- **`CLAUDE.md` gigante y desactualizado**: si tiene miles de líneas y la mitad ya no es cierta, termina siendo peor que no tener nada — el agente puede seguir instrucciones obsoletas.
- **Mezclar contexto permanente con instrucciones de una tarea puntual**: pedidos de "hoy quiero que hagas X" no deberían terminar viviendo en `CLAUDE.md` — eso ensucia el contexto de todas las sesiones futuras.
- **Convenciones que solo existen "en la cabeza del equipo"**: si una regla importante no está en ningún lado escrito (ni en `CLAUDE.md` ni en una skill), el agente no tiene forma de conocerla, y tampoco la tendría una persona nueva en el equipo.
- **Comandos de build/test no estandarizados o rotos**: si ni siquiera una persona puede correr los tests siguiendo el `README`, el agente tampoco va a poder — y va a perder tiempo/tokens tratando de adivinar cómo hacerlo.
- **No versionar nada de la configuración de Claude Code**: dejar todo en configuración local hace que cada persona del equipo tenga que rearmar lo mismo, y que el comportamiento del agente varíe según quién lo use.
