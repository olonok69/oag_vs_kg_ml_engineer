# Demo: de Naive RAG a OAG sobre la memoria de tickets

Cuatro técnicas de recuperación responden a las mismas preguntas reales sobre el mismo corpus, y una
quinta skill las compara. Cada técnica es una skill de Claude Code que se ejecuta en directo.

La demo tiene dos escenarios, elegidos para enseñar dónde gana cada técnica:

| Id | Escenario | Se espera que gane |
|---|---|---|
| `letter-end-runin` | Pregunta de reglas sobre un componente modelado: qué tickets e invariantes no romper al arreglar un bug | OAG |
| `comment-memo-landscape` | Pregunta exploratoria sobre un área que la ontología no modela: qué tickets tratan de ella y en qué temas se agrupan | GraphRAG |

Las dos preguntas tienen además una versión en castellano llano, sin nombres de código (`--lang es`), para
ver qué pasa cuando el corpus está en inglés y la pregunta no: sin capa semántica fallan las tres técnicas
deterministas; con ella (embeddings multilingües o sinónimos en castellano en la ontología) se recuperan
en distinta medida.

| Skill | Técnica | Qué recupera | Script |
|---|---|---|---|
| `/demo-naive-rag` | Naive RAG | Trozos de texto por similitud (TF-IDF; `--embed` para embeddings multilingües) | `demo/naive_rag.py` |
| `/demo-agentic-rag` | Agentic RAG | Claude busca y lee en bucle con Grep/Read | (Claude) + `demo/record_answer.py` |
| `/demo-graphrag` | GraphRAG | Nuestro skill `/kg`: vecinos en el grafo de tickets y lista de lectura | `demo/graphrag.py` |
| `/demo-oag` | OAG | Hechos tipados, validados contra `demo/oag/ontology.yaml`, seleccionados por set cover | `demo/oag.py` |
| `/demo-compare` | Comparativa | Recall, precisión, F1, tokens de contexto y llamadas LLM, por escenario e idioma | `demo/compare.py` |
| (todas) | Capa semántica | Embeddings multilingües compartidos por las tres técnicas deterministas | `demo/semantic.py` |

Todas las skills y scripts aceptan el id de la pregunta (`/demo-oag comment-memo-landscape`,
`python demo/oag.py query --q comment-memo-landscape`); sin id se usa la pregunta por defecto.

Qué ejecuta cada paso, función por función: [`docs/GUIA_TECNICA.md`](../docs/GUIA_TECNICA.md)
(EN: [`docs/TECHNICAL_GUIDE.md`](../docs/TECHNICAL_GUIDE.md)).

`/demo-graphrag` no es una implementación nueva: es la consulta que hace `/kg` (`kg_query.sh <tema>`,
equivalente a `graphify explain`) sobre el `graph.json` que construye `/kg-refresh` en el repo lambda.
El script la reproduce en Python para poder aplicar el hold-out y limitarla al corpus de la demo;
`--native` llama a `kg_query.sh` directamente si graphify está instalado.

## Datos

Todo lo que viene del proyecto real vive en `data/`, que está en `.gitignore`. Nada de `data/` se sube
a GitHub.

```
data/
  corpus/*.md            ficheros del corpus de kg (copia de document-parser-lambda/data/knowledge-graph/_corpus)
  kg/output/graph.json   grafo de tickets construido por /kg-refresh (document-parser-lambda/data/knowledge-graph/output)
  kg/output/community_labels.json   nombres de las comunidades del grafo (temas), de /kg-refresh
  kg/kg_query.sh         wrapper de /kg, solo para --native
  questions.yaml         preguntas, respuestas esperadas y hold-out (plantilla: demo/questions.example.yaml)
  oag/<id>/facts.json    hechos generados por `oag.py build --q <id>`
  runs/<id>/*.json       resultados de cada técnica; runs/compare.md con las tablas
  cache/embeddings/      embeddings del corpus y del grafo (capa semántica), se regeneran solos
```

El corpus es el `_corpus/` completo de `/kg` (452 ficheros tras el hold-out). Tras actualizarlo hay que
volver a ejecutar `python demo/oag.py build --q <id>` para cada pregunta. Los scripts no dependen del
número de ficheros.

## Las preguntas y las respuestas esperadas

**`letter-end-runin`** es un bug real ya investigado. Su writeup contiene una sección de "do-not-break" y una
batería de regresión escritas por quien lo resolvió: esa es la respuesta esperada. El writeup y las
notas que lo resumen se declaran como `holdout` en `questions.yaml` y se excluyen de todas las técnicas
(corpus, grafo y hechos), de modo que la pregunta se responde como si el bug fuera nuevo.

**`comment-memo-landscape`** es la pregunta de quien entra en un área que no conoce. La respuesta esperada
sale de una regla objetiva, no de una lista elegida a mano: todos los writeups de tickets cuyo título
menciona el área. No hay hold-out, porque no hay una hoja de respuestas que esconder.

Métricas, contra la respuesta esperada:

- **F1**: media armónica de recall y precisión; resume las dos en un número.

- **Recall**: proporción de tickets esperados que aparecen en el resultado.
- **Precisión**: proporción del resultado que está en la respuesta esperada. La lista esperada es un
  mínimo, no un techo: un ticket extra puede ser correcto.
- **Naive RAG y GraphRAG** se puntúan por los tickets que aparecen en el contexto que devuelven, porque no
  afirman nada sobre ellos. **OAG** se puntúa por el sujeto de cada fact block y los orígenes de sus
  invariantes; los tickets que solo aparecen como procedencia ("quién lo dijo") no cuentan.
- **Recall de la respuesta de Claude**: lo que Claude contesta tras leer ese contexto, registrado con
  `record_answer.py`. Es lo que de verdad compara las técnicas, y varía entre ejecuciones.

## Cómo ejecutarla

Entorno con [uv](https://docs.astral.sh/uv/) (WSL Ubuntu o Linux; el `pyproject.toml` está en la raíz):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # si no está uv
sudo apt install -y libcairo2                     # solo para regenerar los PNG de los diagramas
uv sync                                           # crea .venv con la demo y el deck
uv sync --group embed                             # opcional: capa semántica (torch CPU y el modelo multilingüe)
source .venv/bin/activate                         # antes de lanzar claude, para que `python` sea el del venv
python demo/oag.py build          # una vez, o tras cambiar el corpus o la ontología
```

Sin uv: `pip install -r demo/requirements.txt`.

Y una vez por pregunta: `python demo/oag.py build --q letter-end-runin` y
`python demo/oag.py build --q comment-memo-landscape`.

En Claude Code, primer escenario: `/demo-naive-rag`, `/demo-agentic-rag`, `/demo-graphrag`, `/demo-oag`.
Segundo escenario: `/demo-graphrag comment-memo-landscape` y `/demo-oag comment-memo-landscape` (y, si hay
tiempo, `/demo-naive-rag comment-memo-landscape`). Al final, `/demo-compare`. Cada skill ejecuta su
script, responde usando solo lo que ha recuperado y registra la respuesta.

Los scripts también funcionan sin Claude Code:

```bash
python demo/naive_rag.py [--q <id>] [--k 5] [--embed] [--lang es]
python demo/graphrag.py [--q <id>] [--hops 2] [--lang es] [--semantic] [--full] [--native]
python demo/oag.py query [--q <id>] [--schema 1|2|3] [--lang es] [--semantic] [--min-sim 0.42]
python demo/compare.py [--q <id>]
```

La capa semántica necesita el grupo `embed` y, la primera vez, acceso a huggingface.co y a su CDN
(`*.hf.co`) para descargar `paraphrase-multilingual-MiniLM-L12-v2` (unos 470 MB). Después funciona sin
red (`HF_HUB_OFFLINE=1`). Para usar otro modelo: `--model <nombre>` o `DEMO_EMBED_MODEL`.

## Qué muestra cada paso

1. **Naive RAG.** Recupera trozos que se parecen a la pregunta. Encuentra los términos, pero no distingue
   un ticket relevante de uno que solo aparece en el mismo párrafo, y no sabe por qué importa ninguno.
2. **Agentic RAG.** Claude planifica y vuelve a buscar. Mejora la precisión a cambio de pasos, tokens y
   resultados que cambian entre ejecuciones.
3. **GraphRAG (/kg).** Consulta determinista y barata, sin LLM. Devuelve vecinos y una lista de lectura,
   pero la mayoría de las aristas son genéricas (`references`, `conceptually_related_to`): dice qué leer,
   no qué hecho aporta cada fichero. Más saltos suben el recall y bajan la precisión. Agrupa el resultado
   en temas con las comunidades con nombre del grafo, sin que nadie haya modelado el área antes.
4. **OAG.** La ontología se escribe antes: clases, relaciones, componentes con sus sinónimos y reglas.
   La extracción solo puede producir lo que el esquema permite, y la validación rechaza el resto
   (las menciones genéricas entre tickets). La pregunta se mapea a un componente y el set cover devuelve
   el mínimo de hechos que la cubren, cada uno con su fuente.
5. **De OAG v1 a v2.** La primera ontología fallaba de dos formas: traía tickets "no romper" de otras
   áreas (numeración, PDF) y no veía un invariante de detección de títulos que el fin de carta usa. La v2
   añade una restricción (el ticket protegido debe compartir componente) y una relación `calls` entre
   componentes. `--schema 1` reproduce la v1. Es evolución del esquema, escrita después de ver el fallo.
6. **Pregunta en castellano llano (`--lang es`).** Las tres técnicas deterministas comparan palabras y el
   corpus está en inglés: sin capa semántica no encuentran nada. Con ella, cada una usa embeddings
   multilingües solo en el primer paso: Naive RAG ordena los trozos por significado, GraphRAG elige la
   semilla por similitud y OAG elige los componentes por similitud (`--semantic`). La v3 de la ontología
   es la alternativa sin modelo: sinónimos en castellano para cada componente (`--schema 3`).

## Limitaciones

- Dos preguntas: es una demostración, no una evaluación. El Paso 0 del `HANDOVER.md` (15 a 20
  preguntas) es la evaluación.
- OAG v2 se escribió después de ver qué fallaba en la primera pregunta. Hay que validarlo con preguntas
  nuevas antes de atribuirle el resultado.
- Con pocos documentos, Naive RAG lo tiene fácil, sobre todo si entra un hub como `SHARP_EDGES`, que ya es
  un índice escrito a mano. Con el corpus completo (452 ficheros) su recall baja del 100 % al 71 % (ver
  `docs/GUIA_DEMO.md`, sección 6).
- La extracción de OAG es determinista (frontmatter, tablas, citas y sinónimos). En producción se
  completaría con extracción guiada por LLM (Fase C), siempre validada contra la misma ontología.
- Los componentes y sinónimos de la ontología están escritos a mano para este dominio. Ese es el precio
  de OAG y el principal riesgo de mantenimiento.
- El umbral de similitud de OAG (`--min-sim 0.42`) está calibrado con las dos preguntas de la demo. Con
  más preguntas habría que fijarlo con preguntas no vistas.
