# Plugins: empaquetar y compartir tu setup

> **En 30 segundos:** un plugin es una carpeta que junta skills, subagents, hooks y servers MCP para instalarlos como una sola unidad. Se instalan desde un *marketplace* (un repo con un catálogo) con `/plugin`. Sirven para dos cosas: aprovechar setups que armó otro (el marketplace oficial de Anthropic ya viene agregado) y repartirle al equipo tu propio setup con un comando.

## Qué es y cómo funciona

Todo lo que vimos en [skills](10-skills.md), [subagents](11-subagents.md), [hooks](12-hooks.md) y [MCP](13-mcp.md) funciona suelto, sin plugins. El plugin aparece cuando querés **empaquetar varias piezas juntas** y distribuirlas con versiones y actualizaciones.

Un plugin puede traer:

| Componente | Dónde va en el plugin | Qué te da |
|---|---|---|
| Skills | `skills/<nombre>/SKILL.md` | `/nombre-plugin:skill` |
| Subagents | `agents/<nombre>.md` | Agentes a los que Claude puede delegar |
| Hooks | `hooks/hooks.json` | Hooks que se suman a los tuyos |
| Servers MCP | `.mcp.json` | Tools externas mientras el plugin está habilitado |
| Commands (formato viejo) | `commands/*.md` | Igual que skills; para plugins nuevos usá `skills/` |
| Language servers (LSP) | Ver docs | Diagnósticos y navegación de código (ej. `pyright-lsp` para Python) |

Más el manifiesto `.claude-plugin/plugin.json`, que le da nombre y versión.

Un **marketplace** es un repo (o carpeta, o URL) con un `.claude-plugin/marketplace.json` que lista plugins y de dónde bajar cada uno. No es una tienda: es un catálogo.

### Marketplaces de Anthropic

| Nombre (lo que va después de `@`) | Repo | Cómo lo tenés |
|---|---|---|
| `claude-plugins-official` | `anthropics/claude-plugins-official` | Se agrega solo la primera vez que abrís Claude Code |
| `claude-community` | `anthropics/claude-plugins-community` | `/plugin marketplace add anthropics/claude-plugins-community` |
| `claude-code-plugins` (demo) | `anthropics/claude-code` | `/plugin marketplace add anthropics/claude-code` |

Cualquier otro marketplace (de tu empresa, de un colega, de GitHub) es "third-party": Anthropic no lo revisa.

## Cómo se usa

### Instalar

```text
/plugin                                              # abre el panel; pestaña Discover para buscar
/plugin install commit-commands@claude-plugins-official
```

`/plugin install` abre el detalle del plugin: qué va a instalar (skills, subagents, hooks, MCP) y, en el marketplace oficial, una estimación de **costo de contexto** por turno. Elegís el scope y listo. Si el resumen dice `Run /reload-plugins to activate.`, Claude Code lo recarga solo.

| Scope | Dónde queda habilitado | Para quién |
|---|---|---|
| User | `~/.claude/settings.json` | Vos, en todos los proyectos |
| Project | `.claude/settings.json` (se commitea) | Todo el que trabaje en el repo |
| Local | `.claude/settings.local.json` | Vos, solo en este repo |

Desde la terminal (útil para scripts de setup):

```bash
claude plugin install pyright-lsp@claude-plugins-official
claude plugin list
claude plugin disable commit-commands@claude-plugins-official
claude plugin uninstall commit-commands@claude-plugins-official
claude plugin update commit-commands@claude-plugins-official
```

Los skills de un plugin se invocan con prefijo: `/commit-commands:commit`.

### Algunos plugins oficiales que vale la pena mirar

| Plugin | Qué hace |
|---|---|
| `skill-creator` | Crear skills y evaluarlas con/sin skill (ver [Skills](10-skills.md)) |
| `plugin-dev` | Asistente para armar plugins: `/plugin-dev:create-plugin` |
| `mcp-server-dev` | Scaffolding de un server MCP propio |
| `commit-commands` | Commit, push y PR |
| `code-review`, `security-guidance`, `feature-dev` | Revisión de código, guía de seguridad, desarrollo de features |
| `pyright-lsp` | Language server de Python (requiere `pyright-langserver` instalado) |

El catálogo cambia seguido: la pestaña **Discover** de `/plugin` es la fuente de verdad.

### Agregar otro marketplace

```text
/plugin marketplace add mi-org/claude-plugins           # GitHub owner/repo
/plugin marketplace add mi-org/claude-plugins#v1.2.0    # fijado a un tag
/plugin marketplace add https://gitlab.empresa.com/datos/plugins.git
/plugin marketplace add ./mi-marketplace                # carpeta local
```

Marketplaces privados usan tus credenciales de git ya configuradas (`gh auth login`, SSH); Claude Code nunca te pide contraseña.

## Ejemplo: el plugin del equipo de datos

Juntar en un plugin lo que el equipo usa siempre: la skill de revisión, el subagent revisor de dbt, los hooks de ruff y de bloqueo de borrados, y el MCP de Linear.

```text
plugins-datos/                         # el repo del marketplace
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── datos-equipo/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── skills/
        │   └── revisar-modelo-dbt/SKILL.md
        ├── agents/
        │   └── revisor-dbt.md
        ├── hooks/
        │   └── hooks.json
        ├── scripts/
        │   ├── ruff.sh
        │   └── bloquear-destructivos.py
        └── .mcp.json
```

`plugins/datos-equipo/.claude-plugin/plugin.json`:

```json
{
  "name": "datos-equipo",
  "description": "Setup del equipo de data engineering: revisión de dbt, ruff, bloqueo de borrados en BigQuery/GCS",
  "version": "1.0.0",
  "author": { "name": "Equipo de Datos" }
}
```

`plugins/datos-equipo/hooks/hooks.json` (mismo formato que en settings, con `${CLAUDE_PLUGIN_ROOT}` para apuntar a los scripts del plugin):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/bloquear-destructivos.py", "args": [] }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/ruff.sh", "args": [] }]
      }
    ]
  }
}
```

`.claude-plugin/marketplace.json` en la raíz del repo:

```json
{
  "name": "plugins-datos",
  "owner": { "name": "Equipo de Datos" },
  "plugins": [
    {
      "name": "datos-equipo",
      "source": "./plugins/datos-equipo",
      "description": "Setup del equipo de data engineering"
    }
  ]
}
```

Validar y probar antes de publicar:

```bash
claude plugin validate ./plugins-datos
claude --plugin-dir ./plugins-datos/plugins/datos-equipo    # prueba en una sesión, sin instalar
```

### Que el equipo lo tenga al abrir el repo

En el `.claude/settings.json` de cada repo de datos:

```json
{
  "extraKnownMarketplaces": {
    "plugins-datos": {
      "source": { "source": "github", "repo": "mi-org/plugins-datos" }
    }
  },
  "enabledPlugins": {
    "datos-equipo@plugins-datos": true
  }
}
```

Al abrir el repo y aceptar el diálogo de confianza, Claude Code registra el marketplace y habilita el plugin. Como el plugin está en el mismo repo del marketplace (ruta relativa), se carga desde ahí. Si el plugin apuntara a otro repo, cada persona tendría que correr una vez `claude plugin install datos-equipo@plugins-datos --scope project`.

## Trucos y errores comunes

- **Un plugin habilitado cuesta contexto en cada turno**, aunque no lo uses: nombres y descripciones de sus skills y agentes van siempre. Deshabilitá lo que no usás; la pestaña **Installed** de `/plugin` agrupa los "no usados recientemente" y `/skill-doctor` muestra el costo.
- **Un plugin corre código con tus permisos** (hooks, servers MCP). Leé el detalle antes de instalar, sobre todo de marketplaces third-party.
- **Solo `plugin.json` va dentro de `.claude-plugin/`.** Skills, agentes y hooks van en la raíz del plugin; si los ponés adentro de `.claude-plugin/`, no cargan.
- **El `name` de la entrada en `marketplace.json` tiene que coincidir con el `name` de `plugin.json`**, y las rutas `source` son relativas a la raíz del marketplace. Son las dos causas más comunes de instalaciones que fallan.
- **Actualizaciones:** el marketplace oficial se actualiza solo; los third-party vienen con auto-update apagado (se prende desde la pestaña **Marketplaces**). La sesión abierta sigue con la versión vieja hasta `/reload-plugins`.
- **Algunos campos de subagents no aplican en plugins**: `hooks`, `mcpServers` y `permissionMode` del frontmatter se ignoran por seguridad. Poné los hooks en `hooks/hooks.json` y los servers en `.mcp.json` del plugin.
- **Plugins en la nube:** las sesiones cloud y las [rutinas](16-automatizacion.md) no cargan los plugins de tu máquina ni los que habilita el `.claude/settings.json` del repo. Lo que necesites ahí, commitealo como skill en `.claude/skills/`.
- **Atajo para algo personal:** `claude plugin init mi-tool` crea un plugin en `~/.claude/skills/mi-tool/` que se carga en todas tus sesiones sin marketplace.
- **`/plugin` no funciona en `claude -p`**: instalá desde la shell con `claude plugin install`; los plugins ya instalados sí cargan en modo headless.

## Ver también

- [Skills](10-skills.md), [Subagents](11-subagents.md), [Hooks](12-hooks.md), [MCP](13-mcp.md) — las piezas que empaqueta un plugin.
- [Estructura de proyecto](19-estructura-de-proyecto.md) — dónde vive cada cosa en `.claude/`.
- Documentación oficial: [Plugins](https://code.claude.com/docs/en/plugins/overview) · [Instalar](https://code.claude.com/docs/en/plugins/install) · [Crear](https://code.claude.com/docs/en/plugins/create) · [Crear un marketplace](https://code.claude.com/docs/en/plugins/create-marketplace).
