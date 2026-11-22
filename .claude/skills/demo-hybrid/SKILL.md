---
name: demo-hybrid
description: Demo paso 5. Responde la pregunta de la demo con el híbrido GraphRAG + OAG, en el que GraphRAG propone y la ontología filtra cuando la pregunta cae en ella. Usar cuando se pida /demo-hybrid o combinar GraphRAG y OAG.
argument-hint: "[letter-end-runin | comment-memo-landscape] [--lang es]"
---

# Demo: híbrido GraphRAG + OAG

Cómo ejecutar los scripts: desde la raíz del repo, con el venv activo, exactamente `python demo/<script>.py ...`,
sin `cd`, sin encadenar comandos con `&&` y sin rutas a `.venv`. Así una sola aprobación («no volver a
preguntar» para `python demo/...`) cubre toda la demo. Si `python` no existe, el venv no está activo: dilo y
para, en lugar de probar otras rutas.

Pregunta: si la skill se invoca con un id (por ejemplo `/demo-hybrid comment-memo-landscape`), añade
`--q <id>` al comando; si no, se usa la pregunta por defecto. Con `--lang es` añade `--lang es --semantic`
(la pregunta en castellano llano, con la capa semántica para la semilla del grafo y los componentes).

Objetivo: mostrar qué se gana y qué no al combinar las dos técnicas. Ver `demo/hybrid.py`.

1. Ejecuta `python demo/hybrid.py` (con `--q <id>` si toca). El script lanza GraphRAG a 2 saltos y la
   consulta de OAG v2 y combina sus resultados; no llama a ningún LLM.
2. Explica la ruta que ha tomado:
   - Si la pregunta nombra un componente de la ontología: el embudo. Candidatos del grafo, los que se
     conectan al componente en la ontología (clases y relaciones) y los que cumplen sus reglas
     (restricción de mismo componente y `calls`). Di cuántos tickets añade la ontología que el grafo no
     propuso (en la pregunta A, ninguno).
   - Si no nombra ninguno: la respuesta es la lista de GraphRAG sin filtrar, y las comunidades del grafo
     salen como propuesta para ampliar la ontología. Subraya que la propuesta la revisa una persona.
3. Responde la pregunta usando SOLO los tickets y fuentes que ha devuelto el script.
4. Registra tu respuesta: `python demo/record_answer.py hybrid "<ids>"`.
5. Cierra con dos líneas, sin exagerar: el híbrido iguala a la mejor técnica en cada pregunta, no la
   supera; lo que aporta es no tener que elegir y una lista de qué modelar después. Su punto débil es
   decidir si la pregunta cae en la ontología: una pregunta de exploración que nombre un componente se
   filtraría por error.
