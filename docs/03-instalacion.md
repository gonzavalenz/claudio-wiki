# Instalación y primeros pasos

> **En 30 segundos:** instalá con el instalador nativo (`curl -fsSL https://claude.ai/install.sh | bash`), abrí una terminal nueva, entrá a tu repo y corré `claude`. La primera vez te pide login en el navegador. Después corré `/init` para generar el `CLAUDE.md` y arrancá con una tarea chica.

## Requisitos

- **Sistema**: macOS 13+, Windows 10 1809+, Ubuntu 20.04+, Debian 10+ o Alpine 3.19+. 4 GB de RAM.
- **Shell**: Bash, Zsh, PowerShell o CMD.
- **Cuenta**: Pro, Max, Team, Enterprise o Console (API). **El plan gratis de claude.ai no incluye Claude Code.** También funciona con proveedores cloud (Amazon Bedrock, Google Cloud's Agent Platform —ex Vertex AI—, Microsoft Foundry).

## Instalar

| Método | Comando | Se actualiza solo |
|---|---|---|
| **Nativo (recomendado)** — macOS, Linux, WSL | `curl -fsSL https://claude.ai/install.sh \| bash` | Sí |
| Nativo — Windows PowerShell | `irm https://claude.ai/install.ps1 \| iex` | Sí |
| Homebrew | `brew install --cask claude-code` | No (`brew upgrade claude-code`) |
| WinGet | `winget install Anthropic.ClaudeCode` | No |
| npm (requiere Node.js 22+) | `npm install -g @anthropic-ai/claude-code` | No |

Verificá:

```bash
claude --version   # imprime la versión, ej. "2.1.xxx (Claude Code)"
claude doctor      # diagnóstico de instalación y settings, sin abrir sesión
```

Si dice `command not found`, el directorio de instalación no está en el `PATH`: abrí una terminal nueva o revisá la guía de troubleshooting oficial.

## Login

```bash
cd ~/repos/dbt-analytics
claude
```

La primera vez abre el navegador para loguearte. Si no se abre, apretá `c` para copiar la URL. En WSL, SSH o contenedores puede aparecer un código para pegar en la terminal.

| Situación | Qué hacer |
|---|---|
| Cambiar de cuenta | `/login` dentro de la sesión |
| Cerrar sesión | `/logout` |
| Tenés `ANTHROPIC_API_KEY` exportada | Claude Code te pide aprobar esa key en vez de abrir el navegador |
| Tu empresa usa Claude vía GCP | Ver abajo |

### Usarlo con Claude en Google Cloud

Si tu organización consume Claude por Google Cloud's Agent Platform, en vez de loguearte con claude.ai configurás variables de entorno:

```bash
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=global
export ANTHROPIC_VERTEX_PROJECT_ID=mi-proyecto-gcp
claude
```

También existe `/setup-vertex`, un asistente interactivo (oculto en el menú hasta que `CLAUDE_CODE_USE_VERTEX=1` esté seteado; escribilo completo).

## Primera sesión en un repo

1. **Pararte en la raíz del repo** (`cd`). Claude Code trabaja sobre la carpeta donde lo abrís.
2. **Aceptar el diálogo de confianza** (*workspace trust*) la primera vez: te muestra qué permisos o hooks trae el repo.
3. **Correr `/init`**: analiza el proyecto y genera un `CLAUDE.md` con comandos de build/test y convenciones. Si ya existe, propone mejoras en vez de pisarlo.
4. **Pulir el `CLAUDE.md`** con lo que Claude no puede deducir del código (ver [Memoria](06-memoria.md)).
5. **Arrancar con preguntas**, no con cambios:

```text
¿cómo está organizado este proyecto dbt? ¿qué capas hay y cómo se nombran los modelos?
```

6. **Después, una tarea chica y verificable**:

```text
agregá un test unique sobre pedido_id en stg_pedidos y corré dbt test --select stg_pedidos
```

Atajos que conviene saber desde el día uno: `/` lista comandos, `Shift+Tab` cambia el modo de permisos, `Esc` frena a Claude, `/help` muestra la ayuda. Ver [Comandos](08-comandos-slash.md).

## Formas de lanzar `claude`

```bash
claude                                   # sesión interactiva
claude "explicá qué hace dags/ingesta_ventas.py"   # interactiva con un prompt inicial
claude -p "listá los modelos sin tests"  # una consulta y sale (modo no interactivo)
claude -c                                # continúa la última conversación en esta carpeta
claude -r                                # elige una sesión anterior de una lista
claude -n migracion-staging              # arranca con un nombre de sesión
```

## IDE y terminal

| Dónde | Cómo |
|---|---|
| VS Code / Cursor | Extensiones (`Cmd+Shift+X`) → buscar "Claude Code" → Install. Trae su propio CLI para el panel |
| JetBrains (PyCharm...) | Instalar el CLI + el plugin "Claude Code" del JetBrains Marketplace. Desde una terminal externa, `/ide` lo conecta al IDE |
| Saltos de línea en el prompt | `\` + `Enter` funciona en todas las terminales; `Shift+Enter` es nativo en iTerm2, Ghostty, Kitty, WezTerm, Warp, Apple Terminal y Windows Terminal |
| Otras terminales | `/terminal-setup` instala `Shift+Enter` en VS Code, Cursor, Alacritty, Zed; en Apple Terminal habilita `Option+Enter` |

## Actualizar

La instalación nativa se actualiza sola en segundo plano. Para forzarlo:

```bash
claude update
```

## Trucos y errores comunes

- **No uses `sudo npm install -g`**: genera problemas de permisos. Preferí el instalador nativo.
- **Para actualizar con npm**, `npm install -g @anthropic-ai/claude-code@latest`. `npm update -g` puede no llevarte a la última versión.
- **Abrí `claude` en la raíz del repo, no en tu home**: la carpeta define qué `CLAUDE.md` se carga, a qué archivos tiene acceso y dónde se guardan las sesiones.
- **Si algo anda raro**, `/doctor` dentro de la sesión diagnostica (y puede arreglar) problemas de instalación y configuración.
- **Lo demás es incremental**: skills, hooks, MCP y plugins se suman cuando hacen falta. No los necesitás para empezar.

## Ver también

- [Modelos](04-modelos.md) — cuál usar y cómo cambiarlo
- [Memoria](06-memoria.md) — qué poner en el `CLAUDE.md` que genera `/init`
- [Permisos](07-permisos.md) — cuánta autonomía darle desde el principio
- [MCP](13-mcp.md) — conectar BigQuery, Jira y otros servicios
