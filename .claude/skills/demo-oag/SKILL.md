---
name: demo-oag
description: Demo paso 4. Responde la pregunta de la demo con OAG, hechos tipados extraídos y validados contra una ontología mínima. Usar cuando se pida /demo-oag o mostrar OAG.
argument-hint: "[letter-end-runin | comment-memo-landscape] [--lang es]"
---

# Demo: OAG (Ontology-Augmented Generation)

Cómo ejecutar los scripts: desde la raíz del repo, con el venv activo, exactamente `python demo/<script>.py ...`,
sin `cd`, sin encadenar comandos con `&&` y sin rutas a `.venv`. Así una sola aprobación («no volver a
preguntar» para `python demo/...`) cubre toda la demo. Si `python` no existe, el venv no está activo: dilo y
para, en lugar de probar otras rutas.

Pregunta: la demo tiene dos escenarios en `data/questions.yaml` (`letter-end-runin`, donde se espera
que gane OAG, y `comment-memo-landscape`, donde se espera que gane GraphRAG). Si la skill se invoca con
un id (por ejemplo `/demo-oag comment-memo-landscape`), añade `--q <id>` a todos los comandos; si no, se
usa la pregunta por defecto. Si se pide en castellano (`--lang es`, por ejemplo
`/demo-oag letter-end-runin --lang es`), añade `--lang es`: los scripts usan entonces `pregunta_llana`
(la pregunta en castellano llano, sin nombres de código) en lugar de la versión en inglés.

Objetivo: mostrar la diferencia de definir el esquema antes (schema-first). Ver `demo/README.md` y
`demo/oag/ontology.yaml`.

1. Enseña la ontología: `demo/oag/ontology.yaml`. Resume en cuatro líneas clases, relaciones, componentes
   con sus sinónimos (altLabels, y en castellano desde v3) y reglas de extracción.
2. Construye los hechos: `python demo/oag.py build`. Comenta el informe: hechos por relación y, sobre
   todo, lo rechazado por la validación (relaciones que no están en el esquema).
3. Consulta con la primera ontología y con la corregida: `python demo/oag.py query --schema 1` y
   `python demo/oag.py query`. Explica cómo la pregunta se mapea a un componente, cómo el set cover elige
   el mínimo de fact blocks y qué ha cambiado de v1 a v2: la restricción que exige que un ticket
   "no romper" comparta componente (quita ruido) y la relación `calls` (fin de carta llama a
   `get_titles`), que recupera el invariante que faltaba. Di que v2 se escribió después de ver el fallo:
   es evolución del esquema, y se valida con más preguntas.
4. Responde la pregunta elegida usando SOLO los fact blocks. Para cada ticket di el hecho
   (qué invariante origina, quién lo nombra como "no romper", qué test lo fija) y su fuente.
5. Registra tu respuesta: `python demo/record_answer.py oag "<ids>"`.
6. Cierra con dos líneas: qué aporta frente a /kg y cuál es el precio (escribir y mantener la ontología).
7. Con `--lang es`: la consulta con v2 no reconoce ningún componente (las etiquetas están en inglés).
   Repite con `--schema 3` (sinónimos en castellano escritos en la ontología) y con `--semantic`
   (componentes por similitud con un modelo multilingüe, umbral 0,42 calibrado con las dos preguntas).
   Subraya que el idioma solo afecta al primer paso: una vez reconocido el componente, los hechos son
   los mismos que en inglés.
8. En `comment-memo-landscape` la pregunta no menciona ningún componente de la ontología y OAG no
   devuelve nada. No lo disimules: es el límite de la técnica (solo ve lo que el esquema declara).
