---
name: demo-agentic-rag
description: Demo paso 2. Responde la pregunta de la demo con Agentic RAG, buscando y leyendo el corpus en bucle con Grep/Read. Usar cuando se pida /demo-agentic-rag o mostrar Agentic RAG.
---

# Demo: Agentic RAG

Objetivo: mostrar a Claude recuperando por sí mismo (planificar, buscar, leer, volver a buscar) y lo
que cuesta. Ver `demo/README.md`.

Reglas:
- Solo puedes leer ficheros de `data/corpus/`. Nada de `data/kg/`, `data/oag/`, `data/runs/` ni
  `data/questions.yaml` salvo el campo `pregunta`.
- No leas los ficheros de `holdout_files` de `data/questions.yaml`: son la hoja de respuestas.
- Máximo 12 llamadas a herramientas de búsqueda o lectura. Cuéntalas.

Pasos:
1. Lee el campo `pregunta` de `data/questions.yaml` y di en una línea tu plan de búsqueda.
2. Busca con Grep y lee con Read (por rangos, no ficheros enteros si son grandes). Narra cada paso en una
   línea: qué buscas y qué has aprendido.
3. Responde: tickets e invariantes a respetar, cada uno con fichero y línea de donde sale.
4. Registra el resultado: `python demo/record_answer.py agentic_rag "<ids>" --tool-calls <n> --tokens <aprox. tokens leídos>`.
5. Cierra con dos líneas: qué ha ganado frente a Naive RAG y qué ha costado (pasos, tokens, variabilidad
   entre ejecuciones).
