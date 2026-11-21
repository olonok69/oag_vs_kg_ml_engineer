# OAG vs grafo de conocimiento de tickets

Investigación sobre **Ontology-Augmented Generation (OAG)** y su relación con el grafo de conocimiento de
tickets de la metodología de agentes IA (repos `*_code_ml_engineer`), más la presentación sobre el tema y el
material de partida para adoptar lo útil.

## Contenido

| Ruta | Qué es |
|---|---|
| [`HANDOVER.md`](HANDOVER.md) | Traspaso completo: qué se hizo, fuentes, plan accionable y lo que necesita otro agente |
| [`docs/OAG_VS_KG.md`](docs/OAG_VS_KG.md) | El informe: qué es OAG (OG-RAG, Palantir, Medium), comparación con nuestro grafo, qué adoptar y cómo medirlo |
| [`presentacion/OAG_vs_KG_Presentacion.pptx`](presentacion/OAG_vs_KG_Presentacion.pptx) | Deck de 19 slides, mismo estilo que los decks del curso |
| [`presentacion/build_pptx_oag.py`](presentacion/build_pptx_oag.py) | Generador del deck (`pip install python-pptx && python presentacion/build_pptx_oag.py`) |
| [`reference/KNOWLEDGE_GRAPH.md`](reference/KNOWLEDGE_GRAPH.md) | Cómo funciona el grafo de tickets actual (`/kg`, `/kg-refresh`) |
| [`reference/knowledge-graph/`](reference/knowledge-graph/) | Diseño, scripts, tests y el grafo construido (versión sanitizada): línea base para medir |
| [`reference/templates/`](reference/templates/) | Plantillas de la metodología: la ontología implícita (ticket, sharp edges, follow-ups, test map…) |

`reference/` es una copia de `claude_code_ml_engineer/docs/` (2026-11-20); algunos enlaces relativos dentro
de esos ficheros apuntan a su repo de origen.

## Siguientes pasos (hoja de ruta del informe)

1. **Línea base**: set de 15–20 preguntas con respuesta conocida y recall del grafo actual.
2. **Fase A**: `ontology.yaml` mínima (~8 clases, ~10 relaciones) a partir de `reference/templates/`.
3. **Fase B**: backbone determinista (frontmatter + citas de tickets) y validación en `finalize`.
4. **Fase C**: extracción de graphify guiada por la ontología.
5. **Fase D**: `/kg facts` y gate de invariantes en el flujo de trabajo.
