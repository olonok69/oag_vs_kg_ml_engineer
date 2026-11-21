---
name: demo-agentic-rag
description: Demo paso 2. Responde la pregunta de la demo con Agentic RAG, buscando y leyendo el corpus en bucle con Grep/Read. Usar cuando se pida /demo-agentic-rag o mostrar Agentic RAG.
---

# Demo: Agentic RAG

Pregunta: la demo tiene dos escenarios en `data/questions.yaml` (`letter-end-runin`, donde se espera
que gane OAG, y `comment-memo-landscape`, donde se espera que gane GraphRAG). Si la skill se invoca con
un id (por ejemplo `/demo-agentic-rag comment-memo-landscape`), añade `--q <id>` a todos los comandos; si no, se
usa la pregunta por defecto.

Objetivo: mostrar a Claude recuperando por sí mismo (planificar, buscar, leer, volver a buscar) y lo
que cuesta. Ver `demo/README.md`.

Reglas:
- Solo puedes leer ficheros de `data/corpus/`. Nada de `data/kg/`, `data/oag/`, `data/runs/` ni
  `data/questions.yaml` salvo los campos `pregunta` y `scenario` de la pregunta elegida.
- No leas los ficheros de `holdout_files` de `data/questions.yaml`: son la hoja de respuestas.
- Máximo 12 llamadas a herramientas de búsqueda o lectura. Cuéntalas.

Pasos:
1. Lee el campo `pregunta` de la pregunta elegida y di en una línea tu plan de búsqueda.
2. Busca con Grep y lee con Read (por rangos, no ficheros enteros si son grandes). Narra cada paso en una
   línea: qué buscas y qué has aprendido.
3. Responde: tickets e invariantes a respetar, cada uno con fichero y línea de donde sale.
4. Registra el resultado: `python demo/record_answer.py agentic_rag "<ids>" --tool-calls <n> --tokens <aprox. tokens leídos>`.
5. Cierra con dos líneas: qué ha ganado frente a Naive RAG y qué ha costado (pasos, tokens, variabilidad
   entre ejecuciones).
