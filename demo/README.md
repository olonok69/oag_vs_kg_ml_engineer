# Demo: de Naive RAG a OAG sobre la memoria de tickets

Cuatro técnicas de recuperación responden a la misma pregunta real sobre el mismo corpus, y una quinta
skill las compara. Cada técnica es una skill de Claude Code que se ejecuta en directo.

| Skill | Técnica | Qué recupera | Script |
|---|---|---|---|
| `/demo-naive-rag` | Naive RAG | Trozos de texto por similitud (TF-IDF; `--embed` para embeddings) | `demo/naive_rag.py` |
| `/demo-agentic-rag` | Agentic RAG | Claude busca y lee en bucle con Grep/Read | (Claude) + `demo/record_answer.py` |
| `/demo-graphrag` | GraphRAG | Nuestro skill `/kg`: vecinos en el grafo de tickets y lista de lectura | `demo/graphrag.py` |
| `/demo-oag` | OAG | Hechos tipados, validados contra `demo/oag/ontology.yaml`, seleccionados por set cover | `demo/oag.py` |
| `/demo-compare` | Comparativa | Recall, precisión, tokens de contexto y llamadas LLM | `demo/compare.py` |

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
  kg/kg_query.sh         wrapper de /kg, solo para --native
  questions.yaml         pregunta, respuesta esperada y hold-out (plantilla: demo/questions.example.yaml)
  oag/facts.json         hechos generados por `oag.py build`
  runs/*.json            resultados de cada técnica y compare.md
```

Para ampliar el corpus basta con copiar más ficheros de `_corpus/` a `data/corpus/` y volver a ejecutar
`python demo/oag.py build`. Los scripts no dependen del número de ficheros.

## La pregunta y la respuesta esperada

La pregunta es un bug real ya investigado. Su writeup contiene una sección de "do-not-break" y una
batería de regresión escritas por quien lo resolvió: esa es la respuesta esperada. El writeup y las
notas que lo resumen se declaran como `holdout` en `questions.yaml` y se excluyen de todas las técnicas
(corpus, grafo y hechos), de modo que la pregunta se responde como si el bug fuera nuevo.

Métricas, contra la respuesta esperada:

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
uv sync --group embed                             # opcional: naive_rag.py --embed (instala torch)
source .venv/bin/activate                         # antes de lanzar claude, para que `python` sea el del venv
python demo/oag.py build          # una vez, o tras cambiar el corpus o la ontología
```

Sin uv: `pip install -r demo/requirements.txt`.

En Claude Code, en este orden: `/demo-naive-rag`, `/demo-agentic-rag`, `/demo-graphrag`, `/demo-oag`,
`/demo-compare`. Cada skill ejecuta su script, responde a la pregunta usando solo lo que ha recuperado y
registra la respuesta.

Los scripts también funcionan sin Claude Code:

```bash
python demo/naive_rag.py [--k 5] [--embed]
python demo/graphrag.py [--hops 2] [--full] [--native]
python demo/oag.py query
python demo/compare.py
```

## Qué muestra cada paso

1. **Naive RAG.** Recupera trozos que se parecen a la pregunta. Encuentra los términos, pero no distingue
   un ticket relevante de uno que solo aparece en el mismo párrafo, y no sabe por qué importa ninguno.
2. **Agentic RAG.** Claude planifica y vuelve a buscar. Mejora la precisión a cambio de pasos, tokens y
   resultados que cambian entre ejecuciones.
3. **GraphRAG (/kg).** Consulta determinista y barata, sin LLM. Devuelve vecinos y una lista de lectura,
   pero la mayoría de las aristas son genéricas (`references`, `conceptually_related_to`): dice qué leer,
   no qué hecho aporta cada fichero. Más saltos suben el recall y bajan la precisión.
4. **OAG.** La ontología se escribe antes: clases, relaciones, componentes con sus sinónimos y reglas.
   La extracción solo puede producir lo que el esquema permite, y la validación rechaza el resto
   (las menciones genéricas entre tickets). La pregunta se mapea a un componente y el set cover devuelve
   el mínimo de hechos que la cubren, cada uno con su fuente.

## Limitaciones

- Una sola pregunta y un corpus pequeño: es una demostración, no una evaluación. El Paso 0 del
  `HANDOVER.md` (15 a 20 preguntas) es la evaluación.
- Con pocos documentos, Naive RAG lo tiene fácil, sobre todo si entra un hub como `SHARP_EDGES`, que ya es
  un índice escrito a mano. Con el corpus completo (452 ficheros) su recall baja del 100 % al 71 %,
  mientras que OAG se mantiene en el 86 % (ver `docs/GUIA_DEMO.md`, sección 6).
- La extracción de OAG es determinista (frontmatter, tablas, citas y sinónimos). En producción se
  completaría con extracción guiada por LLM (Fase C), siempre validada contra la misma ontología.
- Los componentes y sinónimos de la ontología están escritos a mano para este dominio. Ese es el precio
  de OAG y el principal riesgo de mantenimiento.
