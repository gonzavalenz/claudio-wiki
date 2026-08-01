# Instalación y primeros pasos

## Requisitos e instalación del CLI

Claude Code corre como un CLI (`claude`) que se instala una vez en la máquina y queda disponible en cualquier proyecto. No requiere que el proyecto tenga ninguna configuración especial para empezar a usarlo — se ejecuta desde la carpeta del repo que se quiera trabajar.

Requisitos generales:
- Una terminal (macOS, Linux o Windows con WSL).
- Node.js instalado (el CLI se distribuye como paquete npm).
- Una cuenta de Anthropic con acceso a Claude Code (plan de consumo por API o suscripción, según cómo se facture).

Instalación típica vía npm:

```bash
npm install -g @anthropic-ai/claude-code
```

(Confirmar siempre el comando exacto en la documentación oficial al momento de instalar, ya que el nombre del paquete y el método de instalación pueden cambiar entre versiones.)

## Login / autenticación

Antes de poder usarlo hay que autenticar la cuenta. Dentro de una sesión de Claude Code, esto se hace con:

```
/login
```

Esto abre el flujo de autenticación (típicamente vía navegador) y deja la sesión de terminal autenticada para las siguientes veces, sin tener que repetir el login en cada proyecto.

Esto es distinto de `gh auth login` (autenticación de GitHub CLI) — son dos herramientas separadas con su propia autenticación. Ver [MCP](11-mcp.md) si además se van a conectar servidores externos que requieran sus propias credenciales.

## Primer uso: correr Claude Code en un proyecto por primera vez

1. Pararse en la carpeta raíz del proyecto (`cd` hasta ahí).
2. Correr `claude` para iniciar una sesión interactiva.
3. Si es la primera vez en ese repo, correr `/init` — analiza el proyecto y genera un `CLAUDE.md` inicial con contexto útil (estructura, comandos de build/test, convenciones detectadas). Ver [Memoria](05-memoria.md) para qué va en ese archivo y cómo mantenerlo.
4. Empezar con pedidos concretos y acotados mientras se genera confianza en cómo actúa el agente en ese repo puntual (ver [Permisos](07-permisos.md) sobre cuánta autonomía darle desde el principio).

No hace falta ninguna configuración adicional para arrancar — el resto (skills, hooks, MCP, comandos custom) es incremental y se suma a medida que hace falta, no es requisito para el primer uso.
