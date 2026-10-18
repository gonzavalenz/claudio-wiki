# Agent

> verificado: 2026-10-18 · fuentes: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works), [Best practices](https://code.claude.com/docs/en/best-practices), [Copilot cloud agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)

Un agent es un LLM que usa tools en un loop: decide él mismo qué paso dar y qué tool usar, a partir del feedback del entorno. Un **coding agent** es un agent cuyo entorno es tu repo y tu terminal.

## Cuándo usarlo y cuándo no

- **Workflow**: el LLM y los tools siguen caminos de código predefinidos. Es predecible y barato.
- **Agent**: el LLM dirige su propio proceso. Conviene cuando no se puede saber de antemano cuántos pasos hacen falta.
- Regla: usar la solución más simple que funcione. Si alcanza con una sola llamada o con un workflow fijo, el agent sobra, porque cuesta más y sus errores se acumulan.

## Cómo funciona

```
prompt → [ gather context → take action → verify ] → … → respuesta
                ↑______ tool results ______↓
```

- **Model** razona; **tools** actúan (leer/editar archivos, buscar, ejecutar comandos, web). Sin tools, solo hay texto.
- **Harness**: la capa que rodea al modelo. Le da los tools, administra el contexto y aplica los permisos. Claude Code, Copilot y Gemini CLI son harnesses.
- **Loop**: cada tool result vuelve al modelo como dato real del entorno ("ground truth"). El loop corta cuando la tarea termina, cuando se llega a un límite o cuando hace falta pedirle algo al humano.
- **Por qué el código es un dominio ideal**: es verificable. Tests, builds y linters le dan al agent una señal objetiva de si está avanzando.

## En Claude Code

- **Interrumpir**: `Esc` corta la acción en curso. Si escribís y das `Enter` mientras trabaja, el mensaje se encola. `Esc Esc` o `/rewind` vuelven a un checkpoint.
- **Permission modes**: se rotan con `Shift+Tab`. Ver [tools-and-permissions](tools-and-permissions.md).
- **Sesiones**: `claude --continue` / `--resume` retoman una sesión; `/branch` la bifurca.
- **Cerrar el loop de verificación**: pedir el check en el mismo prompt, usar `/goal`, un Stop [hook](hooks.md) o un [subagent](subagents.md) revisor.

## En otras herramientas

- **Copilot**: el cloud agent trabaja en segundo plano, en un entorno efímero: implementa, corre tests y abre un PR. Se configura con `copilot-setup-steps.yml`. `no probado`

## Errores comunes

- **No darle cómo verificar**: si no hay un check, "parece hecho" es la única señal, y el loop de verificación terminás siendo vos.
- **Exploración sin límite**: "investigá el proyecto" sin acotar termina en cientos de archivos leídos y el [contexto](context.md) lleno.
- **Microgestionar**: dictarle cada paso. Lo que hay que darle es el objetivo, el contexto y cómo se verifica el resultado.
- **Usar un agent donde alcanza un script.**

## Ver también

[context](context.md) · [tools-and-permissions](tools-and-permissions.md) · [subagents](subagents.md)
