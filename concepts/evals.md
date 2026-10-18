# Evals

> verificado: 2026-10-18 · fuentes: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests), [Plugin evals](https://code.claude.com/docs/en/plugin-evals), [Skills: evals con skill-creator](https://code.claude.com/docs/en/skills), [Evaluating skills (agentskills.io)](https://agentskills.io/skill-creation/evaluating-skills), [ADK eval](https://adk.dev/evaluate/)

Una eval es un test automatizado del comportamiento de un agent, un prompt, una skill o un subagent. Sin evals, una mejora es solo una impresión.

## Cuándo usarlo y cuándo no

**Usarlo para:**
- Skills y subagents que se reusan: ¿se disparan cuando corresponde? ¿mejoran el resultado frente a no tenerlos?
- Comparar versiones de un prompt o modelos.
- Detectar regresiones al cambiar instrucciones.

**No usarlo para:** prompts de un solo uso. Ahí basta con leer el resultado.

## Cómo funciona

| Término | Qué es |
|---|---|
| Task | Un caso: input + criterio de éxito |
| Trial | Una corrida de la task (el agent no es determinista: varias por task) |
| Grader | Lo que califica el trial |
| Transcript | Todo lo que hizo el agent: tool calls, razonamiento |
| Outcome | El estado final del entorno, **no** lo que el agent dice que hizo |

**Tipos de grader:**

| Grader | Pro | Contra |
|---|---|---|
| Código (tests, regex, `ruff`, ¿existe el archivo?) | Rápido y reproducible | Frágil ante salidas válidas pero distintas |
| LLM-as-judge (rúbrica) | Flexible | No determinista; hay que calibrarlo con humanos |
| Humano | El gold standard | Caro |

Para código: un grader determinista (¿pasan los tests?) primero, y una rúbrica LLM para lo que no se puede medir así. Usá como juez un modelo distinto del evaluado, que devuelva una salida parseable.

**Métricas**: pass@k = al menos 1 éxito en k intentos (sube con k). pass^k = los k exitosos (baja: con 75% por intento, 3 intentos dan ≈42%). pass@k sirve si alcanza con un éxito; pass^k mide consistencia.

**Dataset**: "20-50 simple tasks drawn from real failures is a great start". Para una skill alcanza con arrancar con 2–3 casos. Incluí casos donde el comportamiento **no** debería ocurrir.

## En Claude Code

- **`claude plugin eval`**: los casos van en `evals/<caso>/prompt.md` + `graders/*.md`. Hay graders `regex`, `tool_used`, `tool_order` y `file_exists` (gratis), y `llm` y `baseline` (usan un juez). Cada caso corre con y sin el plugin, y reporta `WITH`, `W/OUT` y `Δ`. `claude plugin eval init` genera los casos.
  - Ojo: `--threshold` mira solo `WITH`. El Δ no cambia el exit code, así que un CI puede pasar aunque el plugin no aporte nada.
- **skill-creator** (`/plugin install skill-creator@claude-plugins-official`): usa `evals/evals.json` dentro de la skill. Compara con y sin la skill, hace A/B ciego entre versiones y ajusta la `description` para que dispare bien. Su formato de casos no es compatible con el de `plugin eval`.

## En otras herramientas

- **Formato agnóstico** (agentskills.io): `evals.json` con `prompt`, `expected_output`, `files` y `assertions`. Las assertions se escriben después de ver la primera corrida.
- **Google ADK**: `adk eval` con métricas de trayectoria y respuesta. Es un framework de agents, no un coding agent. `no probado`
- No encontré nada equivalente documentado en Copilot, Cursor ni Gemini CLI (búsqueda corta, `no confirmado`).

## Errores comunes

- **Calificar la secuencia exacta de tool calls**: calificá el outcome, porque hay varios caminos válidos.
- **Leer un 0% como incapacidad del agent**: lo más común es que la task o el grader estén rotos.
- **Probar solo los casos positivos**: termina en over-triggering.
- **Estado compartido entre trials**: cada trial necesita un entorno limpio.
- **No leer los transcripts**: los números solos esconden por qué falla.
- **Graders que se pueden hacer trampa**: en CORE-Bench, arreglar el grading, las tasks ambiguas y el scaffold subió a Opus 4.5 de 42% a 95%.

## Ver también

[skills](skills.md) · [subagents](subagents.md) · [rag](rag.md)
