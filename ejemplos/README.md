# Ejemplos

Artefactos copiables para un repo de datos (Python, BigQuery, dbt, Airflow/Composer). Código y config primero, explicación mínima al lado. Todos los formatos (frontmatter, eventos de hooks, sintaxis de permisos) están verificados contra la [documentación oficial](https://code.claude.com/docs/en/claude_code_docs_map.md).

| Carpeta | Qué hay | Va en tu repo como |
|---|---|---|
| [`claude-md/`](claude-md/README.md) | `CLAUDE.md` para un proyecto dbt + BigQuery y para un repo de DAGs de Airflow | `CLAUDE.md` |
| [`settings/`](settings/README.md) | Permisos `allow` / `ask` / `deny` pensados para el stack | `.claude/settings.json` |
| [`hooks/`](hooks/README.md) | Guardia de BigQuery, formato con ruff, notificación de macOS | `.claude/hooks/*.sh` + bloque `hooks` en settings |
| [`agents/`](agents/README.md) | Subagents `revisor-dbt` y `explorador-lineage` | `.claude/agents/*.md` |
| [`skills/`](skills/README.md) | `dbt-nuevo-modelo` y `revision-de-diffs` | `.claude/skills/<nombre>/SKILL.md` |
| [`mcp/`](mcp/README.md) | Servers MCP de BigQuery, dbt y GitHub | `.mcp.json` |

## Kit mínimo para un repo nuevo

```bash
cd ~/repos/mi-proyecto-dbt
W=~/workspace/claudio/ejemplos      # ruta a esta carpeta

cp $W/claude-md/dbt-bigquery.md CLAUDE.md
mkdir -p .claude/hooks .claude/agents .claude/skills
cp $W/settings/settings.json .claude/settings.json
cp $W/hooks/scripts/{guardia-bigquery,formatear-python}.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh
cp $W/agents/revisor-dbt.md $W/agents/explorador-lineage.md .claude/agents/
cp -r $W/skills/dbt-nuevo-modelo .claude/skills/
```

Después: sumar el bloque `hooks` de [`hooks/settings-proyecto.json`](hooks/settings-proyecto.json) dentro de `.claude/settings.json`, adaptar el `CLAUDE.md`, abrir `claude` y verificar con `/permissions`, `/hooks`, `/skills` y `/context`.

## Qué se commitea y qué no

| Archivo | ¿Se commitea? |
|---|---|
| `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/`, `.claude/agents/`, `.claude/skills/`, `.mcp.json` | Sí: es config del equipo |
| `.claude/settings.local.json`, `CLAUDE.local.md` | No: preferencias tuyas para ese repo |
| `~/.claude/settings.json`, `~/.claude/CLAUDE.md`, `~/.claude/agents/` | No: viven en tu home, aplican a todos tus repos |

Ver [19 — Estructura de proyecto](../docs/19-estructura-de-proyecto.md).
