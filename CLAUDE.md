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
| `presentacion/build_pptx_oag.py` | Generador del deck (python-pptx). El `.pptx` se regenera desde aquí; no editarlo a mano |
| `demo/` | Scripts de la demo y ontología mínima (`demo/oag/ontology.yaml`) |
| `.claude/skills/demo-*` | Skills de la demo |
| `reference/` | Documentación y scripts del grafo de tickets (copia sanitizada) y plantillas de la metodología |
| `data/` | Datos reales, fuera de git (ver `demo/README.md`) |

## Presentación

```bash
pip install python-pptx
python presentacion/build_pptx_oag.py
soffice --headless --convert-to pdf presentacion/OAG_vs_KG_Presentacion.pptx   # revisión visual
```

Para añadir o cambiar una slide se edita el generador, se regenera y se revisa el render. Los helpers de
estilo (`base`, `cards`, `panel_bullets`, `code`, `table`, `steps`, `takeaway`) mantienen el estilo del
deck.

## Demo

Cinco skills responden a la misma pregunta real sobre el mismo corpus:

1. `/demo-naive-rag`: trozos de texto por similitud.
2. `/demo-agentic-rag`: Claude busca y lee en bucle.
3. `/demo-graphrag`: nuestro skill `/kg` sobre `data/kg/output/graph.json`.
4. `/demo-oag`: hechos tipados validados contra la ontología.
5. `/demo-compare`: recall, precisión y coste.

Preparación:

```bash
pip install -r demo/requirements.txt
python demo/oag.py build     # tras cambiar el corpus o la ontología
```

Origen de los datos: `D:\repos3\ILS_2\document-parser-lambda\data\knowledge-graph\` (`_corpus/` y
`output/graph.json`). La pregunta y la respuesta esperada están en `data/questions.yaml`; el ticket que
sirve de hoja de respuestas se excluye de todas las técnicas (`holdout`).

Durante una skill de la demo, responde solo con lo que haya recuperado esa técnica. No uses lo que sepas
del proyecto ni leas los ficheros excluidos.
