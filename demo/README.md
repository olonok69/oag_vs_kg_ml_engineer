# Demo: de Naive RAG a OAG sobre la memoria de tickets

Cinco enfoques de recuperación responden a las mismas preguntas reales sobre el mismo corpus, y una
sexta skill los compara. Cada técnica es una skill de Claude Code que se ejecuta en directo.

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
| `/demo-hybrid` | Híbrido | GraphRAG propone y la ontología filtra si la pregunta cae en ella; si no, lista del grafo y propuesta para la ontología | `demo/hybrid.py` |
| `/demo-compare` | Comparativa | Recall, precisión, F1, tokens de contexto y llamadas LLM, por escenario e idioma | `demo/compare.py` |
| (Naive RAG, GraphRAG, OAG e híbrido) | Capa semántica | Embeddings multilingües; el híbrido transmite la opción a GraphRAG y OAG | `demo/semantic.py` |

Los comandos de recuperación aceptan el id de la pregunta (`/demo-oag comment-memo-landscape`,
`python demo/oag.py query --q comment-memo-landscape`); sin id se usa la pregunta por defecto.

Cómo lanzarla dentro de Claude Code, comando a comando y con lo que debe salir:
[`docs/EJECUTAR_DEMO.md`](../docs/EJECUTAR_DEMO.md) (EN: [`docs/RUN_DEMO.md`](../docs/RUN_DEMO.md)).

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
  holdout/<id>/          vista del corpus sin la hoja de respuestas, de `holdout.py --q <id>` (Agentic RAG)
  runs/<id>/*.json       resultados de cada técnica; runs/compare.md con las tablas
  cache/embeddings/      embeddings del corpus y del grafo (capa semántica), se regeneran solos
```

El corpus es el `_corpus/` completo de `/kg` (453 ficheros; 450 en la pregunta A tras el hold-out). Tras actualizarlo hay que
volver a ejecutar `python demo/oag.py build --q <id>` para cada pregunta. Los scripts no dependen del
número de ficheros.

## Las preguntas y las respuestas esperadas

**`letter-end-runin`** es un bug real ya investigado. Su writeup contiene una sección de "do-not-break" y una
batería de regresión escritas por quien lo resolvió: esa es la respuesta esperada. El writeup y las
notas que lo resumen se declaran como `holdout` en `questions.yaml` y se excluyen de todas las técnicas
(corpus, grafo y hechos), de modo que la pregunta se responde como si el bug fuera nuevo. También se excluye
todo lo que deriva del ticket reservado: las notas cuyo título o `tickets:` lo nombran y, en el resto del
corpus, cada pasaje que lo menciona (sección, fila de tabla, viñeta o párrafo). Lo hace `lib.holdout_view`;
`python demo/holdout.py --q <id>` escribe esa vista en `data/holdout/<id>/` para Agentic RAG, que lee con
Grep y Read, y deja en `_holdout_report.json` qué se quitó.

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
uv sync --group embed                             # crea .venv con la demo, el deck y la capa semántica
                                                  # (uv sync a secas deja fuera la capa semántica)
source .venv/bin/activate                         # antes de lanzar claude, para que `python` sea el del venv
claude                                            # Claude Code, desde la raíz del repo
```

Sin uv: `pip install -r demo/requirements.txt`.

Y una vez por pregunta: `python demo/oag.py build --q letter-end-runin` y
`python demo/oag.py build --q comment-memo-landscape`.

Dentro de Claude Code, cada skill se invoca con `/` y su nombre; el id de la pregunta y `--lang es` van detrás
(`/demo-oag comment-memo-landscape`, `/demo-oag letter-end-runin --lang es`). Escribe `/clear` antes de cada
skill. La primera vez que una skill ejecute `python demo/...`, aprueba el comando para todo el proyecto.

Primer escenario: `/demo-naive-rag`, `/demo-agentic-rag`, `/demo-graphrag`, `/demo-oag`.
Segundo escenario: `/demo-graphrag comment-memo-landscape` y `/demo-oag comment-memo-landscape` (y, si hay
tiempo, `/demo-naive-rag comment-memo-landscape`). Después, `/demo-hybrid` en las dos preguntas para
combinar GraphRAG y OAG. Al final, `/demo-compare`. Cada skill ejecuta su
script, responde usando solo lo que ha recuperado y registra la respuesta.

Los scripts también funcionan sin Claude Code:

```bash
python demo/holdout.py [--q <id>]
python demo/naive_rag.py [--q <id>] [--k 5] [--chunk-words 180] [--overlap 30] [--embed] [--model <nombre>] [--lang en|es] [--query "..."] [--quiet]
python demo/graphrag.py [--q <id>] [--topic <tema>] [--hops <n>] [--lang en|es] [--semantic] [--model <nombre>] [--full] [--native] [--quiet]
python demo/oag.py build [--q <id>]
python demo/oag.py query [--q <id>] [--query "..."] [--schema 1|2|3] [--lang en|es] [--semantic] [--min-sim 0.42] [--model <nombre>] [--quiet]
python demo/hybrid.py [--q <id>] [--hops <n>] [--schema 1|2|3] [--lang en|es] [--semantic] [--quiet]
python demo/record_answer.py [--q <id>] <tecnica> "<ids>" [--tool-calls <n>] [--tokens <n>]
python demo/compare.py [--q <id>] [--no-run]
```

La capa semántica necesita el grupo `embed` y, la primera vez, acceso a huggingface.co y a su CDN
(`*.hf.co`) para descargar `paraphrase-multilingual-MiniLM-L12-v2` (unos 470 MB). Después funciona sin
red (`HF_HUB_OFFLINE=1`). Para usar otro modelo: `--model <nombre>` en los comandos compatibles o
`DEMO_EMBED_MODEL`.

## Referencia completa de los scripts

Todos los comandos se lanzan desde la raíz del repositorio. `--q <id>` selecciona una entrada de
`data/questions.yaml`; si se omite, se usa su valor `default` (o `DEMO_Q` si está definida). Los
comandos de recuperación guardan su JSON bajo `data/runs/<id>/`; los detalles de sus algoritmos y
funciones están en [`docs/GUIA_TECNICA.md`](../docs/GUIA_TECNICA.md) y
[`docs/TECHNICAL_GUIDE.md`](../docs/TECHNICAL_GUIDE.md).

| Script | Para qué sirve | Lee | Escribe o efecto |
|---|---|---|---|
| [`holdout.py`](holdout.py) | Prepara la vista que puede leer Agentic RAG, sin la respuesta reservada | Corpus y `questions.yaml` | Sustituye `data/holdout/<id>/` por los Markdown filtrados y `_holdout_report.json` |
| [`naive_rag.py`](naive_rag.py) | Divide el corpus en ventanas y recupera las `k` más similares por TF-IDF o embeddings | Corpus filtrado y texto de pregunta | Imprime chunks y puntuación; guarda `naive_rag*.json` |
| [`graphrag.py`](graphrag.py) | Resuelve una semilla y recorre el grafo por anchura; muestra vecindario, fuentes y comunidades | `graph.json`, corpus, pregunta y, si existe, `community_labels.json` | Imprime contexto y puntuación; guarda `graphrag*.json`. `--native` solo llama a `kg_query.sh` y no guarda una ejecución |
| [`oag.py`](oag.py) | `build` extrae y valida hechos; `query` selecciona fact blocks mediante set cover | Corpus, pregunta y `oag/ontology.yaml`; `query` lee además los hechos construidos | `build` escribe `data/oag/<id>/facts.json`; `query` imprime y guarda `oag*.json` |
| [`hybrid.py`](hybrid.py) | Ejecuta GraphRAG y OAG, y usa los componentes de la ontología para filtrar o dejar pasar el resultado del grafo | Entradas de GraphRAG y OAG, pregunta y hechos OAG | Guarda `hybrid*.json` con la ruta elegida (`ontology` o `graphrag`) |
| [`record_answer.py`](record_answer.py) | Puntúa los IDs de la respuesta final de Claude y los añade a una ejecución | IDs, pregunta y, si existe, el JSON previo de la técnica | Agentic RAG crea `agentic_rag*.json`; para otra técnica añade `answer` y `answer_score` o crea un JSON mínimo |
| [`compare.py`](compare.py) | Ejecuta las variantes deterministas y genera tablas con resultados guardados, incluida la respuesta de Claude si se registró | Preguntas y `data/runs/<id>/*.json` | Imprime y escribe `data/runs/compare.md`; `--no-run` solo lee resultados existentes |
| [`lib.py`](lib.py) | Funciones compartidas; no es un comando independiente | Configuración, corpus, preguntas y resultados | Define rutas, filtra el hold-out, extrae IDs, calcula métricas y serializa ejecuciones |
| [`semantic.py`](semantic.py) | Funciones opcionales de embeddings; no es un comando independiente | Textos y modelo multilingüe | Devuelve similitudes ordenadas y cachea vectores en `data/cache/embeddings/` |

### Opciones y comportamiento por comando

- **`holdout.py`** acepta `--q`. El informe enumera ficheros reservados, notas derivadas excluidas
  y pasajes redactados. Vuelve a crear únicamente la carpeta generada `data/holdout/<id>/`; no
  modifica `data/corpus/`.
- **`naive_rag.py`** acepta `--k`, `--chunk-words`, `--overlap`, `--embed`, `--model`, `--lang`,
  `--query` y `--quiet`. `--embed` cambia TF-IDF por similitud de embeddings. `--query` prevalece
  sobre el texto definido en la pregunta; `--lang es` usa su versión en castellano llano.
- **`graphrag.py`** acepta `--topic`, `--hops`, `--lang`, `--semantic`, `--model`, `--full`,
  `--native` y `--quiet`. De forma normal limita el grafo a fuentes del corpus de la demo y aplica
  el hold-out. `--full` amplía el ámbito al grafo completo; `--native` delega en el wrapper `/kg`
  instalado y no forma parte del resultado puntuado.
- **`oag.py build`** reconstruye los hechos usando la ontología y no llama a un LLM.
  **`oag.py query`** acepta `--query`, `--schema`, `--lang`, `--semantic`, `--min-sim`, `--model`
  y `--quiet`. `--schema` reproduce las versiones 1, 2 o 3; `--semantic` selecciona componentes
  por similitud y requiere el grupo `embed`.
- **`hybrid.py`** acepta `--hops`, `--schema`, `--lang`, `--semantic` y `--quiet`. Si la pregunta
  se asigna a componentes, devuelve los tickets filtrados por OAG; si no, mantiene los candidatos
  de GraphRAG y presenta comunidades como propuestas para revisión humana. Construye los hechos si
  aún no existen.
- **`record_answer.py`** acepta como técnica `naive_rag`, `agentic_rag`, `graphrag`, `oag` o una
  clave de variante, por ejemplo `oag_v3_es`. Los IDs pueden separarse por cualquier delimitador.
  `--tool-calls` y `--tokens` registran el coste aproximado de recuperación de Agentic RAG.
- **`compare.py`** acepta `--q` y `--no-run`. Sin `--q` procesa todas las preguntas; por defecto
  vuelve a ejecutar las variantes deterministas, construye los hechos OAG que falten y omite las
  variantes semánticas si no está instalado `sentence-transformers`. `--no-run` evita esas
  ejecuciones y compone las tablas únicamente con los JSON ya guardados.

`lib.py` no tiene CLI. `add_question_arg` y `load_question` resuelven `--q`, `DEMO_Q` y el valor
por defecto; `add_lang_arg`, `spanish_question` y `spanish_topic` proporcionan la variante en
castellano; `run_key`, `run_dir` y `facts_path` construyen las rutas de resultados. `holdout_pattern`,
`derived_file`, `redact`, `holdout_view`, `excluded_files` y `load_corpus` producen la misma vista
filtrada para todas las técnicas; `ticket_ids` extrae IDs y elimina los reservados. `score` y
`print_score` calculan recall y precisión, `approx_tokens` estima caracteres/4 y `save_run` guarda el
JSON común.

`semantic.py` tampoco es un comando: `model_name` resuelve el modelo, `encode` carga y cachea
embeddings normalizados, `similarities` calcula cosenos y `rank` devuelve los índices ordenados.
El modelo se carga en CPU bajo demanda; las técnicas sin `--embed` o `--semantic` no necesitan esa
dependencia.

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
5. **Híbrido GraphRAG + OAG.** GraphRAG aporta candidatos amplios. Si la pregunta se asocia a un
   componente de la ontología, OAG filtra esa lista; si no, se conserva GraphRAG y sus comunidades se
   muestran como propuestas que una persona puede revisar. No modifica la ontología ni llama a un LLM.
6. **De OAG v1 a v2.** La primera ontología fallaba de dos formas: traía tickets "no romper" de otras
   áreas (numeración, PDF) y no veía un invariante de detección de títulos que el fin de carta usa. La v2
   añade una restricción (el ticket protegido debe compartir componente) y una relación `calls` entre
   componentes. `--schema 1` reproduce la v1. Es evolución del esquema, escrita después de ver el fallo.
7. **Pregunta en castellano llano (`--lang es`).** El corpus está en inglés, por lo que la búsqueda
   por palabras de Naive RAG, GraphRAG y OAG v2 no resuelve la diferencia de idioma. La capa semántica
   usa embeddings multilingües en el primer paso de cada técnica: Naive RAG ordena los trozos por
   significado, GraphRAG elige la semilla por similitud y OAG elige los componentes (`--semantic`).
   OAG v3 ofrece una alternativa sin modelo: sinónimos en castellano para cada componente
   (`--schema 3`).

## Limitaciones

- Dos preguntas: es una demostración, no una evaluación. El Paso 0 del `HANDOVER.md` (15 a 20
  preguntas) es la evaluación.
- OAG v2 se escribió después de ver qué fallaba en la primera pregunta. Hay que validarlo con preguntas
  nuevas antes de atribuirle el resultado.
- Con pocos documentos, Naive RAG lo tiene fácil, sobre todo si entra un hub como `SHARP_EDGES`, que ya es
  un índice escrito a mano. Con el corpus completo (453 ficheros) su recall baja del 100 % al 71 % (ver
  `docs/GUIA_DEMO.md`, sección 6).
- La extracción de OAG es determinista (frontmatter, tablas, citas y sinónimos). En producción se
  completaría con extracción guiada por LLM (Fase C), siempre validada contra la misma ontología.
- Los componentes y sinónimos de la ontología están escritos a mano para este dominio. Ese es el precio
  de OAG y el principal riesgo de mantenimiento.
- El umbral de similitud de OAG (`--min-sim 0.42`) está calibrado con las dos preguntas de la demo. Con
  más preguntas habría que fijarlo con preguntas no vistas.
