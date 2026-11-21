# CLAUDE.md

Investigación sobre Ontology-Augmented Generation (OAG) frente al grafo de conocimiento de tickets
(`/kg`), con una presentación y una demo en directo. Antes de cambiar nada, lee `HANDOVER.md`
(contexto, fuentes, plan de adopción y reglas) y `demo/README.md` si vas a tocar la demo.

## Reglas

- **Confidencialidad.** Los datos reales (corpus de tickets, grafo, pregunta de la demo, resultados)
  viven solo en `data/`, que está en `.gitignore`. Nunca se commitea nada de `data/`. Lo que hay en
  `reference/` es material sanitizado (ClientA, TKT-NNN). Si un fichero nuevo contiene nombres de
  clientes o IDs reales, no va al repo.
- **Sin atribución de IA** en commits, PRs, comentarios ni ficheros: ni `Co-Authored-By`, ni
  "Generated with", ni enlaces a sesiones. Commit como
  `olonok69 <22950229+olonok69@users.noreply.github.com>`.
- **Idioma.** Documentación y conversación en castellano de España. Código, identificadores y nombres
  técnicos en inglés.
- **Estilo.** Documentación técnica y profesional, sin emojis ni formato recargado. Comentarios en
  GitHub breves y con el mínimo formato.
- **Audiencia.** La presentación y la demo son divulgativas: explicar los conceptos para cualquier
  público sin perder rigor técnico.
- **El humano decide.** Proponer y ejecutar lo reversible; los merges y todo lo que salga del repo los
  aprueba juan.

## Mapa

| Ruta | Qué es |
|---|---|
| `HANDOVER.md` | Traspaso completo: pregunta, fuentes, comparación, plan (Paso 0 y Fases A a D), reglas |
| `docs/OAG_VS_KG.md` | Informe de investigación |
| `docs/GUIA_DEMO.md`, `docs/DEMO_GUIDE.md` | Guía de la demo en ES y EN |
| `docs/GUIA_TECNICA.md`, `docs/TECHNICAL_GUIDE.md` | Guía técnica de la demo (qué se ejecuta y dónde), con enlaces al código |
| `docs/img/build_diagrams.py` | Generador de los diagramas: SVG para las guías y PNG para el deck |
| `presentacion/build_pptx_oag.py` | Generador del deck (python-pptx). El `.pptx` se regenera desde aquí; no editarlo a mano |
| `presentacion/translations_en.py` | Traducciones para el deck en inglés |
| `demo/` | Scripts de la demo y ontología mínima (`demo/oag/ontology.yaml`) |
| `.claude/skills/demo-*` | Skills de la demo |
| `reference/` | Documentación y scripts del grafo de tickets (copia sanitizada) y plantillas de la metodología |
| `data/` | Datos reales, fuera de git (ver `demo/README.md`) |

## Presentación

```bash
uv sync && source .venv/bin/activate          # entorno (ver demo/README.md)
python docs/img/build_diagrams.py --png        # SVG + PNG de los diagramas, tras cambiar alguno
python presentacion/build_pptx_oag.py          # deck ES
python presentacion/build_pptx_oag.py --lang en   # deck EN (avisa de líneas sin traducir)
soffice --headless --convert-to pdf presentacion/OAG_vs_KG_Presentacion.pptx   # revisión visual
```

Para añadir o cambiar una slide se edita el generador, se regenera y se revisa el render. Los helpers de
estilo (`base`, `cards`, `panel_bullets`, `code`, `table`, `steps`, `takeaway`) mantienen el estilo del
deck. Las slides de diagrama usan `diagram(slide, "<nombre>")`, que inserta `docs/img/<nombre>.<lang>.png`.
Un texto nuevo en el deck necesita su entrada en `translations_en.py`.

## Demo

Cinco skills responden a las mismas preguntas reales sobre el mismo corpus. Hay dos escenarios en
`data/questions.yaml`: `letter-end-runin` (reglas sobre un componente modelado, gana OAG) y
`comment-memo-landscape` (explorar un área sin modelar, gana GraphRAG). Las skills y los scripts aceptan
el id (`--q <id>`):

1. `/demo-naive-rag`: trozos de texto por similitud.
2. `/demo-agentic-rag`: Claude busca y lee en bucle.
3. `/demo-graphrag`: nuestro skill `/kg` sobre `data/kg/output/graph.json`.
4. `/demo-oag`: hechos tipados validados contra la ontología (`--schema 1` reproduce la primera versión).
5. `/demo-compare`: recall, precisión y coste.

Preparación:

```bash
uv sync && source .venv/bin/activate   # lanzar claude con el venv activo
python demo/oag.py build --q letter-end-runin         # tras cambiar el corpus o la ontología
python demo/oag.py build --q comment-memo-landscape
```

Origen de los datos: `D:\repos3\ILS_2\document-parser-lambda\data\knowledge-graph\` (`_corpus/` y
`output/graph.json`). La pregunta y la respuesta esperada están en `data/questions.yaml`; el ticket que
sirve de hoja de respuestas se excluye de todas las técnicas (`holdout`).

Si cambias el código de la demo, actualiza los enlaces a líneas (`#L`) de `docs/GUIA_TECNICA.md` y
`docs/TECHNICAL_GUIDE.md`.

Durante una skill de la demo, responde solo con lo que haya recuperado esa técnica. No uses lo que sepas
del proyecto ni leas los ficheros excluidos.
