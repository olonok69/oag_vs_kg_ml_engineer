"""English text for build_pptx_oag.py --lang en.

Keys are the Spanish paragraph text exactly as the generator emits it (all runs joined).
A string value replaces the content and keeps marker runs ("▸  ", "“ ", " ”"); a list value
gives one string per run, for paragraphs that mix formats.
"""

_B = "▸  "

PLAIN = {
    "INVESTIGACIÓN · METODOLOGÍA DE AGENTES IA": "RESEARCH · AI AGENT METHODOLOGY",
    "Fuentes: Sharma, Kumar & Li — OG-RAG (arXiv 2412.15235, EMNLP 2025) · docs de Palantir Foundry · L. Huang, \"From RAG to OAG\" (Medium) · reference/KNOWLEDGE_GRAPH.md":
        "Sources: Sharma, Kumar & Li — OG-RAG (arXiv 2412.15235, EMNLP 2025) · Palantir Foundry docs · L. Huang, \"From RAG to OAG\" (Medium) · reference/KNOWLEDGE_GRAPH.md",
    "LA PREGUNTA": "THE QUESTION",
    "¿Es OAG lo que ya hacemos?": "Is OAG what we already do?",
    "OAG vs grafo de tickets · Investigación": "OAG vs the ticket graph · Research",
    "Respuesta corta: primos, no gemelos": "Short answer: cousins, not twins",
    "Lo que nos llevamos": "What we take away",
    "PARTE 1": "PART 1", "PARTE 2": "PART 2", "PARTE 3": "PART 3", "PARTE 4": "PART 4",
    "Qué es OAG": "What OAG is",
    "De recuperar trozos de texto a recuperar hechos tipados según una ontología.":
        "From retrieving text chunks to retrieving typed facts that follow an ontology.",
    "De RAG a OAG": "From RAG to OAG",
    "Tres lecturas del término": "Three readings of the term",
    "Qué es una ontología": "What an ontology is",
    "OG-RAG: el pipeline": "OG-RAG: the pipeline",
    "OG-RAG: resultados y límites": "OG-RAG: results and limits",
    "PARTE 1 · TRES LECTURAS": "PART 1 · THREE READINGS",
    "Un nombre, tres cosas distintas": "One name, three different things",
    "PARTE 1 · CONCEPTOS": "PART 1 · CONCEPTS",
    "Definición": "Definition",
    "Clases": "Classes",
    "Los tipos de cosas del dominio: Ticket, Invariante, Símbolo, Test.":
        "The kinds of things in the domain: Ticket, Invariant, Symbol, Test.",
    "Relaciones": "Relations",
    "Enlaces con nombre: Ticket fixes Símbolo, Invariante guards Símbolo.":
        "Named links: Ticket fixes Symbol, Invariant guards Symbol.",
    "Atributos": "Attributes",
    "Propiedades de cada clase: estado, causa raíz, fichero fuente.":
        "Properties of each class: status, root cause, source file.",
    "Restricciones": "Constraints",
    "«guards» solo sale de un Invariante; todo nodo tiene fichero fuente.":
        "«guards» only starts at an Invariant; every node has a source file.",
    "Esquema + instancias (nuestro dominio)": "Schema + instances (our domain)",
    "# esquema: qué PUEDE existir": "# schema: what CAN exist",
    "# hechos: qué ES verdad hoy": "# facts: what IS true today",
    "PARTE 1 · OG-RAG: RESULTADOS": "PART 1 · OG-RAG: RESULTS",
    "Lo que dicen los números (y lo que no)": "What the numbers say (and what they do not)",
    "Soja": "Soybean", "Trigo": "Wheat", "Noticias": "News",
    "Tabla 1 del paper. «—» = no terminó en un día. Modelos: GPT-4o(-mini), Llama-3.1 8B/70B, temperatura 0.":
        "Table 1 of the paper. «—» = did not finish in a day. Models: GPT-4o(-mini), Llama-3.1 8B/70B, temperature 0.",
    "Titulares del abstract": "Abstract headlines",
    "Letra pequeña": "Small print",
    "Nuestro grafo vs OAG": "Our graph vs OAG",
    "El grafo de tickets construido con graphify, puesto al lado de OG-RAG y Palantir.":
        "The ticket graph built with graphify, side by side with OG-RAG and Palantir.",
    "Recordatorio: cómo funciona": "Recap: how it works",
    "Nuestra pipeline y lo aprendido": "Our pipeline and what we learned",
    "Comparación lado a lado": "Side-by-side comparison",
    "La ontología que ya tenemos sin saberlo": "The ontology we already have without knowing it",
    "Veredicto": "Verdict",
    "PARTE 2 · RECORDATORIO": "PART 2 · RECAP",
    "El grafo de tickets en una slide": "The ticket graph in one slide",
    "Pipeline y consulta": "Pipeline and query",
    "/graphify <scratch>     # subagentes extraen el grafo": "/graphify <scratch>     # subagents extract the graph",
    "/kg <ticket-o-tema>     # explain/path/find, sin LLM": "/kg <ticket-or-topic>   # explain/path/find, no LLM",
    "Corpus → grafo": "Corpus → graph",
    "Valor": "Value",
    "Ficheros / palabras": "Files / words",
    "Nodos · aristas · comunidades": "Nodes · edges · communities",
    "Aristas EXTRACTED / INFERRED": "EXTRACTED / INFERRED edges",
    "Tipos que salieron (emergentes)": "Types that emerged",
    "PARTE 2 · COMPARACIÓN": "PART 2 · COMPARISON",
    "Lado a lado": "Side by side",
    "Dimensión": "Dimension",
    "Nuestro grafo de tickets": "Our ticket graph",
    "Esquema": "Schema",
    "Ontología definida antes (expertos)": "Ontology defined up front (experts)",
    "Ontología de negocio curada": "Curated business ontology",
    "Emergente: lo decide el LLM al extraer": "Emergent: the LLM decides while extracting",
    "Extracción": "Extraction",
    "LLM mapea docs → JSON-LD": "LLM maps docs → JSON-LD",
    "Pipelines + chunks como objetos": "Pipelines + chunks as objects",
    "Subagentes graphify sobre markdown": "graphify subagents over markdown",
    "Representación": "Representation",
    "Hipergrafo de fact blocks": "Hypergraph of fact blocks",
    "Objetos, enlaces, acciones": "Objects, links, actions",
    "Grafo NetworkX, aristas con confianza": "NetworkX graph, edges with confidence",
    "Recuperación": "Retrieval",
    "Set-cover greedy de hiperaristas": "Greedy set cover of hyperedges",
    "Semántica / keyword / híbrida": "Semantic / keyword / hybrid",
    "explain · path · find, deterministas": "explain · path · find, deterministic",
    "Coste por consulta": "Cost per query",
    "0 LLM extra": "0 extra LLM",
    "0 LLM: lee graph.json": "0 LLM: reads graph.json",
    "Salida": "Output",
    "Hechos dentro del prompt": "Facts inside the prompt",
    "Chunks + citas en Workshop": "Chunks + citations in Workshop",
    "Lista de lectura: tickets + zona de peligro": "Reading list: tickets + danger zone",
    "Acciones": "Actions",
    "Sí, tipadas": "Yes, typed",
    "Skills (/kg, /kg-refresh) y gates del método": "Skills (/kg, /kg-refresh) and method gates",
    "PARTE 2 · LO QUE YA TENEMOS": "PART 2 · WHAT WE ALREADY HAVE",
    "Una ontología implícita en las plantillas": "An implicit ontology in the templates",
    "ISSUE_NOTE / <TICKET>.md: síntoma, causa raíz, fix, tests, estado.":
        "ISSUE_NOTE / <TICKET>.md: symptom, root cause, fix, tests, status.",
    "Invariante / sharp edge": "Invariant / sharp edge",
    "SHARP_EDGES.md: «no tocar», con ticket de origen.": "SHARP_EDGES.md: «do not touch», with ticket of origin.",
    "FOLLOWUPS.md: deuda abierta enlazada a su ticket.": "FOLLOWUPS.md: open debt linked to its ticket.",
    "Componente / símbolo": "Component / symbol",
    "Extractores y funciones (get_letter_end…); CodeGraph los conoce.":
        "Extractors and functions (get_letter_end…); CodeGraph knows them.",
    "Test / criterio QA": "Test / QA criterion",
    "TEST_MAP y QA_ACCEPTANCE: qué prueba qué.": "TEST_MAP and QA_ACCEPTANCE: what tests what.",
    "Lección / decisión": "Lesson / decision",
    "PLAYBOOK, memoria y handovers.": "PLAYBOOK, memory and handovers.",
    "El hueco": "The gap",
    "PARTE 2 · VEREDICTO": "PART 2 · VERDICT",
    "¿Cuánto se parece?": "How similar is it?",
    "Igual (≈ la mitad del camino)": "The same (≈ half of the way)",
    "Distinto (lo que falta para ser OAG)": "Different (what is missing to be OAG)",
    "Qué adoptar": "What to adopt",
    "Lo útil de OAG, al tamaño de un equipo pequeño y sin plataforma nueva.":
        "The useful parts of OAG, sized for a small team and with no new platform.",
    "Una ontología mínima": "A minimal ontology",
    "Seis adopciones concretas": "Six concrete adoptions",
    "Hoja de ruta y qué NO hacer": "Roadmap and what NOT to do",
    "Cómo medir si mejora": "How to measure whether it improves",
    "PARTE 3 · ONTOLOGÍA MÍNIMA": "PART 3 · MINIMAL ONTOLOGY",
    "Ocho clases, diez relaciones, un fichero": "Eight classes, ten relations, one file",
    "Esbozo (el detalle se decide con el corpus real)": "Sketch (the detail is decided with the real corpus)",
    "Reglas de diseño": "Design rules",
    "PARTE 3 · ADOPCIONES": "PART 3 · ADOPTIONS",
    "Seis cosas que tomar de OAG": "Six things to take from OAG",
    "Extracción guiada": "Guided extraction",
    "Pasar ontology.yaml a los subagentes de graphify: solo clases y relaciones del esquema.":
        "Pass ontology.yaml to the graphify subagents: only the schema's classes and relations.",
    "Validación en finalize": "Validation in finalize",
    "Comprobación tipo SHACL: rechaza aristas fuera del esquema y nodos sin fuente.":
        "SHACL-style check: reject edges outside the schema and nodes without a source.",
    "Backbone determinista": "Deterministic backbone",
    "Frontmatter YAML en las plantillas + las citas SST-NNNN → hechos sin LLM.":
        "YAML frontmatter in the templates + SST-NNNN citations → facts without an LLM.",
    "/kg facts <tema>": "/kg facts <topic>",
    "Fact blocks mínimos que cubren la consulta (set-cover de OG-RAG), con atribución.":
        "Minimal fact blocks covering the query (OG-RAG set cover), with attribution.",
    "Invariantes como gate": "Invariants as a gate",
    "Antes del merge: invariantes que guardan los símbolos tocados (join con CodeGraph).":
        "Before merging: invariants guarding the touched symbols (join with CodeGraph).",
    "IDs estables": "Stable IDs",
    "Nodos con id de clase + ticket: las etiquetas de comunidad sobreviven al refresh.":
        "Nodes keyed by class + ticket: community labels survive a refresh.",
    "PARTE 3 · HOJA DE RUTA": "PART 3 · ROADMAP",
    "De menos a más, y qué no hacer": "From less to more, and what not to do",
    "Fase A · esquema": "Phase A · schema",
    "Escribir ontology.yaml desde las plantillas. Frontmatter en ticket y sharp edges nuevos.":
        "Write ontology.yaml from the templates. Frontmatter in new tickets and sharp edges.",
    "Fase B · backbone": "Phase B · backbone",
    "Parser determinista de frontmatter + citas. Validación en finalize.":
        "Deterministic parser for frontmatter + citations. Validation in finalize.",
    "Fase C · extracción": "Phase C · extraction",
    "graphify guiado por el esquema; INFERRED solo para lo que el parser no ve.":
        "Schema-guided graphify; INFERRED only for what the parser cannot see.",
    "Fase D · consumo": "Phase D · consumption",
    "/kg facts y el gate de invariantes en el flujo de 11 etapas.":
        "/kg facts and the invariant gate in the 11-stage workflow.",
    "Qué NO adoptar": "What NOT to adopt",
    "PARTE 3 · MEDIR": "PART 3 · MEASURE",
    "Validar el instrumento antes de creerle": "Validate the instrument before trusting it",
    "Set de preguntas con respuesta conocida": "Question set with known answers",
    "Criterio de keep / revert": "Keep / revert criterion",
    "La demo": "The demo",
    "Cinco skills de Claude Code, una pregunta real y la misma vara de medir.":
        "Five Claude Code skills, one real question and the same yardstick.",
    "OAG en la demo": "OAG in the demo",
    "Cómo evaluamos": "How we evaluate",
    "Resultados": "Results",
    "Cuándo usar cada técnica": "When to use each technique",
    "PARTE 4 · RESULTADOS": "PART 4 · RESULTS",
    "Misma pregunta, cuatro técnicas": "Same question, four techniques",
    "Técnica": "Technique",
    "Precisión": "Precision",
    "Tokens de contexto": "Context tokens",
    "LLM al recuperar": "LLM calls during retrieval",
    "GraphRAG (/kg, 1 salto)": "GraphRAG (/kg, 1 hop)",
    "GraphRAG (/kg, 2 saltos)": "GraphRAG (/kg, 2 hops)",
    "mayor": "larger",
    "en directo": "live",
    "variable": "variable",
    "varios pasos": "several steps",
    "Corpus completo: 452 ficheros. Al crecer el corpus, Naive RAG pierde recall y OAG lo mantiene. Respuesta esperada de 7 tickets; una pregunta es una demostración, no una evaluación.":
        "Full corpus: 452 files. As the corpus grows, Naive RAG loses recall and OAG keeps it. Expected answer of 7 tickets; one question is a demonstration, not an evaluation.",
    "Con 14 ficheros (R / P)": "With 14 files (R / P)",
    "~1.600": "~1,600",
    "~7.000": "~7,000",
    "~2.000": "~2,000",
    "CIERRE": "CLOSING",
    "En una frase": "In one sentence",
    "Referencias": "References",
    "Palantir Foundry docs — Ontology augmented generation (palantir.com/docs/foundry/ontology/ontology-augmented-generation).":
        "Palantir Foundry docs — Ontology augmented generation (palantir.com/docs/foundry/ontology/ontology-augmented-generation).",
    "Repo: docs/GUIA_DEMO.md · docs/OAG_VS_KG.md · reference/KNOWLEDGE_GRAPH.md · demo/README.md":
        "Repo: docs/DEMO_GUIDE.md · docs/OAG_VS_KG.md · reference/KNOWLEDGE_GRAPH.md · demo/README.md",
}

BULLETS = {
    "references 286 · relates_to 221": "references 286 · relates_to 221",
    "rationale_for 66 · fixes 59": "rationale_for 66 · fixes 59",
    "semantically_similar_to 22 · conceptually_related_to 18": "semantically_similar_to 22 · conceptually_related_to 18",
    "Mismo objetivo: anclar al agente en conocimiento del dominio estructurado, con fuente citable":
        "Same goal: ground the agent in structured domain knowledge, with a citable source",
    "Mismo truco de coste: la inferencia cara se paga al construir; la consulta no llama al LLM":
        "Same cost trick: expensive inference is paid at build time; the query does not call the LLM",
    "Diferencia clave: OAG define el esquema ANTES (schema-first); nuestro grafo lo deja EMERGER":
        "Key difference: OAG defines the schema FIRST (schema-first); our graph lets it EMERGE",
    "Nuestro grafo se parece más a GraphRAG que a OG-RAG": "Our graph is closer to GraphRAG than to OG-RAG",
    "Nuestras plantillas (ticket, sharp edges, follow-ups) ya son una ontología implícita":
        "Our templates (ticket, sharp edges, follow-ups) are already an implicit ontology",
    "Una ontología mínima y explícita (≈8 clases, ≈10 relaciones)":
        "A minimal, explicit ontology (≈8 classes, ≈10 relations)",
    "Extracción guiada por esa ontología + validación en finalize":
        "Extraction guided by that ontology + validation in finalize",
    "Backbone determinista desde el frontmatter de las plantillas":
        "Deterministic backbone from the templates' frontmatter",
    "/kg facts: fact blocks mínimos con atribución": "/kg facts: minimal fact blocks with attribution",
    "Invariantes como gate antes del merge": "Invariants as a gate before merging",
    "Un set de preguntas con respuesta conocida para medir recall":
        "A set of questions with known answers to measure recall",
    "Visión conceptual, sin método ni números": "Conceptual view, no method and no numbers",
    "Ontología = capa normativa del conocimiento": "Ontology = normative layer of knowledge",
    "Clases, relaciones y axiomas obligatorios (OWL, SHACL)": "Classes, relations and mandatory axioms (OWL, SHACL)",
    "OAG como convergencia de las generaciones de RAG": "OAG as the convergence of the RAG generations",
    "El paper serio: arXiv 2412.15235, EMNLP 2025": "The serious paper: arXiv 2412.15235, EMNLP 2025",
    "Docs → fact blocks JSON-LD mapeados a la ontología": "Docs → JSON-LD fact blocks mapped to the ontology",
    "Hipergrafo + recuperación greedy de hiperaristas": "Hypergraph + greedy hyperedge retrieval",
    "Evaluado contra RAG, RAPTOR y GraphRAG": "Evaluated against RAG, RAPTOR and GraphRAG",
    "Ontología = capa operativa del negocio": "Ontology = operational layer of the business",
    "Objetos, enlaces y acciones tipados": "Typed objects, links and actions",
    "OAG en la práctica: chunks como objetos + búsqueda semántica/híbrida (RRF)":
        "OAG in practice: chunks as objects + semantic/hybrid search (RRF)",
    "El LLM consulta objetos y propone acciones": "The LLM queries objects and proposes actions",
    "La especificación explícita y compartida de un dominio: qué tipos de cosas existen, cómo se relacionan y qué reglas deben cumplir. Escrita para que una máquina pueda usarla y validarla.":
        "The explicit, shared specification of a domain: what kinds of things exist, how they relate and which rules they must satisfy. Written so that a machine can use and validate it.",
    "+55% recall de hechos correctos": "+55% recall of correct facts",
    "+40% corrección de respuesta": "+40% answer correctness",
    "Atribución 30% más rápida": "30% faster attribution",
    "+27% en razonamiento sobre hechos": "+27% on fact-based reasoning",
    "Datos propietarios, dos dominios · ontologías hechas a mano · relevancia de respuesta no siempre mejor (RAPTOR gana en trigo y noticias)":
        "Proprietary data, two domains · hand-made ontologies · answer relevance not always better (RAPTOR wins on wheat and news)",
    "Nodos: document 420 · code 58 · concept 20 · rationale 9": "Nodes: document 420 · code 58 · concept 20 · rationale 9",
    "~75% de las aristas son genéricas (references / relates_to)": "~75% of the edges are generic (references / relates_to)",
    "Las clases existen en las plantillas, pero graphify no las conoce: cada refresh las reinventa (por eso solo <1% de las etiquetas de comunidad sobrevive).":
        "The classes exist in the templates, but graphify does not know them: every refresh reinvents them (which is why <1% of community labels survive).",
    "Conocimiento del dominio como grafo, no como chunks": "Domain knowledge as a graph, not as chunks",
    "Construcción cara una vez; consulta barata y reproducible": "Expensive build once; cheap, reproducible queries",
    "Atribución: cada nodo apunta a su fichero fuente": "Attribution: every node points to its source file",
    "Diseñado para que el agente lo use ANTES de actuar (history-first)":
        "Designed for the agent to use BEFORE acting (history-first)",
    "Honestidad sobre la confianza (EXTRACTED vs INFERRED)": "Honest about confidence (EXTRACTED vs INFERRED)",
    "Sin esquema previo: tipos de nodo y arista genéricos": "No up-front schema: generic node and edge types",
    "Sin restricciones ni validación del grafo": "No constraints and no graph validation",
    "Sin hechos tipados (fixes / regresses / guards / supersedes)": "No typed facts (fixes / regresses / guards / supersedes)",
    "Devuelve qué leer, no los hechos mismos": "Returns what to read, not the facts themselves",
    "Sin acciones ligadas a la ontología": "No actions bound to the ontology",
    "Sale de las plantillas que ya usamos, no de un libro de OWL": "Comes from the templates we already use, not from an OWL textbook",
    "Pequeña: si una relación no responde una pregunta real, fuera": "Small: if a relation does not answer a real question, it goes",
    "Versionada junto a los scripts del KG (va en data/, igual que el grafo)":
        "Versioned with the KG scripts (lives in data/, like the graph)",
    "Relaciones genéricas permitidas, pero marcadas como «pista»": "Generic relations allowed, but marked as «hint»",
    "Cliente → rol en la versión que se comparte fuera": "Client → role in the version shared outside",
    "Una plataforma (Foundry) ni un triplestore OWL: nuestro tamaño no lo justifica":
        "A platform (Foundry) or an OWL triplestore: our size does not justify it",
    "Meter hechos en el prompt en lugar de leer la fuente: el grafo apunta, el writeup manda":
        "Putting facts in the prompt instead of reading the source: the graph points, the writeup rules",
    "Una ontología grande «por completitud»: el coste de mantenerla es el riesgo nº1 de OAG":
        "A large ontology «for completeness»: maintaining it is OAG's number one risk",
    "15–20 preguntas reales: «¿qué tickets tocan get_letter_end?», «¿qué invariante protege X?»":
        "15–20 real questions: «which tickets touch get_letter_end?», «which invariant protects X?»",
    "Respuesta esperada = lista de tickets / invariantes, escrita a mano":
        "Expected answer = list of tickets / invariants, written by hand",
    "Métrica: recall de contexto, como C-Rec en OG-RAG": "Metric: context recall, like C-Rec in OG-RAG",
    "Medir el grafo actual primero: es la línea base": "Measure the current graph first: it is the baseline",
    "Mejora de recall en zonas densas (fin de carta, títulos, numeración)":
        "Recall improves in dense areas (end of letter, titles, numbering)",
    "No empeora en áreas aisladas": "No regression in isolated areas",
    "Coste de refresh igual o menor": "Same or lower refresh cost",
    "Composición, no total: revisar QUÉ tickets faltan, no solo cuántos":
        "Composition, not totals: check WHICH tickets are missing, not just how many",
    "Decir qué no puede mostrar el set (sesgo de quien lo escribe)":
        "State what the set cannot show (the bias of whoever writes it)",
}

QUOTES = {
    "OAG no es un reemplazo: es el siguiente paso natural de nuestra Fase 2.":
        "OAG is not a replacement: it is the natural next step of our Phase 2.",
    "Lo común: un esquema del dominio que el LLM respeta al recuperar, razonar y actuar.":
        "What they share: a domain schema the LLM respects when retrieving, reasoning and acting.",
    "No es una taxonomía ni una lista de etiquetas: es un contrato sobre qué es un hecho válido en el dominio.":
        "It is not a taxonomy or a list of tags: it is a contract on what a valid fact is in the domain.",
    "La ganancia está en el recall de hechos; el precio, construir y mantener la ontología.":
        "The gain is in fact recall; the price is building and maintaining the ontology.",
    "No hay que inventar la ontología: hay que escribir la que las plantillas ya usan.":
        "We do not need to invent the ontology: we need to write down the one the templates already use.",
    "Somos GraphRAG con disciplina de ingeniería; OAG añade el contrato del esquema.":
        "We are GraphRAG with engineering discipline; OAG adds the schema contract.",
    "Cada adopción es pequeña, reversible y medible: encaja con los gates del método.":
        "Each adoption is small, reversible and measurable: it fits the method's gates.",
    "Mismo principio que el método: un gate verde que no puede fallar no prueba nada.":
        "Same principle as the method: a green gate that cannot fail proves nothing.",
    "Naive RAG encuentra las palabras; OAG devuelve los hechos y dice de dónde salen.":
        "Naive RAG finds the words; OAG returns the facts and says where they come from.",
}

# Paragraphs with mixed formatting: one string per run.
RUNS = {
    "¿se parece a nuestro grafo de conocimiento de tickets?": ["does it resemble our ", "ticket knowledge graph", "?"],
    "PARTE 1 — Qué es OAG: de RAG a ontologías · OG-RAG (Microsoft Research) · Palantir Foundry":
        ["PART 1 — ", "What OAG is: from RAG to ontologies · OG-RAG (Microsoft Research) · Palantir Foundry"],
    "PARTE 2 — Nuestro grafo de tickets frente a OAG: qué compartimos y en qué diferimos":
        ["PART 2 — ", "Our ticket graph versus OAG: what we share and where we differ"],
    "PARTE 3 — Qué adoptar: ontología mínima, extracción guiada, fact blocks, gates y cómo medirlo":
        ["PART 3 — ", "What to adopt: minimal ontology, guided extraction, fact blocks, gates and how to measure it"],
    "PARTE 4 — La demo: de Naive RAG a OAG con Claude Code, cómo evaluamos y cuándo usar cada técnica":
        ["PART 4 — ", "The demo: from Naive RAG to OAG with Claude Code, how we evaluate and when to use each technique"],
    "Nuestro grafo ya hace la mitad de OAG. Escribir la ontología que nuestras plantillas usan, y validar el grafo contra ella, es la otra mitad.":
        ["Our graph already does half of OAG. ",
         "Writing down the ontology our templates use, and validating the graph against it, is the other half."],
}

# Text that stays as it is (names, code, numbers).
KEEP = [
    "Ontology-Augmented Generation", "Medium (L. Huang)", "OG-RAG (Microsoft Research)", "Palantir Foundry",
    "Ticket    --fixes-->       Symbol", "Invariant --guards-->      Symbol", "Ticket    --originates-->  Invariant",
    "TKT-104  fixes  get_letter_end", "Context recall", "RAPTOR", "GraphRAG", "OG-RAG",
    "kg_refresh.sh prepare   # manifest → _corpus → scratch", "kg_refresh.sh finalize  # output/ + leak-check",
    "116 / ~196k", "Palantir OAG", "Ticket", "Follow-up", "Recall", "Naive RAG", "Agentic RAG",
    "Embeddings + LLM",
    "# data/knowledge-graph/ontology.yaml", "classes: [Ticket, Invariant, Followup, Component,",
    "          Symbol, Test, Lesson, Decision]", "relations:",
    "  fixes:        Ticket -> Ticket|Symbol", "  regresses:    Ticket -> Ticket",
    "  supersedes:   Ticket|Decision -> Ticket|Decision", "  guards:       Invariant -> Symbol|Component",
    "  originates:   Ticket -> Invariant|Lesson", "  touches:      Ticket -> Symbol|Component",
    "  verified_by:  Ticket|Invariant -> Test", "  blocks / depends_on / follows_up",
    "K. Sharma, P. Kumar, Y. Li — OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for LLMs. arXiv 2412.15235 (2024), EMNLP 2025.",
    "L. Huang — From RAG to OAG (medium.com/@linghuang_76674).",
    "Lewis et al. 2020 (arXiv 2005.11401) · Gao et al. 2023 (arXiv 2312.10997) · Edge et al. 2024, GraphRAG (arXiv 2404.16130) · Singh et al. 2025, Agentic RAG (arXiv 2501.09136)",
]

TRANSLATIONS: dict = {}
TRANSLATIONS.update(PLAIN)
TRANSLATIONS.update({_B + k: v for k, v in BULLETS.items()})
TRANSLATIONS.update({f"“ {k} ”": v for k, v in QUOTES.items()})
TRANSLATIONS.update(RUNS)
TRANSLATIONS.update({k: k for k in KEEP})
