# Traspaso: OAG vs grafo de conocimiento de tickets

> **Para quién:** cualquier persona o agente que continúe este trabajo, aquí o en otro proyecto.
> **Fecha:** 2026-11-20, actualizado el 2026-11-21. **Estado:** investigación, presentación (33 slides, ES y EN), guía
> y demo en directo terminadas; la adopción (Fases A–D) no ha empezado. La demo deja las dos primeras preguntas
> del Paso 0 y una ontología mínima de partida.
> Léelo entero antes de tocar nada: la sección 6 tiene las reglas que no se pueden romper.

---

## 1. La pregunta y la respuesta

**Pregunta (juan, 2026-11-19):** ¿Ontology-Augmented Generation (OAG) se parece a lo que usamos en la
metodología de agentes IA, en concreto al grafo de conocimiento de tickets? ¿Qué podemos adoptar?

**Respuesta:** primos, no gemelos. Nuestro grafo ya hace aproximadamente la mitad de OAG:

| Compartimos | Nos falta para ser OAG |
|---|---|
| Conocimiento del dominio en un grafo, no en chunks | Un esquema definido **antes** de extraer (schema-first) |
| Inferencia cara una vez al construir; la consulta no llama al LLM | Restricciones y validación del grafo contra el esquema |
| Atribución: cada nodo apunta a su fichero fuente | Hechos tipados (`fixes`, `regresses`, `guards`, `supersedes`…) |
| Uso antes de actuar (regla *history-first*) | Devolver hechos, no solo «qué leer» |
| Confianza explícita (EXTRACTED vs INFERRED) | Acciones ligadas a la ontología |

Nuestro grafo es **schema-emergent** (graphify decide los tipos al extraer), lo que lo acerca a GraphRAG más
que a OG-RAG. Prueba en los datos: en el grafo actual (453 ficheros, 3.977 nodos, 8.076 aristas) unos dos tercios
de las aristas son genéricas (`references` 4.749 de 8.076); en la copia sanitizada de `reference/`, ~75 % de 672.
Las plantillas de la metodología ya contienen una ontología implícita; falta escribirla y validar contra ella.

Informe completo: [`docs/OAG_VS_KG.md`](docs/OAG_VS_KG.md). Deck: [`presentacion/OAG_vs_KG_Presentacion.pptx`](presentacion/OAG_vs_KG_Presentacion.pptx).

---

## 2. Lo que se hizo (cronología)

1. **Lectura del sistema actual** en `claude_code_ml_engineer/docs/`: `KNOWLEDGE_GRAPH.md`,
   `knowledge-graph/design.md`, `phase2-refresh-design.md`, `output/GRAPH_REPORT.md` y `graph.json`
   (se contaron tipos de nodo y de arista, ver §4), y `ai-agents-code-methodology/README.md`.
2. **Investigación de OAG** con las tres fuentes que dio juan y búsqueda adicional (§3).
3. **Comparación** en siete dimensiones y propuesta de adopción (§5).
4. **Presentación** de 18 slides (19 desde que se añadió «Qué es una ontología») con el estilo de los decks del curso (paleta oscura, barra coral, eyebrow +
   título, tarjetas numeradas, franja de conclusión). Generada por código, renderizada a PDF con LibreOffice y
   revisada visualmente.
5. **Primera ubicación:** rama `claude/project-thread-oog8kb` de `claude_code_ml_engineer` (commit `356a646`,
   sin PR, sin fusionar). **Obsoleta**: el 2026-11-20 juan creó este repo y todo se movió aquí (commit
   inicial `9f34423` en `main`).
6. **Demo en directo** (2026-11-21): cinco skills de Claude Code (`/demo-naive-rag`, `/demo-agentic-rag`,
   `/demo-graphrag`, `/demo-oag`, `/demo-compare`) sobre el corpus completo de `/kg` (452 ficheros), con los
   datos reales en `data/` (fuera de git) y entorno con uv. Ver `demo/README.md`.
7. **Guía de la demo y diagramas** en ES y EN (`docs/GUIA_DEMO.md`, `docs/DEMO_GUIDE.md`, `docs/img/`) y deck
   bilingüe con la Parte 4 (la demo); 33 slides desde el punto 10.
8. **Dos escenarios** (decisión de juan): el objetivo no es demostrar que OAG siempre gana, sino enseñar dónde
   gana cada técnica y si merece la pena adoptarla. Pregunta A (reglas sobre un componente modelado): gana
   OAG con el esquema v2 (100 % de recall, 15 tickets frente a 53 de GraphRAG a dos saltos). Pregunta B
   (explorar un área que la ontología no modela): gana GraphRAG (83 % de recall y temas por comunidades;
   OAG no devuelve nada). La v2 de la ontología (restricción de componente y relación `calls`) se escribió
   tras ver el fallo de la v1 y así se cuenta. Detalle en la sección 6 de `docs/GUIA_DEMO.md`.
9. **Pregunta en castellano y capa semántica** (a raíz de una duda de juan: la pregunta está en castellano y el
   corpus en inglés). Las dos preguntas tienen una versión en castellano llano sin nombres de código
   (`--lang es`). Sin capa semántica fallan Naive RAG, GraphRAG y OAG. Se añade `demo/semantic.py` (embeddings
   multilingües `paraphrase-multilingual-MiniLM-L12-v2`, CPU): Naive RAG `--embed`, semilla de GraphRAG
   `--semantic` y componentes de OAG `--semantic`, y la ontología v3 con sinónimos en castellano. Con cualquiera
   de los dos arreglos OAG recupera en la pregunta A lo mismo que en inglés (100 % / 47 %); GraphRAG llega a la
   zona correcta pero no al nodo central (59 % en B frente al 83 %). El umbral semántico de OAG (0,42) está
   calibrado con estas dos preguntas. El entorno cloud necesitó permitir huggingface.co, `*.hf.co`,
   download.pytorch.org y download-r2.pytorch.org.
10. **Cómo ejecutarla en Claude Code**: chuleta `docs/EJECUTAR_DEMO.md` (EN: `docs/RUN_DEMO.md`) con la
   preparación, cómo se invoca cada skill y lo que debe salir, y una slide con los comandos. Las cinco skills se
   probaron en Claude Code. Las skills ejecutan siempre `python demo/...` desde la raíz para que una sola
   aprobación del permiso sirva para toda la demo. Pendiente: la prueba de Agentic RAG detectó que el hold-out
   de la pregunta A no excluye la viñeta del ticket excluido en `SHARP_EDGES` ni una nota `knowledge__` que
   describe su arreglo; hay que decidir si se excluyen (cambiaría algunas cifras).

---

## 3. Investigación: fuentes y hallazgos

| Fuente | Tipo | Qué aporta | Fiabilidad |
|---|---|---|---|
| K. Sharma, P. Kumar, Y. Li — [OG-RAG](https://arxiv.org/abs/2412.15235), Microsoft Research, arXiv 2412.15235 (dic. 2024), [EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1674/) | Paper | El único **método** concreto, con evaluación | Alta. El paper usa «OG-RAG», no «OAG» |
| Palantir — [Ontology augmented generation](https://www.palantir.com/docs/foundry/ontology/ontology-augmented-generation) | Docs de producto | OAG como práctica de plataforma | Media: describe sobre todo búsqueda semántica |
| L. Huang — [From RAG to OAG](https://medium.com/@linghuang_76674/from-rag-to-oag-68e3ac807c29) (Medium, 2026) | Divulgación | Marco conceptual y evolución de RAG | Baja: sin método ni números |

### OG-RAG (lo importante)

- **Ontología** = conjunto de triples (sujeto, atributo, valor); el valor es otra entidad o texto libre. No es
  una taxonomía: las relaciones no tienen por qué ser jerárquicas. Hecha a mano/revisada por expertos.
- **Preproceso:** un LLM (GPT-4o) mapea cada documento a la ontología y emite *fact blocks* JSON-LD.
- **Hipergrafo:** cada bloque aplanado es una hiperarista; cada par clave-valor es un hipernodo.
- **Recuperación:** top-k nodos por similitud de clave y de valor; después, greedy: el mínimo conjunto de
  hiperaristas que cubre esos nodos (óptimo bajo una restricción de matroide, según los autores).
- **Generación:** los hechos van al prompt como lista de diccionarios. **0 llamadas LLM extra al consultar.**
- **Resultados (Tabla 1, context recall):**

  | Dataset | RAG | RAPTOR | GraphRAG | OG-RAG |
  |---|---|---|---|---|
  | Soja | 0.22 | 0.54 | 0.41 | **0.84** |
  | Trigo | 0.14 | 0.85 | 0.78 | **0.95** |
  | Noticias | 0.01 | 0.82 | — (no terminó en 1 día) | 0.82 |

  Abstract: +55% recall de hechos, +40% corrección, atribución 30% más rápida, +27% en razonamiento sobre hechos.
- **Límites:** datos propietarios, dos dominios, ontologías manuales; la relevancia de respuesta no siempre
  mejora (RAPTOR gana en trigo 0.89 vs 0.79 y noticias 0.76 vs 0.73).

### Palantir

Chunks de documentos almacenados como objetos de la Ontología con propiedad de embedding; búsqueda semántica,
keyword o híbrida (fusión RRF, k=60); HyDE y aumento de query opcionales. Más amplio que el artículo: su
Ontología modela objetos, enlaces y **acciones** tipadas que el LLM puede consultar y proponer. Consejo útil:
si todo el contexto cabe en la ventana, empieza sin búsqueda.

### Medium

Define OAG como el uso de la ontología como «capa normativa» (clases, relaciones, axiomas tipo OWL/SHACL) dentro
de la cual ocurren recuperación y generación. Lo presenta como la sexta generación tras Naive RAG, RAG+rerank,
Modular RAG y Agentic RAG.

> **Nota de verificación:** el paper y la página de Palantir se leyeron en parte de forma literal y en parte
> mediante resumen automático (las cifras de la Tabla 1 y del abstract son literales; detalles posteriores
> como el estudio con 16 usuarios no se citan por eso). Si vas a citar algo nuevo, vuelve a la fuente.

---

## 4. El sistema actual (lo que hay que saber del grafo de tickets)

Documentación completa en [`reference/KNOWLEDGE_GRAPH.md`](reference/KNOWLEDGE_GRAPH.md) y
[`reference/knowledge-graph/`](reference/knowledge-graph/).

- **Qué indexa:** la *memoria del proyecto*: writeups por ticket, `STATUS`/`SHARP_EDGES`/`FOLLOWUPS`/`PLAYBOOK`,
  orientación (`CLAUDE.md`), runbooks y notas de memoria. Complementa a CodeGraph (código) con el *por qué*.
- **Corpus:** `manifest.txt` reproducible generado por `build_manifest.py`; `stage_corpus.py` lo aplana con
  nombres que preservan la procedencia (`tkt-103__tkt-103.md`, `hub__STATUS.md`…).
- **Construcción (`/kg-refresh`):** `kg_refresh.sh prepare` → `/graphify <scratch>` (subagentes LLM extraen
  nodos y aristas) → `kg_refresh.sh finalize` (copia artefactos + leak-check).
- **Consulta (`/kg`):** `kg_query.sh <tema>` (vecinos), `kg_query.sh <A> <B>` (camino), `kg_query.sh find <substr>`.
  Determinista, sin LLM: lee `output/graph.json`.
- **Cifras del grafo actual** (`/kg-refresh` del 20-11-2026, el que usa la demo, en `data/`): 453 ficheros
  (~690k palabras) → 3.977 nodos, 8.076 aristas, 213 comunidades; 93 % EXTRACTED, 7 % INFERRED.
- **Cifras de la copia sanitizada en este repo (`reference/`, 2026-11-20):** 116 ficheros (~196k palabras) → 507 nodos, 672 aristas, 35 comunidades;
  92% aristas EXTRACTED, 7% INFERRED. Nodos: `document` 420, `code` 58, `concept` 20, `rationale` 9.
  Aristas: `references` 286, `relates_to` 221, `rationale_for` 66, `fixes` 59, `semantically_similar_to` 22,
  `conceptually_related_to` 18.
- **Gotchas que ya costaron caro:**
  - graphify respeta `.gitignore` y `data/` está ignorado → correr in situ encuentra 0 ficheros. Se monta el
    corpus en un scratch fuera del repo.
  - graphify escribe `graphify-out/` relativo al CWD → `finalize` debe sincronizar también la copia in situ o
    las consultas leen un grafo viejo.
  - `community_labels.json` (nombres de comunidad, escritos a mano) **no** se regenera: en una reconstrucción
    sobrevivió <1%. Por eso los IDs estables de §5 importan.

Para recalcular las cifras:

```bash
python3 -c "import json,collections as c; g=json.load(open('reference/knowledge-graph/output/graph.json')); \
print(len(g['nodes']), len(g['links'])); print(c.Counter(e['relation'] for e in g['links']).most_common())"
```

---

## 5. Qué adoptar: plan accionable

Principio rector: pequeño, reversible y medible, igual que los gates de la metodología.

### Paso 0 — Línea base (hacer primero)

- Escribir 15–20 preguntas reales con respuesta conocida, p. ej. «¿qué tickets tocan `get_letter_end`?»,
  «¿qué invariante protege X?». Respuesta esperada = lista de IDs de ticket/invariante, escrita a mano.
- Medir el recall del grafo actual con `kg_query.sh` (equivalente a C-Rec de OG-RAG).
- Revisar la **composición** (qué falta), no solo el total, y anotar qué no puede mostrar el set.
- Sugerencia de ubicación: `eval/questions.yaml` + `eval/run_eval.py`.
- Punto de partida: la demo ya tiene el formato y el arnés (`data/questions.yaml` con varias preguntas,
  `demo/compare.py` con recall, precisión y F1 por técnica). Sus dos preguntas son las primeras del set;
  conviene mezclar preguntas de reglas y de exploración, porque cada técnica gana en un tipo.

### Fase A — Ontología mínima

`ontology.yaml` derivada de [`reference/templates/`](reference/templates/). Esbozo (ajustar con el corpus real):

```yaml
classes: [Ticket, Invariant, Followup, Component, Symbol, Test, Lesson, Decision]
relations:
  fixes:       {from: Ticket, to: [Ticket, Symbol]}
  regresses:   {from: Ticket, to: Ticket}
  supersedes:  {from: [Ticket, Decision], to: [Ticket, Decision]}
  guards:      {from: Invariant, to: [Symbol, Component]}
  originates:  {from: Ticket, to: [Invariant, Lesson]}
  touches:     {from: Ticket, to: [Symbol, Component]}
  verified_by: {from: [Ticket, Invariant], to: Test}
  blocks:      {from: Ticket, to: Ticket}
  depends_on:  {from: Ticket, to: Ticket}
  follows_up:  {from: Followup, to: Ticket}
```

De dónde sale cada clase: `ISSUE_NOTE_TEMPLATE` (Ticket: síntoma, causa raíz, fix, tests),
`SHARP_EDGES_TEMPLATE` (Invariant: invariante, por qué, test guarda, ticket de origen), `FOLLOWUPS_TEMPLATE`
(Followup), `TEST_MAP_TEMPLATE` / `QA_ACCEPTANCE_TEMPLATE` (Test), `HANDOVER_TEMPLATE` / PLAYBOOK (Lesson, Decision).
Regla: si una relación no responde una pregunta del set de la línea base, fuera.

### Fase B — Backbone determinista + validación

- Frontmatter YAML en las plantillas de ticket y de sharp edges (id, clase, `touches`, `fixes`, `guards`…).
- Parser sin LLM: frontmatter + citas de tickets (`TKT-NNN` / `SST-NNNN`) → nodos y aristas tipados.
- Validación estilo SHACL en `kg_refresh.sh finalize`: rechazar aristas fuera del esquema y nodos sin
  `source_file`; informar de lo rechazado, no tragárselo.

### Fase C — Extracción guiada

- Pasar `ontology.yaml` a los subagentes de graphify; `INFERRED` solo para lo que el parser no ve.
- IDs de nodo estables (`clase:ticket`, p. ej. `Invariant:TKT-128`) para que las etiquetas de comunidad
  sobrevivan al refresh.

### Fase D — Consumo

- `kg_query.sh facts <tema>`: devuelve el mínimo conjunto de *fact blocks* que cubre la consulta (greedy
  set-cover de OG-RAG sobre `graph.json`), cada uno con su fichero fuente. El grafo apunta; el writeup manda.
- Gate de invariantes antes del merge: invariantes que `guards` los símbolos tocados por el diff (join con CodeGraph).

### Qué **no** adoptar

- Plataforma (Foundry) ni triplestore OWL: el tamaño no lo justifica.
- Meter hechos en el prompt en lugar de leer la fuente.
- Una ontología grande «por completitud»: mantenerla es el riesgo nº1 de OAG.

**Criterio de keep/revert:** mejora de recall en zonas densas (fin de carta, títulos, numeración), sin empeorar
áreas aisladas, con coste de refresh igual o menor.

---

## 6. Reglas y restricciones (no negociables)

- **Confidencialidad:** el grafo real vive bajo `data/` (gitignored) porque contiene nombres de clientes.
  Lo que hay en `reference/` es la versión sanitizada (ClientA, TKT-NNN). Nunca subas un grafo o corpus sin
  sanitizar a un repo; un grafo para compartir fuera necesita su propia pasada cliente → rol.
- **Sin atribución de IA** en commits, PRs ni ficheros del repo (ni trailers `Co-Authored-By`, ni pies
  «Generated with…»). Commit como `olonok69 <22950229+olonok69@users.noreply.github.com>`.
- **Idioma:** juan escribe en castellano e inglés mezclados; responder y documentar en castellano salvo que
  cambie. El código y los nombres técnicos van en inglés.
- **El humano decide:** el agente investiga, propone y ejecuta lo reversible; push a ramas compartidas, merges
  y todo lo que salga fuera los aprueba juan.

---

## 7. Mapa del repo y cómo regenerar

| Ruta | Qué es |
|---|---|
| `HANDOVER.md` | Este documento |
| `docs/OAG_VS_KG.md` | Informe de investigación |
| `docs/GUIA_DEMO.md`, `docs/DEMO_GUIDE.md` | Guía de la presentación y la demo (ES, EN) |
| `docs/EJECUTAR_DEMO.md`, `docs/RUN_DEMO.md` | Cómo ejecutar la demo en Claude Code, comando a comando (ES, EN) |
| `docs/GUIA_TECNICA.md`, `docs/TECHNICAL_GUIDE.md` | Qué ejecuta cada skill por dentro, con enlaces al código (ES, EN) |
| `docs/img/` | Diagramas SVG y PNG, generados por `build_diagrams.py` |
| `docs/pdf/` | Guías e informe en PDF, generados por `docs/build_pdfs.py` (pandoc y Chrome) |
| `presentacion/build_pptx_oag.py` | Generador del deck (python-pptx, idempotente; `--lang en` para inglés) |
| `presentacion/OAG_vs_KG_Presentacion.pptx` | Deck de 33 slides (ES); `OAG_vs_KG_Presentation_EN.pptx` (EN) |
| `demo/`, `.claude/skills/demo-*` | Scripts, ontología mínima (`demo/oag/ontology.yaml`) y skills de la demo |
| `reference/KNOWLEDGE_GRAPH.md` | Explicación del grafo de tickets |
| `reference/knowledge-graph/` | Scripts, tests, diseño y grafo sanitizado (copia de `claude_code_ml_engineer/docs/`, 2026-11-20) |
| `reference/templates/` | Plantillas de la metodología (la ontología implícita) |

```bash
uv sync --group embed && source .venv/bin/activate
python docs/img/build_diagrams.py --png         # diagramas
python presentacion/build_pptx_oag.py           # regenera el .pptx (añade --lang en para el inglés)
# revisión visual (opcional)
soffice --headless --convert-to pdf presentacion/OAG_vs_KG_Presentacion.pptx
```

El generador copia los helpers de estilo de `claude_code_ml_engineer/presentacion/build_pptx.py`
(`base`, `cards`, `panel_bullets`, `code`, `divider`, `takeaway`) y añade `table` y `steps`. Si cambia el
estilo del curso, sincroniza esos helpers. Footer: «OAG vs grafo de tickets · Investigación».

Repos relacionados (mismo autor): `claude_code_ml_engineer`, `cursor_code_ml_engineer`,
`copilot_code_ml_engineer`, `pi_code_ml_engineer`. La metodología completa está en
`docs/ai-agents-code-methodology/` de cualquiera de ellos; `COPILOT_ADAPTATION.md` explica cómo aplicarla en un
repo sin grafo.

---

## 8. Para llevar esto a otro proyecto

1. **Tienes ya un grafo tipo graphify:** empieza por el Paso 0 (línea base) y la Fase A. Reutiliza
   `reference/knowledge-graph/` como plantilla de scripts.
2. **No tienes grafo:** primero la metodología (plantillas de ticket y sharp edges con frontmatter desde el
   día uno). Así el backbone determinista (Fase B) sale gratis y quizá no necesites extracción LLM.
3. **Adapta la ontología al dominio**, no copies la de aquí: las ocho clases salen de *nuestras* plantillas.
   Pregunta qué preguntas reales hace el equipo y deriva las relaciones de ahí.
4. **Mide antes y después** con preguntas de respuesta conocida. Sin línea base no sabrás si OAG ayuda.
5. **Checklist mínima para el agente que empiece:**
   - [ ] Leer este documento y `docs/OAG_VS_KG.md`
   - [ ] Leer `reference/KNOWLEDGE_GRAPH.md` (o el equivalente del proyecto destino)
   - [ ] Confirmar con la persona dónde vive el corpus real y si es confidencial
   - [ ] Escribir el set de preguntas y medir la línea base
   - [ ] Proponer `ontology.yaml` y esperar el visto bueno antes de cambiar la extracción
