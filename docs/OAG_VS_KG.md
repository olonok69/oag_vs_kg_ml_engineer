# Ontology-Augmented Generation (OAG) frente al grafo de tickets

> Investigación (2026-11-19). Pregunta: ¿OAG es lo mismo que hacemos con el grafo de conocimiento de
> tickets ([`../reference/KNOWLEDGE_GRAPH.md`](../reference/KNOWLEDGE_GRAPH.md))? ¿Qué podemos adoptar?
> Deck: [`../presentacion/OAG_vs_KG_Presentacion.pptx`](../presentacion/OAG_vs_KG_Presentacion.pptx)
> (se regenera con `python presentacion/build_pptx_oag.py`).

## Respuesta corta

**Primos, no gemelos.** Compartimos el objetivo (anclar al agente en conocimiento del dominio estructurado y
citable) y el truco de coste (la inferencia cara se paga al construir; `/kg` no llama al LLM). La diferencia
clave: **OAG es schema-first** (la ontología se define antes y la extracción se ciñe a ella); **nuestro grafo
es schema-emergent** (graphify decide los tipos al extraer). Por eso nuestro grafo se parece más a GraphRAG
que a OG-RAG. Las plantillas de la metodología ya contienen una ontología implícita: falta escribirla y validar
el grafo contra ella.

## Qué es OAG (tres fuentes, tres lecturas)

| Fuente | Qué aporta |
|---|---|
| L. Huang, *From RAG to OAG* (Medium, 2026) | Visión conceptual: la ontología como «capa normativa» (clases, relaciones, axiomas tipo OWL/SHACL). Sin método ni evaluación. |
| Sharma, Kumar & Li, *OG-RAG* (Microsoft Research, arXiv 2412.15235, EMNLP 2025) | El método concreto. Un LLM mapea los documentos a la ontología → *fact blocks* JSON-LD → hipergrafo (bloque = hiperarista, par clave-valor = hipernodo). Recuperación: top-k nodos por clave y por valor + selección greedy del mínimo conjunto de hiperaristas que cubre. Sin llamadas LLM extra al consultar. |
| Palantir Foundry, *Ontology augmented generation* | Versión de plataforma: chunks como objetos de la Ontología, búsqueda semántica / keyword / híbrida (RRF, k=60), y una Ontología de negocio con objetos, enlaces y acciones tipadas. |

Resultados de OG-RAG (Tabla 1, context recall): soja 0.22 RAG / 0.54 RAPTOR / 0.41 GraphRAG / **0.84** OG-RAG;
trigo 0.14 / 0.85 / 0.78 / **0.95**; noticias 0.01 / 0.82 / — / 0.82. El abstract resume: +55% recall de hechos,
+40% corrección, atribución 30% más rápida, +27% en razonamiento sobre hechos. Letra pequeña: datos
propietarios, dos dominios, ontologías hechas a mano, y la relevancia de respuesta no siempre mejora
(RAPTOR gana en trigo y noticias).

## Comparación

| Dimensión | OG-RAG | Palantir | Nuestro grafo |
|---|---|---|---|
| Esquema | Ontología previa (expertos) | Ontología de negocio curada | Emergente, decidido por el LLM |
| Extracción | LLM → JSON-LD | Pipelines + chunks como objetos | Subagentes graphify sobre markdown |
| Representación | Hipergrafo de fact blocks | Objetos, enlaces, acciones | NetworkX, aristas con `relation` + `confidence` |
| Recuperación | Set-cover greedy | Semántica / keyword / híbrida | `explain` / `path` / `find`, deterministas |
| Coste por consulta | 0 LLM extra | Embeddings + LLM | 0 LLM |
| Salida | Hechos en el prompt | Chunks + citas | Lista de lectura (tickets + zona de peligro) |
| Acciones | No | Sí | Skills y gates del método |

Datos del grafo actual: 507 nodos, 672 aristas, 35 comunidades; aristas `references` 286, `relates_to` 221,
`rationale_for` 66, `fixes` 59, `semantically_similar_to` 22, `conceptually_related_to` 18. Unas tres cuartas
partes de las aristas son genéricas: ahí es donde una ontología añadiría más.

## Qué adoptar

1. **Ontología mínima** (`ontology.yaml`, junto a los scripts del KG bajo `data/`): ~8 clases (Ticket, Invariant,
   Followup, Component, Symbol, Test, Lesson, Decision) y ~10 relaciones (`fixes`, `regresses`, `supersedes`,
   `guards`, `originates`, `touches`, `verified_by`, `blocks`, `depends_on`, `follows_up`), sacadas de las
   plantillas que ya usamos.
2. **Extracción guiada**: pasar la ontología a los subagentes de graphify.
3. **Validación en `finalize`** (estilo SHACL): rechazar aristas fuera del esquema y nodos sin fuente.
4. **Backbone determinista**: frontmatter YAML en las plantillas de ticket y sharp edges + parseo de las citas
   `SST-NNNN` → hechos sin LLM (ya era candidato de Fase 2).
5. **`/kg facts <tema>`**: devolver el mínimo conjunto de fact blocks que cubre la consulta, con atribución
   (el set-cover de OG-RAG es barato sobre `graph.json`). El grafo sigue apuntando; el writeup manda.
6. **Invariantes como gate**: antes del merge, listar los invariantes que guardan los símbolos tocados
   (join con CodeGraph).
7. **IDs estables** por clase + ticket, para que las etiquetas de comunidad sobrevivan al refresh
   (hoy sobrevive <1%).

**No adoptar:** plataforma (Foundry) ni triplestore OWL; meter hechos en el prompt en lugar de leer la fuente;
una ontología grande «por completitud» (mantenerla es el riesgo nº1 de OAG).

## Cómo medirlo

Antes de cambiar nada, un set de 15–20 preguntas reales con respuesta conocida («¿qué tickets tocan
`get_letter_end`?», «¿qué invariante protege X?»). Métrica: recall de contexto (como C-Rec). Medir el grafo
actual como línea base, revisar la composición (qué tickets faltan), no solo el total, y decir qué no puede
mostrar el set.

## Fuentes

- K. Sharma, P. Kumar, Y. Li — [OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for Large Language Models](https://arxiv.org/abs/2412.15235) (2024); [EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1674/).
- Palantir — [Ontology augmented generation](https://www.palantir.com/docs/foundry/ontology/ontology-augmented-generation).
- L. Huang — [From RAG to OAG](https://medium.com/@linghuang_76674/from-rag-to-oag-68e3ac807c29).
