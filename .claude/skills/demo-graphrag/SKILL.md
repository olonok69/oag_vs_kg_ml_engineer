---
name: demo-graphrag
description: Demo paso 3. Responde la pregunta de la demo con GraphRAG, que es nuestro skill /kg (graphify explain sobre el grafo de tickets). Usar cuando se pida /demo-graphrag o mostrar GraphRAG.
---

# Demo: GraphRAG (nuestro /kg)

Este paso es el skill `/kg` que ya usamos en el repo lambda: la misma consulta que
`kg_query.sh <tema>` (vecinos de un nodo en `graph.json`, con relación y confianza, y la lista de
ficheros a leer). Aquí se ejecuta en Python puro para aplicar el hold-out y limitarlo al corpus de la
demo. Ver `demo/README.md`.

1. Ejecuta `python demo/graphrag.py` (opciones: `--topic <tema>`, `--hops 2`, `--full` para el grafo
   completo, `--native` para llamar a `kg_query.sh` si graphify está instalado).
2. Explica el resultado en tres líneas: semilla, qué tipos de arista salen y cuántas son genéricas
   (`references`, `conceptually_related_to`).
3. Responde la pregunta de `data/questions.yaml` usando SOLO la salida del script. El grafo da una lista
   de lectura: di qué tickets propones y cuáles solo sabes que "están relacionados" sin saber por qué.
4. Si quieres enseñar el coste de ampliar, repite con `--hops 2` y compara recall y precisión.
5. Registra tu respuesta: `python demo/record_answer.py graphrag "<ids>"`.
