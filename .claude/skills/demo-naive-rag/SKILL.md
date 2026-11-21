---
name: demo-naive-rag
description: Demo paso 1. Responde la pregunta de la demo con Naive RAG (trozos de texto por similitud, sin estructura). Usar cuando se pida /demo-naive-rag o mostrar Naive RAG.
argument-hint: "[letter-end-runin | comment-memo-landscape] [--lang es]"
---

# Demo: Naive RAG

Cómo ejecutar los scripts: desde la raíz del repo, con el venv activo, exactamente `python demo/<script>.py ...`,
sin `cd`, sin encadenar comandos con `&&` y sin rutas a `.venv`. Así una sola aprobación («no volver a
preguntar» para `python demo/...`) cubre toda la demo. Si `python` no existe, el venv no está activo: dilo y
para, en lugar de probar otras rutas.

Pregunta: la demo tiene dos escenarios en `data/questions.yaml` (`letter-end-runin`, donde se espera
que gane OAG, y `comment-memo-landscape`, donde se espera que gane GraphRAG). Si la skill se invoca con
un id (por ejemplo `/demo-naive-rag comment-memo-landscape`), añade `--q <id>` a todos los comandos; si no, se
usa la pregunta por defecto. Si se pide en castellano (`--lang es`, por ejemplo
`/demo-naive-rag letter-end-runin --lang es`), añade `--lang es`: los scripts usan entonces `pregunta_llana`
(la pregunta en castellano llano, sin nombres de código) en lugar de la versión en inglés.

Objetivo: mostrar qué recupera un RAG básico y qué le falta. El corpus y la pregunta están en
`data/` (fuera de git). Ver `demo/README.md`.

1. Ejecuta `python demo/naive_rag.py` (opciones: `--k 5`, `--chunk-words 180`, `--embed` para usar
   embeddings multilingües en lugar de TF-IDF, que necesita `uv sync --group embed`). Muestra la salida
   tal cual. Con `--lang es`, enseña primero TF-IDF y luego `--embed`: sin embeddings, una pregunta en
   castellano casi no comparte palabras con un corpus en inglés.
2. Lee el campo `pregunta` (o `pregunta_llana` con `--lang es`) de la pregunta elegida en `data/questions.yaml` y respóndela usando SOLO los trozos que
   ha impreso el script. No abras otros ficheros ni uses lo que sepas del proyecto.
3. Para cada ticket que propongas, cita el trozo `[n]` del que sale. Si un trozo menciona un ticket pero
   no explica por qué importa, dilo.
4. Cierra con dos líneas para la audiencia: qué ha encontrado el método y qué no puede saber (relaciones,
   por qué un ticket importa, qué es ruido).
5. Registra tu respuesta: `python demo/record_answer.py naive_rag "<ids separados por espacios>"` (con
   variantes, la clave que imprime el script: `naive_rag_es`, `naive_rag_es_sem`...).
