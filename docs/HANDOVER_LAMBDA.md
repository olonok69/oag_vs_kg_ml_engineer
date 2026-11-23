# Traspaso al repo lambda: OAG sobre el grafo de tickets

> **Para quién:** el equipo y el agente (Claude Code u otro) que trabajen en `document-parser-lambda`, donde
> viven el grafo de tickets (`data/knowledge-graph/`), los writeups (`data/changes/`) y las skills `/kg` y
> `/kg-refresh`.
> **Origen:** el repo de investigación `oag_vs_kg_ml_engineer` (informe, deck, demo y guías). Este documento
> resume lo que se vio y se hizo allí, lo que se aprendió y cómo aplicarlo y evaluarlo en el caso real.
> **Fecha:** 2026-11-23. **Estado:** investigación y demo terminadas; la adopción en el repo lambda no ha
> empezado.

Cómo usarlo: el equipo puede leer las secciones 1 a 4 para entender qué se propone y por qué. El agente que
vaya a implementar algo debe leerlo entero y empezar por la sección 7 (instrucciones y reglas).

---

## 1. Resumen

- **Pregunta de partida:** ¿Ontology-Augmented Generation (OAG) se parece a nuestro grafo de tickets? ¿Qué
  merece la pena adoptar?
- **Respuesta:** son primos, no gemelos. El grafo ya hace la mitad de OAG: conocimiento del dominio en un
  grafo, construcción cara una vez, consulta sin LLM y atribución a fichero fuente. Le falta la otra mitad:
  un esquema escrito **antes** de extraer (schema-first), validar el grafo contra él y devolver hechos con
  tipo en lugar de solo «qué leer».
- **Lo que mostró la demo**, con dos preguntas reales sobre el corpus completo de `/kg` (453 ficheros):
  - En una pregunta de **reglas** sobre un componente modelado («qué no romper al arreglar este bug»), OAG
    encuentra los 7 tickets de referencia entre 15 resultados. GraphRAG (nuestro `/kg`) también los encuentra,
    pero entre 53.
  - En una pregunta de **exploración** sobre un área que la ontología no modela, GraphRAG recupera el 83 % y
    lo agrupa en temas. OAG no devuelve nada.
- **Recomendación:** adoptar OAG por partes y solo para las preguntas de reglas. Hay que escribir una
  ontología pequeña que sale en buena parte de las plantillas, extraer sin LLM donde se pueda, validar en
  `/kg-refresh` y añadir un modo `/kg facts` junto al `/kg <tema>` actual. Antes de nada, un set de
  preguntas con respuesta conocida para medir.

---

## 2. Conceptos mínimos

| Término | Qué es | En nuestro caso |
|---|---|---|
| **Ontología** | Especificación explícita del dominio: clases, relaciones, atributos y restricciones. Distingue el esquema (qué puede existir) de los hechos (qué es verdad hoy) | Ticket, Invariant, Component, Test y sus relaciones (`touches`, `guards`, `originates`, `verified_by`...) |
| **Schema-first** | El esquema se escribe antes de extraer y la extracción solo puede emitir lo que el esquema declara | Hoy el grafo es *schema-emergent*: graphify decide los tipos al extraer |
| **Fact block** | Bloque pequeño de hechos tipados sobre un sujeto, con su fuente (OG-RAG lo emite en JSON-LD) | Un ticket con los invariantes que origina, quién lo nombra como «no romper», sus tests y su fichero |
| **Set cover voraz** | Elegir el mínimo conjunto de fact blocks que cubre todos los nodos relevantes para la pregunta | Lo que haría `/kg facts <componente>` |
| **altLabels** | Sinónimos de cada componente en texto libre | `get_letter_end`, `LETTER_END_*`, «end-of-letter» y «fin de carta» son el mismo componente |
| **OWL** | Estándar del W3C para escribir ontologías; con un razonador deduce hechos nuevos; mundo abierto | No hace falta: un YAML cumple su papel |
| **SHACL** | Estándar del W3C para validar datos contra «formas»; mundo cerrado; devuelve un informe | No hace falta: una validación en Python en `finalize` cumple su papel |
| **Recall** | De los tickets de referencia, cuántos encuentra la técnica. Mide lo que se deja fuera | En «qué no romper» es la métrica que manda |
| **Precisión** | De los tickets devueltos, cuántos están en la referencia. Mide el ruido | La referencia es un mínimo: la precisión es una cota baja |

Referencia de método: K. Sharma, P. Kumar, Y. Li, *OG-RAG: Ontology-Grounded Retrieval-Augmented Generation*,
arXiv 2412.15235, EMNLP 2025. Es el único trabajo con método y evaluación; gana sobre todo en recall de hechos
(0,84 a 0,95 frente a 0,41 a 0,78 de GraphRAG en sus dominios), con ontologías hechas a mano.

---

## 3. Qué se hizo en el repo de investigación

1. **Investigación** de las tres lecturas del término (OG-RAG de Microsoft Research, Palantir Foundry y un
   artículo divulgativo) y comparación con el grafo en siete dimensiones. Informe: `docs/OAG_VS_KG.md`.
2. **Medición del grafo real** (`/kg-refresh` del 20-11-2026): 453 ficheros, unas 690.000 palabras, 3.977
   nodos, 8.076 aristas y 213 comunidades. El 93 % de las aristas es EXTRACTED. Unos dos tercios de las
   aristas son genéricas (`references` 4.749, `relates_to`, `conceptually_related_to`,
   `semantically_similar_to`): dicen que dos cosas tienen que ver, no cómo.
3. **Demo en directo** con seis skills de Claude Code sobre el mismo corpus y las mismas preguntas:
   - Naive RAG (trozos por TF-IDF o embeddings);
   - Agentic RAG (Claude busca y lee en bucle);
   - GraphRAG (la consulta de `/kg` reproducida en Python sobre `graph.json`);
   - OAG (ontología YAML, extracción determinista, validación al estilo SHACL y set cover);
   - un híbrido GraphRAG + OAG;
   - una comparativa con recall, precisión, F1 y coste.
4. **Ontología mínima de la demo** (`demo/oag/ontology.yaml`, unas 80 líneas): 4 clases, 6 relaciones, 1
   restricción, 4 componentes con sinónimos en inglés y castellano y reglas de extracción. Es el punto de
   partida natural para la Fase A en el repo lambda.
5. **Pregunta en castellano llano** (el corpus está en inglés) y capa semántica opcional con embeddings
   multilingües en CPU.
6. **Material de presentación**: deck de 35 slides en ES y EN con guion y notas del orador, guías de la demo,
   guía técnica con enlaces al código y PDF de todo.

### Resultados

Pregunta A, reglas sobre un componente modelado (7 tickets de referencia):

| Técnica | Recall | Precisión | Tickets devueltos | Tokens de contexto |
|---|---|---|---|---|
| Naive RAG | 71 % | 62 % | 8 | ~1.600 |
| GraphRAG, 1 salto | 71 % | 50 % | 10 | ~770 |
| GraphRAG, 2 saltos | 100 % | 13 % | 53 | ~7.000 |
| OAG, ontología v1 | 86 % | 35 % | 17 | ~2.000 |
| OAG, ontología v2 | 100 % | 47 % | 15 | ~2.500 |
| Híbrido GraphRAG + OAG | 100 % | 47 % | 15 | ~2.500 |

Pregunta B, explorar un área sin modelar (29 tickets de referencia, por una regla sobre los títulos):

| Técnica | Recall | Precisión | Tickets devueltos |
|---|---|---|---|
| Naive RAG | 10 % | 100 % | 3 |
| GraphRAG, 1 salto | 21 % | 67 % | 9 |
| GraphRAG, 2 saltos | 83 % | 43 % | 56 |
| OAG, v1 y v2 | 0 % | - | 0 |
| Híbrido GraphRAG + OAG | 83 % | 43 % | 56 |

Ninguna técnica llama a un LLM para recuperar, salvo Agentic RAG.

---

## 4. Lecciones aprendidas

1. **Cada técnica gana en un tipo de pregunta.** OAG gana en reglas sobre lo que está modelado; GraphRAG, en
   explorar lo que nadie ha modelado. OAG no sustituye a `/kg`: lo completa. Uno descubre la estructura y el
   otro la fija como contrato.
2. **OAG falla en silencio fuera de su esquema.** Si la pregunta no nombra ningún componente, devuelve cero
   hechos sin avisar. Cualquier integración tiene que decir «esta pregunta no está en la ontología» y caer a
   `/kg`.
3. **La ganancia de OAG está en el ruido, no solo en el recall.** GraphRAG a dos saltos también llega al
   100 %, pero entre 53 tickets. OAG da los mismos 7 entre 15, y cada uno con su porqué: qué invariante
   origina, qué componente toca y qué test lo fija.
4. **La ontología también se depura.** La v1 falló de dos formas, y las dos eran del esquema:
   - una relación sin restricción (`must_not_break`) traía tickets de otras áreas;
   - una dependencia sin declarar (el fin de carta llama a la detección de títulos) dejaba fuera un
     invariante.

   La v2 añadió una restricción de mismo componente y la relación `calls`. Se escribió después de ver el
   fallo, así que el resultado solo se puede atribuir a la técnica cuando se valide con preguntas nuevas.
5. **Las dependencias entre componentes importan.** Sin `calls`, los componentes son islas y se pierden los
   invariantes de código que se llama desde el componente tocado. Es la relación con más valor por línea
   escrita.
6. **La ontología sale de las plantillas.** ISSUE_NOTE (Ticket), SHARP_EDGES (Invariant, con su ticket de
   origen), FOLLOWUPS, TEST_MAP y QA_ACCEPTANCE (Test), PLAYBOOK y memoria (Lesson, Decision). No hay que
   inventarla: hay que escribir la que ya usamos.
7. **La extracción determinista llega lejos.** En la demo no hay LLM ni al construir ni al consultar: tablas
   de invariantes de SHARP_EDGES, citas a tickets, nombres de tests y sinónimos bastan para la pregunta de
   reglas. El LLM queda para lo que el parser no ve, y siempre validado.
8. **Validar y contar lo rechazado.** La validación al estilo SHACL rechaza las aristas fuera del esquema
   (por ejemplo, menciones genéricas) y lo informa. Tragarse lo rechazado esconde fallos de extracción.
9. **El idioma solo afecta al primer paso.** Con la pregunta en castellano llano, las tres técnicas
   deterministas caen sin avisar. Para OAG basta con seis sinónimos en castellano en la ontología o con
   elegir el componente por similitud con un modelo pequeño en CPU: después los hechos son los mismos. El
   umbral semántico (0,42) se calibró con las dos preguntas de la demo y hay que recalibrarlo.
10. **El híbrido iguala, no supera.** GraphRAG propone y la ontología filtra si la pregunta cae en ella; si
    no, queda la lista del grafo y sus comunidades salen como propuesta para ampliar la ontología. Iguala a
    la mejor técnica en cada pregunta sin elegirla. En la pregunta A el grafo no aportó ningún ticket que OAG
    no tuviera. Su valor es el enrutado automático y la lista de qué modelar después.
11. **Con poco corpus todo parece funcionar.** Con 14 ficheros, Naive RAG tenía un 100 % de recall; con 450,
    un 71 %. Evaluar siempre con el corpus completo.
12. **El hold-out se escapa por rincones.** El writeup que sirve de hoja de respuestas se excluyó, pero una
    viñeta de SHARP_EDGES y dos knowledge items describían su arreglo, y una técnica llegó a ellos. El
    hold-out tiene que excluir todo lo que derive del ticket reservado, no solo su fichero. En la demo ya se
    hace (`lib.holdout_view`): fuera las notas sobre el ticket y cada pasaje que lo menciona. Al corregirlo
    solo cambió Naive RAG con embeddings (del 57 % al 43 % de recall en la pregunta A); el resto de cifras de
    este documento ya son las del hold-out completo.
13. **F1 esconde lo que importa.** Por F1, Naive RAG queda casi a la par de OAG v2 en la pregunta A, pero se
    deja 2 de los 7. En «qué no romper» un olvido es una regresión: hay que mirar qué tickets faltan, no solo
    cuántos.
14. **Sin esquema, cada refresh reinventa los tipos.** En lambda, aun con la convención de IDs del prompt,
    solo sobrevive entre el 35 % y el 54 % de los IDs de un refresh al siguiente, y nombrar las comunidades
    cuesta una hora por refresh. Los IDs que salen de un parser determinista son estables por construcción.
15. **La densidad de la extracción LLM depende del modelo y del brief.** Un refresh de lambda necesitó tres
    ejecuciones hasta dar un número de nodos razonable. Todo lo que pase al parser deja de depender de eso; lo
    que quede en el LLM hay que vigilarlo comparando los recuentos por clase con el grafo anterior.

---

## 5. Cómo aplicarlo en el repo lambda

Principio: pequeño, reversible y medible, como los gates de la metodología. Cada fase se puede revertir sin
tocar las demás y tiene su criterio de aceptación.

### Lo que ya existe en lambda (revisado en local el 2026-11-23)

El grafo de lambda está más avanzado que la copia sanitizada que usó la investigación. Ya es en parte
schema-first, aunque sin las clases y relaciones de dominio que dan valor a OAG. Todo vive en
`data/knowledge-graph/` (fuera de git); el procedimiento completo está en `KG_PROCEDURES.md` y el reparto de
papeles en `REFRESH_OWNERSHIP.md`.

| Pieza | Qué hace hoy | Qué tiene ya de OAG |
|---|---|---|
| `build_manifest.py`, `stage_corpus.py` | Eligen y aplanan el corpus (420 ficheros el 20-11). Desde finales de octubre no entra la memoria de los agentes; sí los knowledge items compartidos de `data/changes/knowledge/`. El manifest para si un fichero no está en el registro sincronizado | Corpus reproducible y con procedencia |
| `EXTRACTION_PROMPT_20261009.md` y el brief por chunks `EXTRACTION_PROMPT_chunks_20261117.md` | Fijan cómo extraen los subagentes: convención de IDs por tipo (`ticket_<proyecto>_<n>`, `sym_<nombre>`, `cfg_`, `hub__`, `knowledge__`, `rationale_`, `concept_`), vocabulario de relaciones (`calls`, `implements`, `references`, `cites`, `rationale_for`...) y relaciones tipadas de las tablas de STATUS (`implemented_by`, `is_blocked_by`, `has_parent`, `has_subtask`) | Un esquema ligero: clases implícitas en el prefijo del ID y vocabulario de relaciones cerrado. Faltan las clases y relaciones de dominio: Invariant, Test, Component, `guards`, `originates`, `touches`, `verified_by` |
| `kg_merge_canonical.py` | Fusiona los fragmentos de los chunks, canoniza IDs duplicados y hace un censo de IDs fuera de convención y de fugas de `_corpus` | Una validación al estilo SHACL, pero solo sobre los IDs, no sobre las relaciones ni sus clases de origen y destino |
| Comprobación de procedencia por chunk | Cada nodo tiene `source_file` dentro de su chunk y todos los ficheros quedan cubiertos | Atribución verificada |
| `kg_refresh.sh` (`prepare`, `finalize`, `request`) | Prepara el scratch, copia artefactos, hace el leak-check y la copia de seguridad previa. Solo refresca la máquina publicadora; las demás piden un refresh con `request` | El sitio natural para validar contra la ontología |
| `kg_labels.py` y `community_labels.json` | Nombres de comunidad, re-anclados en cada refresh (`remap`, `check`, `inject-html`) | Nada: es el coste que el esquema reduciría |
| `kg_query.sh` | `explain`, `path`, `find`, con el nombre de comunidad como zona de peligro | Recuperación determinista, sin LLM |
| `kg_domain_noise.py` | Mide cuánto estorban los nodos de metodología en las consultas de producto | Una métrica de calidad del grafo ya en uso |
| `kg_paths.py` / `kg_paths.sh` | Rutas por `KG_DATA_ROOT` y `KG_WORK_DIR`, para correr fuera del repo (pipeline nocturno previsto) | Facilita un `run_eval.py` que lea el mismo grafo |
| Tests del grafo | `test_kg_*.py` (unos 50 tests) | Donde añadir los de la validación y de `facts` |

Fuentes del registro que ya están casi tipadas y que un parser puede leer sin LLM:

- `data/changes/SHARP_EDGES.md`: una tabla de invariantes («Load-bearing invariants») y entradas con su ticket
  de origen, el porqué y el test que las fija. El índice de nombres de invariantes también está al final de
  `CLAUDE.md`, agrupado por área (fin de carta, títulos...). Es la fuente de Invariant, `originates` y
  `guards`.
- `data/changes/TEST_MAP.md`: qué test protege qué ticket, agrupado por variante de extractor. Es la fuente de
  `verified_by`. Ojo: se desfasa (en octubre cubría 110 de 123 ficheros de test).
- El índice de casos del contrato de extracción (`_case_index.md`, generado): cada caso con el test que lo
  fija. Es otra fuente de hechos tipados.
- Las tablas de `STATUS_Tickets.md` y `STATUS_CR_PLAT.md`, con los enlaces entre tickets de Jira, que ya entran
  como relaciones tipadas.

Lo que enseña el historial de refrescos (`KG_PROCEDURES.md`, tabla «Naming cost»):

- Aun con la convención de IDs fijada en el prompt, solo sobrevive entre el 35 % y el 54 % de los IDs de nodo
  de un refresh al siguiente. Se conservan entre el 25 % y el 46 % de los nombres de comunidad, y cada refresh
  cuesta en torno a una hora de nombrar y auditar.
- La densidad de la extracción depende del modelo y del brief. Un refresh necesitó tres ejecuciones: con otro
  modelo salió la mitad de nodos y con una instrucción de «ser exhaustivo», el doble. Por eso hoy se comparan
  los recuentos por tipo con el grafo anterior antes de nombrar.
- Las dos cosas apuntan a lo mismo: lo que se pueda extraer de forma determinista no depende del modelo ni
  del día, y sus IDs son estables por construcción.

### Qué cambia con la propuesta

| Pieza | Cambio | Fase |
|---|---|---|
| `data/knowledge-graph/ontology.yaml` (nuevo) | Clases y relaciones de dominio, con los componentes y sus altLabels | A |
| Parser determinista (nuevo, p. ej. `kg_facts_build.py`) | Lee SHARP_EDGES, TEST_MAP, el índice de casos y los writeups; emite nodos y aristas tipados con IDs por construcción (`invariant_<slug>`, `test_<fichero>`) | B |
| `kg_refresh.sh finalize` | Valida el grafo contra la ontología (relación permitida, clase de origen y destino, `source_file`) y escribe un informe de rechazos | B |
| Prompt de extracción | Añade al vocabulario las relaciones de la ontología y deja a los subagentes solo lo que el parser no ve | C |
| `kg_query.sh facts <tema>` (nuevo) | Fact blocks por set cover, con caída a `explain` si el tema no está en la ontología | D |
| `kg_labels.py` | Nada al principio; mejora sola si sube la supervivencia de IDs | - |

### Paso 0. Línea base (primero, antes de tocar nada)

Detalle en la sección 6. Entregable: `data/knowledge-graph/eval/questions.yaml` con 15 a 20 preguntas y un
`run_eval.py` que mide el `/kg` actual. Sin esto no se puede decidir nada de lo que sigue.

### Fase A. Ontología mínima

- Escribir `data/knowledge-graph/ontology.yaml`, junto al grafo y fuera de git, porque los componentes y
  ejemplos pueden nombrar clientes.
- Punto de partida: `demo/oag/ontology.yaml` del repo de investigación (clases Ticket, Invariant, Component y
  Test; relaciones `touches`, `guards`, `originates`, `verified_by`, `must_not_break` y `calls`; restricción de
  mismo componente; altLabels en inglés y castellano; reglas de extracción).
- Ampliar solo con lo que pidan las preguntas del Paso 0. El esbozo completo de ocho clases (añade Followup,
  Symbol, Lesson y Decision, y las relaciones `fixes`, `regresses`, `supersedes`, `blocks`, `depends_on` y
  `follows_up`) está en `HANDOVER.md`, sección 5, del repo de investigación.
- Regla: si una relación no responde a una pregunta del set, fuera. El coste de mantener la ontología es el
  riesgo número uno de OAG.
- **Aceptación:** cada pregunta de reglas del set se asocia a algún componente por sus altLabels, y una
  persona del equipo ha revisado los componentes y sus `calls`.

### Fase B. Backbone determinista y validación

- Parser sin LLM (`kg_facts_build.py`, junto a los demás scripts del grafo y con rutas por `kg_paths`): lee la
  tabla «Load-bearing invariants» y las entradas de `SHARP_EDGES.md`, `TEST_MAP.md`, el índice de casos del
  contrato de extracción y las citas a tickets de los writeups. Emite nodos y aristas tipados con IDs según la
  convención de prefijos que ya fija el prompt (`invariant_<slug>`, `test_<fichero>`, `component_<slug>`, y
  `ticket_<proyecto>_<n>` para enlazar con lo existente). La función `build` de `demo/oag.py` hace esto sobre la
  copia sanitizada y se puede portar casi tal cual.
- Estos hechos se fusionan con los de los subagentes en `kg_merge_canonical.py`, como una fuente más, antes de
  la canonización. Si un subagente emite el mismo nodo, gana el del parser.
- Validación: ampliar el censo que ya hace `kg_merge_canonical.py` (IDs fuera de convención, fugas de
  `_corpus`) a las relaciones. Una arista se rechaza si su relación no está en el vocabulario o si la clase de
  origen o destino, deducida del prefijo del ID, no es la que pide la ontología. El informe de rechazos por
  motivo lo copia `kg_refresh.sh finalize` junto a los demás artefactos.
- Frontmatter YAML en las plantillas nuevas de ticket y de SHARP_EDGES (componentes que toca, invariantes que
  origina, tests) solo si el parser no llega con las tablas actuales. No hace falta para empezar.
- Respetar el reparto actual: el refresh solo corre en la máquina publicadora y, cuando exista, en el pipeline
  nocturno. El parser no necesita LLM, así que encaja en ese pipeline sin coste.
- Tests junto a los `test_kg_*.py`: parser sobre ficheros de ejemplo, validación con aristas buenas y malas.
- **Aceptación:** el informe de validación sale en cada refresh; los IDs del parser sobreviven al 100 % entre
  dos refrescos sin cambios en el registro; las preguntas de reglas del set no pierden recall respecto a la
  línea base.

### Fase C. Extracción guiada

- El prompt de extracción ya fija la convención de IDs y un vocabulario de relaciones. Esta fase no lo
  reescribe: añade las relaciones de la ontología (`touches`, `guards`, `originates`, `verified_by`,
  `must_not_break`) y le dice a los subagentes que no emitan lo que ya produce el parser (invariantes, tests y
  sus enlaces). Se versiona como un prompt fechado nuevo, igual que hoy.
- INFERRED queda para lo que el parser no ve: qué componente toca un ticket cuando no lo dice una tabla,
  relaciones entre símbolos, lecciones.
- Comparar los recuentos por clase con el grafo anterior antes de nombrar, como ya se hace, y añadir el
  informe de rechazos de la Fase B a esa revisión.
- **Aceptación:** baja el porcentaje de aristas genéricas, sube la supervivencia de IDs y de nombres de
  comunidad respecto a la tabla «Naming cost» de `KG_PROCEDURES.md`, y la hora de nombrar se mantiene o
  baja.

### Fase D. Consumo

- `kg_query.sh facts <tema>`: asocia el tema a componentes por altLabels, sigue `guards`, `calls` y
  `must_not_break` con la restricción de componente y devuelve el mínimo conjunto de fact blocks (set cover),
  cada uno con su fichero. Es la función `query` de `demo/oag.py`. El grafo apunta; el writeup manda.
- Si el tema no se asocia a ningún componente, decirlo y caer a `kg_query.sh <tema>`. Es el enrutado del
  híbrido (`demo/hybrid.py`) y evita el fallo silencioso.
- Gate de invariantes antes del merge: los invariantes que protegen los símbolos tocados por el diff, con un
  cruce con CodeGraph.
- Opcional: sinónimos en castellano en la ontología (barato) o la capa semántica (`demo/semantic.py`) si el
  equipo pregunta en castellano sin nombres de código.
- **Aceptación:** en las preguntas de reglas del set, `facts` iguala o mejora el recall de `/kg` con menos
  tickets devueltos; en las de exploración, el enrutado cae a `/kg` y no pierde nada.

### Qué no hacer

- Montar una plataforma (Foundry) o un triplestore OWL: nuestro tamaño no lo justifica.
- Meter hechos en el prompt en lugar de leer la fuente.
- Modelar todo el dominio «por completitud».
- Sustituir `/kg`: explorar lo sigue haciendo mejor el grafo.
- Atribuir una mejora a OAG sin el set de preguntas.

### Qué reutilizar del repo de investigación

| Fichero | Para qué |
|---|---|
| `demo/oag/ontology.yaml` | Ontología de partida (Fase A) |
| `demo/oag.py` (`build`, validación, `query`) | Parser, validación y set cover (Fases B y D) |
| `demo/hybrid.py` | Enrutado entre `facts` y `/kg`, y propuesta de qué modelar (Fase D) |
| `demo/lib.py` (`score`, `ticket_ids`, `holdout_view`) | Métricas, extracción de IDs y hold-out completo para el Paso 0 |
| `demo/compare.py`, `demo/questions.example.yaml` | Formato del set de preguntas y arnés de comparación |
| `demo/semantic.py` | Capa semántica opcional para preguntas en castellano |
| `docs/GUIA_TECNICA.md` | Qué hace cada función, con enlaces a las líneas |

---

## 6. Cómo evaluarlo en el caso real

### El set de preguntas

- Entre 15 y 20 preguntas reales, de dos tipos y en proporción parecida:
  - **de reglas**: «qué tickets, invariantes o tests protegen este componente», «qué no romper al arreglar
    este bug»;
  - **de exploración**: «qué hay sobre esta área y cómo se organiza».
- Cubrir zonas densas (fin de carta, títulos, numeración) y áreas aisladas.
- Para cada pregunta, una versión en castellano llano sin nombres de código, si el equipo pregunta así.
- Formato: el de `data/questions.yaml` de la demo (`id`, `pregunta`, `pregunta_llana`, `topic`, `tema`,
  `esperado`, `holdout`, `holdout_files`, `hops`).

### La respuesta de referencia

- Preguntas de bug: tomar un bug real ya resuelto y plantearlo como nuevo. La referencia es la lista de
  tickets que su writeup manda respetar.
- Preguntas de exploración: una regla objetiva (por ejemplo, los writeups cuyo título menciona el área), no
  una lista elegida a mano.
- **Hold-out completo:** excluir de todas las técnicas el writeup reservado y todo lo que derive de él:
  viñetas de SHARP_EDGES que describan su arreglo, knowledge items de `data/changes/knowledge/` y notas de
  memoria que lo cuenten, filas de TEST_MAP y del índice de casos que nombren su test, y nodos del grafo cuyo
  fichero fuente sea alguno de esos. En lambda la memoria de los agentes ya no entra en el corpus, pero los
  knowledge items sí. Comprobarlo buscando el ID y las palabras clave del arreglo en el corpus antes de medir.
- La referencia es un mínimo, no un techo: anotar quién la escribió y qué no puede mostrar.

### Métricas

| Métrica | Definición | Para qué |
|---|---|---|
| Recall | Referencia encontrada / referencia | Lo que se deja fuera; manda en reglas |
| Precisión | Referencia encontrada / devueltos | El ruido; cota baja |
| F1 | Media armónica de las dos | Ordenar; no decide por sí sola |
| Tickets devueltos | Tamaño de la lista | Lo que el agente tendrá que leer |
| Tokens de contexto | Caracteres / 4 de lo que llega al modelo | Coste por consulta |
| Llamadas LLM al recuperar | Número | Coste y variabilidad |
| Recall de la respuesta final | Sobre los IDs que da el agente | Lo que importa en uso real |

Qué cuenta como devuelto: en `/kg`, los tickets de los vecinos y de la lista de lectura; en `facts`, el sujeto
de cada fact block y los orígenes de sus invariantes, no los tickets que solo figuran como procedencia.

### Protocolo

1. Medir el `/kg` actual a 1 y 2 saltos: es la línea base.
2. Después de cada fase, volver a medir con el mismo set y el mismo corpus.
3. Revisar la composición: qué tickets faltan y cuáles sobran, pregunta a pregunta.
4. Si una ontología se corrige tras ver un fallo (como la v1 a v2), validarla con preguntas nuevas que no se
   usaron para escribirla.
5. Registrar el coste del refresh (tiempo y llamadas LLM) antes y después.

### Criterio de keep o revert

Se queda el cambio si:

- mejora el recall en las preguntas de reglas, sobre todo en zonas densas;
- no empeora en las de exploración ni en las áreas aisladas;
- reduce los tickets devueltos o los mantiene;
- el coste del refresh es igual o menor.

Si no, se revierte esa fase y se anota por qué.

### Qué no se puede concluir

- Con dos o tres preguntas, nada general: la demo es una demostración, no una evaluación.
- Una mejora conseguida con una ontología escrita mirando las mismas preguntas no cuenta hasta validarla con
  otras.
- Un umbral semántico calibrado con el set no vale para preguntas nuevas sin recalibrar.

---

## 7. Instrucciones para el agente

### Reglas

- **Confidencialidad.** El corpus, el grafo, la ontología real y el set de preguntas pueden contener nombres
  de clientes e IDs reales: viven en `data/` (fuera de git). Nada de eso va a un commit, un PR ni un servicio
  externo. Un grafo que se comparta fuera necesita su propia pasada cliente a rol.
- **El humano decide.** Proponer y ejecutar lo reversible. Cambios en la extracción de `/kg-refresh`, merges y
  todo lo que salga del repo los aprueba juan.
- **Sin atribución de IA** en commits, PRs, comentarios ni ficheros.
- **Idioma:** documentación y conversación en castellano de España; código e identificadores en inglés.
- **El grafo apunta; el writeup manda.** Ni `facts` ni `/kg` sustituyen a leer el writeup antes de tocar
  código.

### Checklist para empezar

- [ ] Leer este documento y, en el repo de investigación, `docs/OAG_VS_KG.md` y `docs/GUIA_TECNICA.md`.
- [ ] Leer en lambda `data/knowledge-graph/KG_PROCEDURES.md`, `REFRESH_OWNERSHIP.md`, los dos prompts de
      extracción vigentes y la skill `kg-refresh`. En el repo de investigación hay una copia sanitizada más
      antigua en `reference/`.
- [ ] Leer `data/changes/SHARP_EDGES.md`, `TEST_MAP.md` y el índice de casos: son la entrada del parser.
- [ ] Confirmar con juan qué máquina publica el grafo y en qué estado está el pipeline nocturno. No lanzar
      un refresh desde otra máquina: pedirlo con `kg_refresh.sh request`.
- [ ] Escribir el set de preguntas del Paso 0 con juan y medir la línea base.
- [ ] Proponer `ontology.yaml` y esperar el visto bueno antes de cambiar la extracción.
- [ ] Una fase cada vez, con su medición y su criterio de keep o revert.

### Bloque para el CLAUDE.md del repo lambda

```markdown
## OAG sobre el grafo de tickets

Plan y lecciones en `docs/HANDOVER_LAMBDA.md` del repo `oag_vs_kg_ml_engineer`.

- `/kg <tema>` explora (GraphRAG). `/kg facts <tema>` (cuando exista) responde preguntas de reglas con hechos
  tipados validados contra `data/knowledge-graph/ontology.yaml`. Si el tema no está en la ontología, usar
  `/kg <tema>`.
- La ontología es pequeña a propósito: una relación nueva solo entra si responde a una pregunta del set de
  `data/knowledge-graph/eval/questions.yaml`.
- Tras cambiar la ontología o la extracción: `kg_refresh.sh finalize` debe dar el informe de validación sin
  rechazos inesperados, y `run_eval.py` no debe perder recall en ninguna pregunta.
- Los hechos de invariantes y tests los produce `kg_facts_build.py` sin LLM; el prompt de extracción no debe
  volver a emitirlos.
- Nada de `data/` va a git.
```

---

## 8. Riesgos y temas abiertos

| Tema | Riesgo | Qué hacer |
|---|---|---|
| Ontología v2 escrita tras ver el fallo | Sobreajuste a una pregunta | Validar con preguntas nuevas |
| Umbral semántico calibrado con dos preguntas | No generaliza | Recalibrar con el set completo o usar sinónimos en la ontología |
| Mantenimiento de la ontología | Se queda atrás respecto a los tickets | Mantenerla pequeña; revisar en cada refresh lo que el grafo propone fuera del esquema |
| Enrutado entre `facts` y `/kg` | Una pregunta de exploración que nombre un componente se filtraría por error | Mostrar siempre por qué ruta se respondió y permitir forzar `/kg` |
| Fallo silencioso de OAG | Cero hechos sin aviso | `facts` debe decir explícitamente que la pregunta no está en la ontología |

---

## 9. Referencias

En el repo de investigación `oag_vs_kg_ml_engineer`:

| Fichero | Qué es |
|---|---|
| `HANDOVER.md` | Traspaso completo de la investigación, con el plan detallado y las cifras |
| `docs/OAG_VS_KG.md` | Informe de investigación |
| `docs/GUIA_DEMO.md`, `docs/DEMO_GUIDE.md` | Guía de la demo y evaluación (ES, EN) |
| `docs/GUIA_TECNICA.md`, `docs/TECHNICAL_GUIDE.md` | Qué ejecuta cada técnica, con enlaces al código |
| `docs/EJECUTAR_DEMO.md`, `docs/RUN_DEMO.md` | Cómo ejecutar la demo en Claude Code |
| `docs/GUION_PRESENTACION.md` | Guion de la presentación |
| `presentacion/OAG_vs_KG_Presentacion.pptx` | Deck (ES; EN en `OAG_vs_KG_Presentation_EN.pptx`) |
| `demo/` | Código de la demo y ontología mínima |

Fuentes externas:

- K. Sharma, P. Kumar, Y. Li, *OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for LLMs*, arXiv
  2412.15235 (2024), EMNLP 2025.
- Palantir Foundry, *Ontology augmented generation* (documentación de producto).
- L. Huang, *From RAG to OAG* (Medium).
- W3C: OWL 2 Web Ontology Language (2009) y Shapes Constraint Language, SHACL (2017).
