# Permisos: cuánta autonomía le das

Claude Code puede ejecutar acciones reales (correr comandos, editar archivos, hacer commits, llamar APIs externas). El sistema de permisos es lo que decide **qué puede hacer solo y qué necesita tu aprobación explícita** antes de ejecutarse.

## Cómo funciona en la práctica

Cuando el agente quiere usar una herramienta que no está explícitamente permitida por la configuración, se te muestra un prompt de confirmación antes de ejecutarla. Vos podés aprobar esa acción puntual, o (según el modo) aprobarla para el resto de la sesión.

Esto aplica sobre todo a:

- Comandos de shell (`Bash`) — sobre todo los que modifican estado: instalar paquetes, `git push`, borrar archivos, etc.
- Escritura/edición de archivos fuera del árbol del proyecto.
- Llamadas a herramientas que interactúan con sistemas externos (APIs, servicios de terceros).

Lo que **no** suele requerir confirmación: lectura de archivos, búsquedas en el repo, comandos de solo lectura (`git status`, `git diff`, `ls`) — porque no tienen efectos secundarios que revertir.

## Configurar allowlist / denylist

Los permisos se configuran en `settings.json` (compartido, versionado con el repo) o `settings.local.json` (personal, no se versiona — ver [`.gitignore`](../.gitignore) de este mismo repo, que ya excluye ese archivo). Ahí se puede definir, por ejemplo, qué comandos de `Bash` quedan pre-aprobados sin preguntar:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff)",
      "Bash(npm test)"
    ]
  }
}
```

También existe la skill `fewer-permission-prompts`, que escanea qué comandos de solo lectura se repiten mucho en una sesión y arma automáticamente una allowlist sugerida para `settings.json` — útil para no tener que armar la lista a mano.

## Acciones que siempre conviene confirmar

Independientemente del modo de permisos configurado, hay una categoría de acciones que por su **impacto y dificultad de reversión** ameritan confirmación explícita en vez de autonomía total:

- Operaciones destructivas: borrar archivos/branches, `rm -rf`, sobreescribir cambios sin commitear.
- Operaciones difíciles de revertir: `git push --force`, `git reset --hard`, hacer `amend` de commits ya publicados, bajar la versión de una dependencia.
- Acciones visibles para otros o que afectan estado compartido: pushear código, crear/cerrar PRs o issues, mandar mensajes (Slack, email), tocar infraestructura compartida.
- Saltear controles de seguridad: `--no-verify`, `--no-gpg-sign`, deshabilitar hooks de pre-commit.

La lógica no es "nunca hacer esto", sino que el costo de confirmar antes es bajo y el costo de una acción no deseada (trabajo perdido, un force-push que pisa el remoto, un mensaje mandado de más) puede ser alto. Que hayas aprobado una acción de este tipo una vez no significa que quede aprobada para siempre — la autorización es por alcance, no un cheque en blanco.

## Cuándo conviene un modo más restrictivo vs. más autónomo

- **Más restrictivo** (confirmar casi todo): recomendable al empezar a trabajar en un repo nuevo, en repos de producción críticos, o cuando el resultado de una acción es difícil de predecir de antemano.
- **Más autónomo** (allowlist amplia, menos interrupciones): tiene sentido en tareas repetitivas y de bajo riesgo (lectura, exploración, tests en un entorno descartable), o cuando ya conocés bien el comportamiento del agente en ese proyecto puntual y confiás en el patrón de acciones que toma.

La recomendación general es ir ampliando la autonomía a medida que se genera confianza en un proyecto/tarea específica, no partir de máxima autonomía por defecto.
