---
name: demo-compare
description: Demo final. Compara Naive RAG, Agentic RAG, GraphRAG (/kg) y OAG sobre la misma pregunta con recall, precisión y coste. Usar cuando se pida /demo-compare o la tabla comparativa.
---

# Demo: comparativa

1. Ejecuta `python demo/compare.py`. Vuelve a lanzar las técnicas deterministas y lee los resultados
   guardados en `data/runs/` (Agentic RAG y las respuestas registradas de Claude).
2. Muestra la tabla tal cual y coméntala en cinco líneas como máximo:
   - recall y precisión de cada técnica frente a la respuesta esperada;
   - coste: tokens de contexto y llamadas LLM al recuperar;
   - qué tipo de resultado da cada una (trozos, pasos, lista de lectura, hechos).
3. Recuerda las limitaciones: una sola pregunta, corpus pequeño, respuesta esperada escrita a mano (es un
   mínimo; un ID extra puede ser correcto). Es una demostración, no una evaluación.
