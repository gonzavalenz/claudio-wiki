# Preguntas abiertas

Respondé debajo de cada una. Mi recomendación va entre paréntesis.

## 1. Fase 5: ¿RAG local sobre la wiki?

Anthropic recomienda no hacer RAG si el corpus pesa menos de ~200k tokens: conviene meterlo entero en el prompt con caching ([fuente](https://www.anthropic.com/engineering/contextual-retrieval)). Esta wiki entra entera, así que el RAG sobre ella sirve solo como ejercicio. Opciones:

- a) Mantenerlo como ejercicio didáctico, aclarándolo en el ejemplo.
- b) Hacerlo sobre un corpus que sí lo justifique: por ejemplo, docs de dbt/DuckDB descargadas o un catálogo de datos de juguete.

(Recomiendo **b**: el ejercicio se parece más a un caso real de tu trabajo.)

Respuesta:

