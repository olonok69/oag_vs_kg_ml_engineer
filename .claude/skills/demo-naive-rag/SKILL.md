---
name: demo-naive-rag
description: Demo paso 1. Responde la pregunta de la demo con Naive RAG (trozos de texto por similitud, sin estructura). Usar cuando se pida /demo-naive-rag o mostrar Naive RAG.
---

# Demo: Naive RAG

Objetivo: mostrar qué recupera un RAG básico y qué le falta. El corpus y la pregunta están en
`data/` (fuera de git). Ver `demo/README.md`.

1. Ejecuta `python demo/naive_rag.py` (opciones: `--k 5`, `--chunk-words 180`, `--embed` si hay
   sentence-transformers). Muestra la salida tal cual.
2. Lee la pregunta de `data/questions.yaml` (campo `pregunta`) y respóndela usando SOLO los trozos que
   ha impreso el script. No abras otros ficheros ni uses lo que sepas del proyecto.
3. Para cada ticket que propongas, cita el trozo `[n]` del que sale. Si un trozo menciona un ticket pero
   no explica por qué importa, dilo.
4. Cierra con dos líneas para la audiencia: qué ha encontrado el método y qué no puede saber (relaciones,
   por qué un ticket importa, qué es ruido).
5. Registra tu respuesta: `python demo/record_answer.py naive_rag "<ids separados por espacios>"`.
