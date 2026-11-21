---
name: demo-compare
description: Demo final. Compara Naive RAG, Agentic RAG, GraphRAG (/kg) y OAG en los dos escenarios de la demo con recall, precisión, F1 y coste. Usar cuando se pida /demo-compare o la tabla comparativa.
---

# Demo: comparativa

1. Ejecuta `python demo/compare.py` (las dos preguntas) o `python demo/compare.py --q <id>` (una). Vuelve
   a lanzar las técnicas deterministas (GraphRAG a uno y dos saltos, OAG con esquema v1 y v2) y lee los
   resultados guardados en `data/runs/<id>/` (Agentic RAG y las respuestas registradas de Claude).
2. Muestra cada tabla tal cual y coméntala en cinco líneas como máximo:
   - recall, precisión y F1 de cada técnica frente a la respuesta esperada;
   - coste: tokens de contexto y llamadas LLM al recuperar;
   - qué tipo de resultado da cada una (trozos, pasos, lista de lectura y temas, hechos).
3. Cierra con dónde gana cada técnica:
   - `letter-end-runin` (reglas sobre un componente modelado): OAG v2 encuentra todo con menos ruido y
     dice por qué cada ticket importa; GraphRAG a dos saltos también lo encuentra todo, pero entre
     muchos más tickets.
   - `comment-memo-landscape` (área que la ontología no modela): GraphRAG descubre el área y la agrupa en
     temas; OAG no devuelve nada.
   - Lección: OAG compensa donde hay reglas estables que alguien puede escribir; GraphRAG, para explorar.
4. Recuerda las limitaciones: dos preguntas, respuesta esperada escrita a mano o por regla (es un mínimo;
   un ID extra puede ser correcto) y OAG v2 corregido después de ver el fallo. Es una demostración, no una
   evaluación.
