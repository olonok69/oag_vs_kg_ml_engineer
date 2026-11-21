---
name: demo-graphrag
description: Demo paso 3. Responde la pregunta de la demo con GraphRAG, que es nuestro skill /kg (graphify explain sobre el grafo de tickets). Usar cuando se pida /demo-graphrag o mostrar GraphRAG.
---

# Demo: GraphRAG (nuestro /kg)

Pregunta: la demo tiene dos escenarios en `data/questions.yaml` (`letter-end-runin`, donde se espera
que gane OAG, y `comment-memo-landscape`, donde se espera que gane GraphRAG). Si la skill se invoca con
un id (por ejemplo `/demo-graphrag comment-memo-landscape`), añade `--q <id>` a todos los comandos; si no, se
usa la pregunta por defecto. Si se pide en castellano (`--lang es`, por ejemplo
`/demo-graphrag letter-end-runin --lang es`), añade `--lang es`: los scripts usan entonces `pregunta_llana`
(la pregunta en castellano llano, sin nombres de código) en lugar de la versión en inglés.

Este paso es el skill `/kg` que ya usamos en el repo lambda: la misma consulta que
`kg_query.sh <tema>` (vecinos de un nodo en `graph.json`, con relación y confianza, y la lista de
ficheros a leer). Aquí se ejecuta en Python puro para aplicar el hold-out y limitarlo al corpus de la
demo. Ver `demo/README.md`.

1. Ejecuta `python demo/graphrag.py` (opciones: `--q <id>`, `--topic <tema>`, `--hops 2`, `--full` para el grafo
   completo, `--native` para llamar a `kg_query.sh` si graphify está instalado).
2. Explica el resultado en tres líneas: semilla, qué tipos de arista salen y cuántas son genéricas
   (`references`, `conceptually_related_to`), y los temas (comunidades con nombre) que agrupan el resultado.
3. Responde la pregunta elegida usando SOLO la salida del script. El grafo da una lista
   de lectura: di qué tickets propones y cuáles solo sabes que "están relacionados" sin saber por qué.
4. Si quieres enseñar el coste de ampliar, repite con `--hops 2` y compara recall y precisión.
   Con `--lang es` el tema está en castellano (`tema`) y la semilla por nombre no encuentra ningún nodo.
   Repite con `--semantic` (semilla por similitud, necesita `uv sync --group embed`) y enseña los
   candidatos con su similitud: el modelo encuentra la zona, pero no siempre el nodo central que elegiría
   alguien que conoce el dominio.
5. Registra tu respuesta: `python demo/record_answer.py graphrag "<ids>"`.
6. En `comment-memo-landscape` el área no está en la ontología de OAG: subraya que el grafo la descubre
   sin que nadie la haya modelado y que las comunidades responden a "en qué temas se agrupan".
