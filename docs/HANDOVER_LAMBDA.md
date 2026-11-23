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
- **Lo que mostró la demo**, con dos preguntas reales sobre el corpus completo de `/kg` (452 ficheros):
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
11. **Con poco corpus todo parece funcionar.** Con 14 ficheros, Naive RAG tenía un 100 % de recall; con 452,
    un 71 %. Evaluar siempre con el corpus completo.
12. **El hold-out se escapa por rincones.** El writeup que sirve de hoja de respuestas se excluyó, pero una
    viñeta de SHARP_EDGES y una nota de memoria describían su arreglo, y una técnica llegó a ellas. El
    hold-out tiene que excluir todo lo que derive del ticket reservado, no solo su fichero.
13. **F1 esconde lo que importa.** Por F1, Naive RAG queda casi a la par de OAG v2 en la pregunta A, pero se
    deja 2 de los 7. En «qué no romper» un olvido es una regresión: hay que mirar qué tickets faltan, no solo
    cuántos.
14. **Sin esquema, cada refresh reinventa los tipos.** Por eso casi ninguna etiqueta de
    `community_labels.json` sobrevive a una reconstrucción. IDs de nodo estables por clase y ticket lo
    arreglan.

---

## 5. Cómo aplicarlo en el repo lambda

Principio: pequeño, reversible y medible, como los gates de la metodología. Cada fase se puede revertir sin
tocar las demás y tiene su criterio de aceptación.

### Qué hay hoy y qué cambia

| Pieza actual | Qué hace | Cambio propuesto |
|---|---|---|
| `build_manifest.py`, `stage_corpus.py` | Eligen y aplanan el corpus en `_corpus/` | Nada |
| `/graphify` (subagentes LLM) | Extrae nodos y aristas, tipos emergentes | Fase C: recibe `ontology.yaml` y solo emite clases y relaciones del esquema |
| `kg_refresh.sh finalize` | Copia artefactos y hace el leak-check | Fase B: añade la validación contra el esquema y su informe |
| `output/graph.json` | Grafo NetworkX | Se mantiene; los hechos tipados se añaden como aristas con `relation` del esquema (o en `facts.json` aparte) |
| `community_labels.json` | Nombres de comunidad, a mano | Fase C: IDs estables para que sobrevivan |
| `kg_query.sh` (`explain`, `path`, `find`) | Consulta determinista, lista de lectura | Fase D: añade `facts <tema>` |
| Plantillas de ticket y SHARP_EDGES | Formato de los writeups | Fase B: frontmatter YAML |

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

- Frontmatter YAML en las plantillas de ticket y de SHARP_EDGES (id, componentes que toca, invariantes que
  origina, tests). Solo en los nuevos; los antiguos se cubren con el parser.
- Parser sin LLM: frontmatter, tablas de invariantes de SHARP_EDGES, citas a tickets y nombres de tests, que
  se convierten en nodos y aristas tipados. La función `build` de `demo/oag.py` hace exactamente esto y se
  puede portar casi tal cual.
- Validación en `kg_refresh.sh finalize`: rechazar aristas cuya relación no esté en el esquema o con origen y
  destino de clase equivocada, y nodos sin fichero fuente o con un ID que no cumpla el patrón. Escribir un
  informe con lo rechazado por motivo.
- **Aceptación:** el informe de validación sale en cada refresh; las preguntas de reglas del set no pierden
  recall respecto a la línea base.

### Fase C. Extracción guiada

- Pasar `ontology.yaml` a los subagentes de graphify, para que solo emitan clases y relaciones del esquema.
  INFERRED queda para lo que el parser no ve.
- IDs de nodo estables del tipo `Invariant:<ticket>`, para que las etiquetas de comunidad sobrevivan al
  refresh.
- **Aceptación:** baja el porcentaje de aristas genéricas, las etiquetas de comunidad sobreviven a un refresh
  y el coste del refresh es igual o menor.

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
| `demo/lib.py` (`score`, `ticket_ids`, hold-out) | Métricas y extracción de IDs para el Paso 0 |
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
  viñetas de SHARP_EDGES que describan su arreglo, notas de memoria, nodos del grafo cuyo fichero fuente sea
  alguno de esos. Comprobarlo buscando el ID y las palabras clave del arreglo en el corpus antes de medir.
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
- [ ] Leer la documentación del grafo en el repo lambda (la guía del grafo y los documentos de diseño de
      `data/knowledge-graph/`; en el repo de investigación hay una copia sanitizada en `reference/`).
- [ ] Confirmar con juan dónde están el corpus y el grafo vigentes y que se pueden leer.
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
- Nada de `data/` va a git.
```

---

## 8. Riesgos y temas abiertos

| Tema | Riesgo | Qué hacer |
|---|---|---|
| Fuga del hold-out en la pregunta A de la demo | Cifras algo optimistas en técnicas que llegan a la viñeta o a la nota | Excluir todo lo derivado del ticket reservado (sección 6) y volver a medir |
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
