# OAG vs grafo de conocimiento de tickets

Investigación sobre **Ontology-Augmented Generation (OAG)** y su relación con el grafo de conocimiento de
tickets de la metodología de agentes IA (repos `*_code_ml_engineer`), más la presentación sobre el tema y el
material de partida para adoptar lo útil.

## Contenido

| Ruta | Qué es |
|---|---|
| [`HANDOVER.md`](HANDOVER.md) | Traspaso completo: qué se hizo, fuentes, plan accionable y lo que necesita otro agente |
| [`docs/OAG_VS_KG.md`](docs/OAG_VS_KG.md) | El informe: qué es OAG (OG-RAG, Palantir, Medium), comparación con nuestro grafo, qué adoptar y cómo medirlo |
| [`docs/GUIA_DEMO.md`](docs/GUIA_DEMO.md) / [`docs/DEMO_GUIDE.md`](docs/DEMO_GUIDE.md) | Guía para presentar la demo (ES / EN): qué es OAG, conceptos, pipelines, la demo con dos escenarios, la evaluación, dónde gana cada técnica y si merece la pena |
| [`docs/GUION_PRESENTACION.md`](docs/GUION_PRESENTACION.md) / [`docs/PRESENTATION_SCRIPT.md`](docs/PRESENTATION_SCRIPT.md) | Guion de la presentación slide a slide (ES / EN), para presentar en directo o grabar en vídeo; el mismo texto va en las notas del orador del deck |
| [`docs/EJECUTAR_DEMO.md`](docs/EJECUTAR_DEMO.md) / [`docs/RUN_DEMO.md`](docs/RUN_DEMO.md) | Cómo ejecutar la demo en Claude Code (ES / EN): preparación, cómo llamar a cada skill, guion comando a comando y qué debe salir |
| [`docs/GUIA_TECNICA.md`](docs/GUIA_TECNICA.md) / [`docs/TECHNICAL_GUIDE.md`](docs/TECHNICAL_GUIDE.md) | Guía técnica de la demo (ES / EN): qué ejecuta cada skill, en qué fichero y función, qué lee y qué escribe |
| [`docs/pdf/`](docs/pdf/) | Las guías y el informe en PDF, generados con `python docs/build_pdfs.py` |
| [`docs/img/`](docs/img/) | Diagramas SVG (ES y EN) de la guía y PNG para el deck, generados con `build_diagrams.py` |
| [`presentacion/OAG_vs_KG_Presentacion.pptx`](presentacion/OAG_vs_KG_Presentacion.pptx) / [`OAG_vs_KG_Presentation_EN.pptx`](presentacion/OAG_vs_KG_Presentation_EN.pptx) | Deck de 35 slides en castellano e inglés, mismo estilo que los decks del curso |
| [`presentacion/build_pptx_oag.py`](presentacion/build_pptx_oag.py) | Generador del deck (`python presentacion/build_pptx_oag.py [--lang en]`) |
| [`demo/`](demo/README.md) | Demo en directo: skills de Claude Code de Naive RAG a OAG sobre la memoria de tickets, con dos preguntas (una de reglas, otra de exploración), también en castellano llano con capa semántica; datos en `data/`, fuera de git |
| [`reference/KNOWLEDGE_GRAPH.md`](reference/KNOWLEDGE_GRAPH.md) | Cómo funciona el grafo de tickets actual (`/kg`, `/kg-refresh`) |
| [`reference/knowledge-graph/`](reference/knowledge-graph/) | Diseño, scripts, tests y el grafo construido (versión sanitizada): línea base para medir |
| [`reference/templates/`](reference/templates/) | Plantillas de la metodología: la ontología implícita (ticket, sharp edges, follow-ups, test map…) |

`reference/` es una copia de `claude_code_ml_engineer/docs/` (2026-11-20); algunos enlaces relativos dentro
de esos ficheros apuntan a su repo de origen.

## Siguientes pasos (hoja de ruta del informe)

Lo que ha enseñado la demo: OAG gana en preguntas de reglas sobre componentes modelados y GraphRAG en
preguntas de exploración. Si la pregunta llega en castellano y sin nombres de código, las tres técnicas
deterministas fallan hasta añadir una capa semántica (sinónimos en la ontología o embeddings multilingües). La
adopción tiene sentido por partes y solo para lo primero (ver las secciones 6 y 8 de `docs/GUIA_DEMO.md`).

1. **Línea base**: set de 15–20 preguntas con respuesta conocida y recall del grafo actual. Las dos de la
   demo son las primeras; `demo/compare.py` sirve de arnés.
2. **Fase A**: `ontology.yaml` mínima (~8 clases, ~10 relaciones) a partir de `reference/templates/`.
3. **Fase B**: backbone determinista (frontmatter + citas de tickets) y validación en `finalize`.
4. **Fase C**: extracción de graphify guiada por la ontología.
5. **Fase D**: `/kg facts <componente>` para reglas junto a `/kg <tema>` para explorar, y gate de invariantes en
   el flujo de trabajo.
