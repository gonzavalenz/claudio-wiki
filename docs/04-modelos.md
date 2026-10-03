# Modelos: cuál usar para qué

> **En 30 segundos:** hay cuatro familias (Fable, Opus, Sonnet, Haiku) y dos perillas: **qué modelo** (`/model`) y **cuánto razona** (`/effort`). El default suele ser Opus con esfuerzo `medium`, y alcanza para casi todo. Subí el esfuerzo o pasá a Fable para problemas difíciles y largos; bajá a Sonnet/Haiku o a esfuerzo `low` para tareas mecánicas.

## Familias y cuándo usar cada una

| Alias | Para qué | Comentario |
|---|---|---|
| `fable` | Las tareas más difíciles y largas: root cause de incidentes, decisiones de arquitectura, trabajo de varias horas | El más capaz. No es el default en ningún plan. En algunos planes se cobra con *usage credits* |
| `opus` | Razonamiento complejo y trabajo diario exigente | El default en Pro, Max, Team, Enterprise y API |
| `sonnet` | Programación del día a día | Más barato que Opus |
| `haiku` | Tareas simples y rápidas | El más rápido y barato |
| `opusplan` | Opus mientras planifica, Sonnet al ejecutar | Combina buen plan con ejecución barata |
| `best` | Fable si lo tenés disponible; si no, Opus | |
| `default` | Vuelve al modelo por defecto de tu cuenta | Borra cualquier override |

Los alias apuntan a la versión recomendada y se actualizan solos. **Dependen del proveedor**: con la API de Anthropic, `opus` y `sonnet` son Opus 5.5 y Sonnet 5.5; en Google Cloud's Agent Platform, `sonnet` todavía apunta a Sonnet 4.5. Para fijar una versión usá el nombre completo (ej. `claude-opus-5-5`).

## Cambiar de modelo

| Dónde | Cómo | Alcance |
|---|---|---|
| En la sesión | `/model` (abre el selector) o `/model sonnet` | Cambia ya y **lo guarda como default** |
| En el selector | `s` sobre una fila | Solo esta sesión |
| Al lanzar | `claude --model opus` | Esta sesión |
| Variable de entorno | `ANTHROPIC_MODEL=sonnet` | Mientras esté seteada |
| Settings | `"model": "opus"` en `settings.json` | Permanente |
| Atajo | `Option+P` (macOS) / `Alt+P` | Cambia sin borrar lo que estabas escribiendo |

Para ver qué modelo estás usando: `/status`, o mostralo en la status line (ver [Contexto](05-contexto.md#monitorear-con-la-status-line)).

## Esfuerzo (`/effort`)

El esfuerzo controla cuánto razona el modelo en cada paso. Más esfuerzo = más tokens y más tiempo, pero prueba más casos borde y verifica más.

| Nivel | Cuándo |
|---|---|
| `low` | Cambios chicos que vas revisando uno por uno: renombrar, un primer borrador, brainstorming |
| `medium` | Default en Opus 5.5 y Sonnet 5.5. Trabajo diario con alcance claro |
| `high` | Cuando importa verificar o hay casos borde: arreglar un bug en código existente |
| `xhigh` | Razonamiento más profundo, más gasto |
| `max` | Problemas difíciles que querés que resuelva solo. Puede "sobrepensar": probalo antes de adoptarlo |

```text
/effort            # abre el slider
/effort high       # lo fija y lo guarda como default para este modelo
/effort auto       # vuelve al default del modelo
```

También: `claude --effort high` al lanzar, o las flechas izquierda/derecha dentro de `/model`. `max` se aplica solo a la sesión actual.

**Para un solo turno**, escribí `ultrathink` en el prompt: pide razonamiento más profundo en ese mensaje sin cambiar el esfuerzo de la sesión. Frases como "think hard" ya **no** son palabras clave: se mandan como texto normal.

## Fast mode

`/fast` (o `Option+O` / `Alt+O`) activa una configuración de Opus hasta 2,5x más rápida, **con mayor costo por token**. Misma calidad, no es otro modelo. Solo funciona en Opus (5.5, 5 y 4.8); en planes de suscripción se cobra con *usage credits*. Mientras está activo ves un `↯` junto al prompt. Conviene activarlo al principio de la sesión, no a mitad.

## Ejemplo: elegir según la tarea

| Tarea | Configuración razonable |
|---|---|
| Agregar `description` a 40 columnas en `schema.yml` | `sonnet` o `haiku`, esfuerzo `low` |
| Implementar un modelo incremental nuevo en dbt con tests | Default (`opus`, `medium`) |
| Bug intermitente en un DAG de Airflow que duplica filas en BigQuery | `opus` con `high`, o `fable` |
| Diseñar la migración de 30 modelos legacy a una arquitectura por capas | `opusplan` o `fable`, empezando en [plan mode](09-plan-mode-y-checkpoints.md) |
| Iterar rápido en vivo sobre una query que estás depurando | `/fast` |

## Trucos y errores comunes

- **Empezá con el default.** Cambiá cuando tengas un motivo: resultados flojos → más esfuerzo; tarea mecánica → menos.
- **Un modelo más grande no compensa un mal prompt.** Contexto claro y una forma de verificar rinden más que subir de modelo.
- **`/model` guarda el default.** Si querés probar un modelo solo para esta sesión, abrí el selector y apretá `s`.
- **Cambiar de modelo a mitad de sesión invalida el prompt cache** (Claude Code puede pedirte confirmación). Si vas a cambiar, mejor al principio.
- **Los subagents heredan el modelo de la sesión**, salvo que su definición fije otro. Si pasás a Opus antes de que delegue búsquedas, esas búsquedas también corren en Opus.
- **Con Fable, describí el resultado, no los pasos.** Está pensado para problemas ambiguos y largos; no hace falta recordarle que verifique.
- **Contexto de 1M tokens**: Sonnet 5.5, Fable y Opus 4.7+ ya corren con context window de 1M en la API de Anthropic, sin elegir variante `[1m]`. Que entre más no significa que convenga llenarlo (ver [Contexto](05-contexto.md)).

## Ver también

- [Contexto](05-contexto.md)
- [Plan mode y checkpoints](09-plan-mode-y-checkpoints.md) — dónde brilla `opusplan`
- [Subagents](11-subagents.md) — fijar un modelo más chico para tareas acotadas
- [Costos](21-costos.md)
