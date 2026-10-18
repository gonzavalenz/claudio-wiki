# RAG

> verificado: 2026-10-18 · fuentes: [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works), [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval), [Embeddings (Claude)](https://platform.claude.com/docs/en/build-with-claude/embeddings), [DuckDB array functions](https://duckdb.org/docs/current/sql/functions/array.html), [DuckDB vss](https://duckdb.org/docs/current/core_extensions/vss.html), [DuckDB fts](https://duckdb.org/docs/current/core_extensions/full_text_search.html), [Cursor semantic search](https://cursor.com/docs/context/semantic-search), [VS Code workspace context](https://code.visualstudio.com/docs/agents/reference/workspace-context), [Gemini CLI file tools](https://www.geminicli.com/docs/tools/file-system)

Retrieval-Augmented Generation: antes de generar, se recuperan fragmentos relevantes de una base de conocimiento y se meten en el prompt. En los coding agents, la tendencia es reemplazar los índices de embeddings por **agentic search**: el agent busca con grep/glob y lee los archivos.

## Cuándo usarlo y cuándo no

**No usarlo cuando:**
- **El corpus entra en contexto.** Para menos de ~200k tokens (~500 páginas), Anthropic recomienda meterlo entero en el prompt con prompt caching. Esta wiki entra entera.
- **El corpus es código del repo.** Grep + lectura no requiere build, no se desactualiza y no saca datos de la máquina.

**Usarlo cuando:**
- El corpus es grande y no es código: documentación interna, tickets, catálogos de datos.
- Las búsquedas son semánticas y no hay términos exactos para grep ("¿dónde calculamos el churn?").
- Se expone como tool vía [MCP](mcp.md), para que el agent decida cuándo consultarlo. No encontré guía oficial sobre esto: es inferencia.

## Cómo funciona

1. **Chunking**: partir los documentos en fragmentos de a lo sumo unos cientos de tokens. En Markdown, cortar por encabezado (criterio propio, no de la fuente).
2. **Embeddings**: convertir cada chunk en un vector. Usá el mismo modelo para la query y para los documentos, con su `input_type` (`query` / `document`).
3. **Retrieval**: top-k por similitud de coseno.
4. **Mejoras** (con cifras de Contextual Retrieval, sobre la tasa de fallo de recall@20):

| Técnica | Reducción del fallo |
|---|---|
| Anteponer a cada chunk un contexto de 50–100 tokens | −35% |
| + BM25 (híbrido léxico + semántico) | −49% |
| + reranking del top-150 a top-20 | −67% |

Anthropic no tiene modelo de embeddings propio: recomienda Voyage. `voyage-4-nano` tiene pesos abiertos y sirve para correr local sin API key, pero no lo probé.

## En local: Python + DuckDB

Para un corpus chico alcanza con búsqueda exacta, sin índice:

```sql
CREATE TABLE chunks (path TEXT, body TEXT, vec FLOAT[1024]);  -- dimensión del modelo (voyage-4-nano: 256–2048)

SELECT path, body
FROM chunks
ORDER BY array_cosine_distance(vec, ?::FLOAT[1024])
LIMIT 5;
```

- **`vss` (HNSW)**: indexa con `CREATE INDEX ... USING HNSW (vec) WITH (metric = 'cosine')`. Solo se usa con `ORDER BY <dist>(...) LIMIT k`; confirmalo con `EXPLAIN` (tiene que aparecer `HNSW_INDEX_SCAN`). El índice vive en RAM. En una base en disco hace falta `SET hnsw_enable_experimental_persistence = true`, que es experimental y tiene riesgo de corrupción.
- **`fts` (BM25)**: `PRAGMA create_fts_index(...)` + `match_bm25(...)` para el híbrido. El índice **no se actualiza solo**: hay que recrearlo con `overwrite := 1` cuando cambia la tabla.

El ejercicio completo va en `examples/` (fase 5).

## En Claude Code

No usa índice de embeddings. Recupera contexto con el agentic loop (Glob, Grep, Read) y, si están instalados los plugins de code intelligence, con definiciones y referencias. Los docs no dicen "no usamos RAG", pero no documentan ningún índice. Según declaraciones de su autor ([fuente secundaria](https://officechai.com/ai/claude-researcher-explains-how-agentic-search-performed-better-than-rag-for-code-generation/), `no confirmado`), empezaron con RAG y lo abandonaron porque agentic search funcionaba mejor.

## En otras herramientas

- **Cursor**: no guarda embeddings del código. Usa un índice local de regex y un subagent de exploración. `no probado`
- **Copilot (VS Code)**: es híbrido. Combina un índice semántico (remoto para repos de GitHub, local para el resto) con grep, y cae a grep si el índice no está listo. El índice local viene apagado por defecto en cuentas de organización o enterprise. `no probado`
- **Gemini CLI**: solo `glob` y `grep_search`, sin índice semántico. `no probado`

## Errores comunes

- **Indexar algo que entra en contexto**: suma complejidad sin ganancia.
- **No reindexar**: el índice queda desactualizado y el agent responde con información vieja.
- **Mezclar modelos o `input_type`** entre la query y los documentos.
- **Indexar lo que debería ignorarse**: respetá `.gitignore` y las exclusiones.
- **Persistir HNSW en producción** sin conocer el riesgo.

## Ver también

[context](context.md) · [mcp](mcp.md) · [evals](evals.md)
