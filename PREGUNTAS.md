# Preguntas abiertas

Respondé debajo de cada una. Mi recomendación va entre paréntesis.

## 1. Formato de los diagramas

`DESIGN.md` dice Excalidraw, pero los diagramas que tiene sentido hacer acá son de flujo: el agentic loop, el ciclo de hooks, orchestrator-workers, la jerarquía de memory. Para ese tipo de diagrama, Excalidraw tiene costos:

- El archivo editable (`.excalidraw`) es un JSON que no se lee bien en un diff ni lo mantiene bien un agente. GitHub no lo muestra.
- Para verlo en el `.md` y en `site/` hay que exportarlo a mano a SVG desde VS Code, cada vez que se cambia. Es fácil que la fuente y la imagen se desincronicen.
- No puedo exportarlo yo desde la terminal sin sumar Node y librerías.

Opciones:

- a) **Mermaid** dentro del `.md`: es texto, se lee bien en un diff, GitHub lo muestra solo y un agente lo edita sin problema. Contra: menos control visual (le aplico el tema oscuro con acento rojo) y en `site/` se necesita la librería JS de Mermaid (una copia local, sin CDN).
- b) **Excalidraw** como dice `DESIGN.md`: yo escribo el `.excalidraw` y vos exportás el SVG desde VS Code.
- c) **Mixto**: Mermaid para los flujos y Excalidraw solo para ilustraciones conceptuales donde el dibujo aporte.

(Recomiendo **c**, empezando solo con Mermaid: hoy no hay ningún diagrama que necesite Excalidraw.)

Respuesta:
