# Fundamentos: LLM, agente y el bucle agéntico

## LLM vs. agente

Un **LLM** (Large Language Model, como los modelos Claude) es, en el fondo, una función que recibe texto y devuelve texto: le das un prompt y te devuelve una continuación. Por sí solo no puede leer un archivo, ejecutar un comando ni saber si lo que escribió es correcto — solo predice qué texto viene después.

Un **agente** es un LLM al que se le da la capacidad de **actuar sobre el mundo real** (leer archivos, correr comandos, buscar en la web, editar código) y de **ver el resultado de esas acciones** para decidir el siguiente paso. Claude Code es un agente: el modelo detrás es el mismo LLM, pero envuelto en un programa que le da `tools` (herramientas) y un ciclo de ejecución.

La diferencia práctica: un chatbot LLM responde una vez y listo. Un agente puede iterar solo — probar algo, ver que falló, corregir, volver a probar — sin que el usuario tenga que copiar y pegar resultados manualmente entre pasos.

## El agentic loop

El **bucle agéntico** (agentic loop) es el mecanismo que convierte a un LLM en agente:

1. El usuario da una instrucción.
2. El modelo decide si puede responder directamente o si necesita usar una **tool** (leer un archivo, correr un comando, buscar código, etc.).
3. Si decide usar una tool, el programa que lo envuelve (Claude Code) **ejecuta esa acción de verdad** y le devuelve el resultado al modelo como parte de la conversación.
4. El modelo lee ese resultado y decide el siguiente paso: usar otra tool, pedir confirmación, o responder al usuario.
5. Se repite desde el paso 2 hasta que la tarea está resuelta.

Ejemplo concreto: pedís "arreglá el bug en el login". El modelo no "sabe" dónde está el bug de entrada — busca el archivo relevante (tool de búsqueda), lo lee (tool de lectura), identifica el problema, lo edita (tool de edición), y opcionalmente corre los tests (tool de ejecución) para confirmar que funcionó. Cada una de esas acciones es una vuelta del loop.

Esto es lo que hace que interactuar con Claude Code se sienta distinto a usar un chat: no es "una pregunta, una respuesta", es una tarea que el agente puede trabajar en varios pasos, con o sin intervención del usuario en el medio (ver [permisos](07-permisos.md) para cuánta intervención pedís).

## Por qué Claude Code es un agente y no un autocompletado

Un autocompletado de código (como el de un IDE tradicional) sugiere la próxima línea o función en base al contexto inmediato del archivo abierto. No explora el repo, no corre comandos, no decide una estrategia de varios pasos: solo completa.

Claude Code, en cambio:

- **Explora el proyecto** antes de actuar (busca archivos, lee código relacionado, entiende convenciones existentes).
- **Ejecuta acciones reales** (correr tests, hacer builds, usar `git`, llamar APIs) y ajusta su plan según el resultado.
- **Mantiene una tarea en curso** a lo largo de múltiples pasos, no solo la línea siguiente.
- **Puede delegar** partes del trabajo en [subagents](09-subagents.md) o seguir procedimientos empaquetados en [skills](08-skills.md).

En otras palabras: el autocompletado optimiza la escritura de código línea por línea; el agente resuelve una tarea de principio a fin, decidiendo por su cuenta qué pasos son necesarios.
