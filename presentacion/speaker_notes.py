"""Speaker notes for build_pptx_oag.py: the presentation script, one entry per slide, in slide order.

Each entry has the slide title (es/en) and the text to say (es/en). The time shown in the script is
estimated from the Spanish text at a calm speaking pace (110 words per minute), without the demo runs.
The generator writes `es` or `en` into the notes of each slide and renders the whole script as
docs/GUION_PRESENTACION.md (ES) and docs/PRESENTATION_SCRIPT.md (EN), so the deck and the guide never
drift apart. Lines that start with "[DEMO]" are actions in Claude Code, not text to read.

Figures are those of the deck (full corpus, 453 files, 450 in question A after the hold-out). If a result changes, change
it here as well.
"""

NOTES = [
    # ------------------------------------------------------------------ 1
    {"title": {"es": "Portada", "en": "Cover"},
     "es": """Buenas. Hoy hablamos de Ontology-Augmented Generation, OAG, y de si tiene sentido para nosotros.

La pregunta de partida es sencilla: ya tenemos un grafo de conocimiento de tickets que usamos con /kg. ¿Es eso OAG? ¿Nos falta algo? ¿Merece la pena?

La sesión tiene cuatro partes: qué es OAG, cómo se compara con nuestro grafo, qué adoptaríamos y una demo en directo con Claude Code. En la demo vamos a ver cinco formas de recuperar información sobre las mismas preguntas reales, desde la más simple, Naive RAG, hasta OAG, y vamos a medir dónde gana cada una.

No vengo a vender OAG. Vengo a enseñar, con datos, dónde ayuda y dónde no.""",
     "en": """Hello. Today we talk about Ontology-Augmented Generation, OAG, and whether it makes sense for us.

The starting question is simple: we already have a ticket knowledge graph that we use through /kg. Is that OAG? Are we missing something? Is it worth it?

The session has four parts: what OAG is, how it compares with our graph, what we would adopt, and a live demo with Claude Code. In the demo we will see five ways of retrieving information for the same real questions, from the simplest, Naive RAG, up to OAG, and we will measure where each one wins.

I am not here to sell OAG. I am here to show, with data, where it helps and where it does not."""},
    # ------------------------------------------------------------------ 2
    {"title": {"es": "¿Es OAG lo que ya hacemos?", "en": "Is OAG what we already do?"},
     "es": """Empiezo por la respuesta corta, para que nadie tenga que esperar al final: OAG y nuestro grafo son primos, no gemelos.

Se parecen en el objetivo, que es anclar al agente en conocimiento del dominio con una fuente que se pueda citar, y en el truco de coste: lo caro se paga al construir el grafo y la consulta no llama a ningún modelo.

La diferencia clave está en el esquema. OAG define antes qué tipos de cosas y de relaciones existen; es lo que llamamos schema-first. Nuestro grafo deja que esos tipos emerjan de lo que el modelo extrae. Por eso nuestro grafo se parece más a GraphRAG que a OAG.

Lo interesante es que nuestras plantillas de tickets, sharp edges y follow-ups ya son una ontología, solo que implícita. A la derecha está lo que nos llevaríamos; lo veremos en la parte 3.""",
     "en": """I start with the short answer, so nobody has to wait for the end: OAG and our graph are cousins, not twins.

They share the goal, which is to ground the agent in domain knowledge with a source it can cite, and the cost trick: the expensive part is paid when the graph is built, and a query calls no model.

The key difference is the schema. OAG defines beforehand which kinds of things and relations exist; we call that schema-first. Our graph lets those types emerge from what the model extracts. That is why our graph is closer to GraphRAG than to OAG.

The interesting part is that our ticket, sharp edges and follow-up templates are already an ontology, only an implicit one. On the right is what we would take; we will see it in part 3."""},
    # ------------------------------------------------------------------ 3
    {"title": {"es": "Parte 1 · Qué es OAG", "en": "Part 1 · What OAG is"},
     "es": """Primera parte: qué es OAG.

La idea en una frase: pasar de recuperar trozos de texto a recuperar hechos con tipo, según una ontología. Vamos a ver de dónde viene, qué significa el término según quién lo use, qué es una ontología y qué dice el paper de referencia, OG-RAG.""",
     "en": """Part one: what OAG is.

The idea in one sentence: moving from retrieving chunks of text to retrieving typed facts, according to an ontology. We will see where it comes from, what the term means depending on who uses it, what an ontology is, and what the reference paper, OG-RAG, says."""},
    # ------------------------------------------------------------------ 4
    {"title": {"es": "De RAG a OAG (diagrama)", "en": "From RAG to OAG (diagram)"},
     "es": """Este diagrama ordena las generaciones de RAG, de izquierda a derecha, de menos a más estructura.

Naive RAG trocea los documentos, los vectoriza y recupera los trozos más parecidos a la pregunta. El rerank añade un segundo modelo que reordena. Modular RAG reescribe la pregunta y combina fuentes. Agentic RAG deja que el agente planifique y busque en bucle. GraphRAG extrae un grafo de entidades y comunidades con un modelo, sin esquema fijo. Y OAG usa una ontología definida antes para guiar la extracción, validar y recuperar.

Fijaos en la fila de abajo, qué recupera cada una: de trozos de texto a hechos con tipo y con fuente.

A la izquierda montar es barato y el modelo interpreta. A la derecha el dominio decide qué es un hecho. Ninguna es mejor en abstracto: depende de la pregunta, y eso es lo que vamos a medir en la demo.""",
     "en": """This diagram lays out the generations of RAG, from left to right, from less to more structure.

Naive RAG chunks the documents, embeds them and retrieves the chunks most similar to the question. Reranking adds a second model that reorders them. Modular RAG rewrites the question and combines sources. Agentic RAG lets the agent plan and search in a loop. GraphRAG extracts a graph of entities and communities with a model, with no fixed schema. And OAG uses an ontology defined beforehand to guide extraction, validation and retrieval.

Look at the bottom row, what each one retrieves: from chunks of text to typed facts with a source.

On the left, setting up is cheap and the model interprets. On the right, the domain decides what a fact is. None is better in the abstract: it depends on the question, and that is what we will measure in the demo."""},
    # ------------------------------------------------------------------ 5
    {"title": {"es": "Un nombre, tres cosas distintas", "en": "One name, three different things"},
     "es": """Cuidado con el término, porque OAG significa cosas distintas según quién lo use.

En el artículo de Medium de Ling Huang es una visión conceptual: la ontología como capa normativa del conocimiento, con OWL y SHACL, pero sin método ni números.

En OG-RAG, de Microsoft Research, es un método concreto y evaluado: los documentos se convierten en fact blocks mapeados a la ontología y se recuperan con un algoritmo voraz. Es el paper serio y el que usamos como referencia.

En Palantir Foundry es una plataforma: la ontología es la capa operativa del negocio, con objetos, enlaces y acciones, y el modelo consulta objetos y propone acciones.

Lo común a las tres está abajo: un esquema del dominio que el modelo respeta al recuperar, al razonar y al actuar.""",
     "en": """Careful with the term, because OAG means different things depending on who uses it.

In Ling Huang's Medium article it is a conceptual view: the ontology as the normative layer of knowledge, with OWL and SHACL, but with no method or numbers.

In OG-RAG, from Microsoft Research, it is a concrete, evaluated method: documents become fact blocks mapped to the ontology and are retrieved with a greedy algorithm. It is the serious paper and the one we use as reference.

In Palantir Foundry it is a platform: the ontology is the operational layer of the business, with objects, links and actions, and the model queries objects and proposes actions.

What the three share is at the bottom: a domain schema that the model respects when retrieving, reasoning and acting."""},
    # ------------------------------------------------------------------ 6
    {"title": {"es": "Qué es una ontología", "en": "What an ontology is"},
     "es": """¿Qué es una ontología? Es la especificación explícita y compartida de un dominio: qué tipos de cosas existen, cómo se relacionan y qué reglas deben cumplir. Y está escrita para que una máquina pueda usarla y comprobarla.

Tiene cuatro piezas. Clases, los tipos de cosas: ticket, invariante, símbolo, test. Relaciones con nombre: un ticket arregla un símbolo, un invariante protege un símbolo. Atributos, las propiedades de cada clase. Y restricciones, las reglas: por ejemplo, la relación «protege» solo puede salir de un invariante, y todo nodo tiene que tener fichero fuente.

A la derecha está la distinción importante: el esquema dice qué puede existir; los hechos dicen qué es verdad hoy.

Y la frase de abajo: una ontología no es una lista de etiquetas. Es un contrato sobre qué cuenta como hecho válido.""",
     "en": """What is an ontology? It is the explicit, shared specification of a domain: which kinds of things exist, how they relate and which rules they must follow. And it is written so that a machine can use it and check it.

It has four pieces. Classes, the kinds of things: ticket, invariant, symbol, test. Named relations: a ticket fixes a symbol, an invariant guards a symbol. Attributes, the properties of each class. And constraints, the rules: for instance, the "guards" relation can only start from an invariant, and every node must have a source file.

On the right is the important distinction: the schema says what can exist; the facts say what is true today.

And the line at the bottom: an ontology is not a list of tags. It is a contract on what counts as a valid fact."""},
    # ------------------------------------------------------------------ 7
    {"title": {"es": "Esquema y hechos (diagrama)", "en": "Schema and facts (diagram)"},
     "es": """Lo mismo, con nuestro dominio. Los ejemplos están sanitizados.

Arriba, el esquema: cuatro clases, ticket, invariante, componente y test, y las relaciones permitidas entre ellas, cada una con su origen y su destino.

Abajo, los hechos: un ticket toca el componente de fin de carta, otro ticket origina un invariante, ese invariante protege el componente, un test verifica el ticket. Cada hecho cumple el esquema.

Y un detalle que va a ser clave en la demo: los sinónimos. get_letter_end, LETTER_END, «fin de carta» y «end-of-letter» son el mismo componente. Esa lista de sinónimos es lo que permite que una pregunta encuentre el componente, y es la parte que escribe quien conoce el dominio.""",
     "en": """The same thing, with our domain. The examples are sanitized.

At the top, the schema: four classes, ticket, invariant, component and test, and the relations allowed between them, each with its source and its target.

At the bottom, the facts: a ticket touches the letter-end component, another ticket originates an invariant, that invariant guards the component, a test verifies the ticket. Every fact complies with the schema.

And a detail that will be key in the demo: the synonyms. get_letter_end, LETTER_END, "fin de carta" and "end-of-letter" are the same component. That list of synonyms is what lets a question find the component, and it is the part written by whoever knows the domain."""},
    # ------------------------------------------------------------------ 8
    {"title": {"es": "OWL y SHACL", "en": "OWL and SHACL"},
     "es": """Dos siglas que vais a oír siempre que se hable de ontologías: OWL y SHACL. Las dos son estándares del W3C.

OWL sirve para escribir la ontología: clases, propiedades, jerarquías y axiomas, como «todo invariante tiene un ticket de origen». Con OWL, un razonador puede deducir hechos nuevos. Y trabaja en mundo abierto: si falta un dato, no es falso, es desconocido.

SHACL sirve para validar datos contra unas formas: qué tipos de nodo hay, qué relaciones se permiten, qué campos son obligatorios. Trabaja en mundo cerrado: si falta un dato obligatorio, es un error, y devuelve un informe con lo que no cumple.

En nuestra demo no usamos los estándares, sino su idea con herramientas ligeras: un YAML hace de OWL y la validación del script hace de SHACL. Si un día el dominio crece, ese YAML se traduce a los estándares.""",
     "en": """Two acronyms you will always hear when ontologies come up: OWL and SHACL. Both are W3C standards.

OWL is for writing the ontology: classes, properties, hierarchies and axioms, such as "every invariant has a ticket of origin". With OWL, a reasoner can infer new facts. And it works under an open world: if a piece of data is missing, it is not false, it is unknown.

SHACL is for validating data against shapes: which node types exist, which relations are allowed, which fields are required. It works under a closed world: if a required value is missing, that is an error, and it returns a report of what does not conform.

In our demo we do not use the standards, only their idea with light tools: a YAML file plays the role of OWL and the script's validation plays the role of SHACL. If the domain grows one day, that YAML translates to the standards."""},
    # ------------------------------------------------------------------ 9
    {"title": {"es": "El pipeline de OG-RAG (diagrama)", "en": "The OG-RAG pipeline (diagram)"},
     "es": """Así funciona OG-RAG, en cinco pasos.

Uno: expertos escriben o revisan la ontología. Dos: un modelo lee cada documento y lo convierte en fact blocks, pequeños bloques JSON que siguen la ontología; abajo tenéis uno del paper, sobre cultivos. Tres: cada fact block es una hiperarista de un hipergrafo. Cuatro: para recuperar, busca los nodos que encajan con la pregunta y elige con un algoritmo voraz el mínimo conjunto de fact blocks que los cubre. Es un set cover; lo vamos a ver funcionar en la demo. Cinco: esos hechos van al prompt.

Lo importante: el modelo trabaja al construir, no al consultar. La consulta no hace llamadas extra al modelo. En eso se parece a nuestro grafo.""",
     "en": """This is how OG-RAG works, in five steps.

One: experts write or review the ontology. Two: a model reads each document and turns it into fact blocks, small JSON blocks that follow the ontology; at the bottom there is one from the paper, about crops. Three: each fact block is a hyperedge of a hypergraph. Four: to retrieve, it finds the nodes that match the question and greedily picks the smallest set of fact blocks that covers them. It is a set cover; we will see it working in the demo. Five: those facts go into the prompt.

The important point: the model works at build time, not at query time. A query makes no extra calls to the model. That is where it resembles our graph."""},
    # ------------------------------------------------------------------ 10
    {"title": {"es": "Lo que dicen los números (y lo que no)", "en": "What the numbers say (and what they do not)"},
     "es": """Los resultados del paper. La tabla mide recall de contexto: qué parte de los hechos necesarios llega al modelo.

OG-RAG gana con claridad en los dos dominios agrícolas, soja y trigo, frente a RAG clásico, RAPTOR y GraphRAG. En noticias empata con RAPTOR, y GraphRAG ni siquiera terminó en un día.

Los titulares del abstract son llamativos: un 55 % más de recall de hechos, un 40 % más de respuestas correctas y una atribución más rápida.

Pero leed la letra pequeña: datos propietarios, solo dos dominios, ontologías hechas a mano, y la relevancia de la respuesta no siempre mejora.

La conclusión honesta es la de abajo: la ganancia está en recuperar los hechos correctos, y el precio es construir y mantener la ontología. Esa es la cuenta que tenemos que hacer nosotros.""",
     "en": """The paper's results. The table measures context recall: how much of the needed facts reaches the model.

OG-RAG clearly wins on the two agricultural domains, soybean and wheat, against classic RAG, RAPTOR and GraphRAG. On news it ties with RAPTOR, and GraphRAG did not even finish within a day.

The abstract's headlines are striking: 55% more fact recall, 40% more correct answers and faster attribution.

But read the small print: proprietary data, only two domains, hand-made ontologies, and answer relevance does not always improve.

The honest conclusion is the one at the bottom: the gain is in retrieving the right facts, and the price is building and maintaining the ontology. That is the sum we have to do ourselves."""},
    # ------------------------------------------------------------------ 11
    {"title": {"es": "Parte 2 · Nuestro grafo vs OAG", "en": "Part 2 · Our graph vs OAG"},
     "es": """Segunda parte: nuestro grafo de tickets, construido con graphify, puesto al lado de OG-RAG y de Palantir. Primero un recordatorio de cómo funciona y después la comparación.""",
     "en": """Part two: our ticket graph, built with graphify, next to OG-RAG and Palantir. First a reminder of how it works, then the comparison."""},
    # ------------------------------------------------------------------ 12
    {"title": {"es": "El grafo de tickets en una slide", "en": "The ticket graph in one slide"},
     "es": """Nuestro grafo en una slide.

A la izquierda, el flujo: kg_refresh prepara el corpus, graphify lanza subagentes que extraen nodos y aristas, finalize lo deja en output y comprueba que no se filtran datos, y /kg consulta el grafo sin llamar a ningún modelo.

Las cifras son las del grafo actual, el mismo que usa la demo: 453 ficheros y unas 690.000 palabras se convierten en casi 4.000 nodos, unas 8.000 aristas y 213 comunidades. El 93 % de las aristas está extraído directamente del texto; el 7 % es inferido.

Fijaos en los tipos que han salido: conceptos, rationales, símbolos, tickets. Y en las aristas: unos dos tercios son genéricas, del tipo «referencia» o «está relacionado con». Dicen que dos cosas tienen que ver, pero no cómo. Ese es el hueco que una ontología vendría a cubrir.""",
     "en": """Our graph in one slide.

On the left, the flow: kg_refresh prepares the corpus, graphify launches subagents that extract nodes and edges, finalize writes it to output and checks that no data leaks, and /kg queries the graph without calling any model.

The figures are those of the current graph, the same one the demo uses: 453 files and about 690,000 words become almost 4,000 nodes, about 8,000 edges and 213 communities. 93% of the edges are extracted directly from the text; 7% are inferred.

Look at the types that came out: concepts, rationales, symbols, tickets. And at the edges: about two thirds are generic, of the "references" or "relates to" kind. They say that two things are related, but not how. That is the gap an ontology would fill."""},
    # ------------------------------------------------------------------ 13
    {"title": {"es": "La pipeline del grafo (diagrama)", "en": "The graph pipeline (diagram)"},
     "es": """El mismo flujo, en detalle.

Arriba, la construcción con /kg-refresh, que se paga una vez: el manifest elige los ficheros, el corpus los aplana guardando su procedencia, graphify extrae con unos veinte subagentes, después se fusionan identificadores duplicados y por último se nombran las comunidades.

Abajo, la consulta con /kg, que es determinista: un tema, el grafo devuelve vecinos, caminos o coincidencias, la zona de peligro con su comunidad, y al final se lee el writeup. La regla es que el grafo apunta y el writeup manda.

La lección está abajo del todo: sin esquema, cada refresh reinventa los tipos, y por eso casi ningún nombre de comunidad sobrevive de una versión a otra.""",
     "en": """The same flow, in detail.

At the top, the build with /kg-refresh, which is paid once: the manifest picks the files, the corpus flattens them while keeping their provenance, graphify extracts with about twenty subagents, then duplicate identifiers are merged and finally the communities are named.

At the bottom, the query with /kg, which is deterministic: a topic, the graph returns neighbours, paths or matches, the danger zone with its community, and in the end you read the writeup. The rule is that the graph points and the writeup decides.

The lesson is at the very bottom: without a schema, every refresh reinvents the types, and that is why almost no community name survives from one version to the next."""},
    # ------------------------------------------------------------------ 14
    {"title": {"es": "Lado a lado", "en": "Side by side"},
     "es": """La comparación, dimensión a dimensión. No hace falta leer la tabla entera; me quedo con cuatro filas.

Esquema: en OG-RAG y en Palantir se define antes; en el nuestro emerge, lo decide el modelo al extraer. Es la diferencia de fondo.

Recuperación: OG-RAG usa el set cover; nosotros, consultas deterministas sobre el grafo. Las dos son baratas al consultar: cero llamadas al modelo.

Salida: OG-RAG pone los hechos dentro del prompt. Nosotros devolvemos una lista de lectura: qué tickets leer y dónde está la zona de peligro. Es más prudente, pero el agente tiene que leer.

Acciones: Palantir liga acciones tipadas a la ontología. Nosotros tenemos skills y gates en la metodología, que cumplen un papel parecido.""",
     "en": """The comparison, dimension by dimension. No need to read the whole table; I keep four rows.

Schema: in OG-RAG and in Palantir it is defined beforehand; in ours it emerges, the model decides it while extracting. That is the underlying difference.

Retrieval: OG-RAG uses the set cover; we use deterministic queries over the graph. Both are cheap at query time: zero calls to the model.

Output: OG-RAG puts the facts inside the prompt. We return a reading list: which tickets to read and where the danger zone is. It is more cautious, but the agent has to read.

Actions: Palantir ties typed actions to the ontology. We have skills and gates in the methodology, which play a similar role."""},
    # ------------------------------------------------------------------ 15
    {"title": {"es": "Una ontología implícita en las plantillas", "en": "An implicit ontology in the templates"},
     "es": """Aquí está la buena noticia: ya tenemos una ontología, solo que está en las plantillas.

La plantilla de ticket define qué es un ticket: síntoma, causa raíz, fix, tests y estado. SHARP_EDGES define los invariantes, las reglas de «no tocar», cada una con su ticket de origen. FOLLOWUPS, la deuda abierta. Los componentes y símbolos son nuestros extractores y funciones. TEST_MAP dice qué prueba qué. Y las lecciones y decisiones están en el playbook y la memoria.

El hueco es que graphify no conoce estas clases. Cada refresh las reinventa, y por eso menos del 1 % de las etiquetas de comunidad sobrevive.

La frase de abajo resume la propuesta: no hay que inventar la ontología, hay que escribir la que ya usan las plantillas.""",
     "en": """Here is the good news: we already have an ontology, only it lives in the templates.

The ticket template defines what a ticket is: symptom, root cause, fix, tests and status. SHARP_EDGES defines the invariants, the "do not touch" rules, each with its ticket of origin. FOLLOWUPS, the open debt. Components and symbols are our extractors and functions. TEST_MAP says what tests what. And lessons and decisions live in the playbook and memory.

The gap is that graphify does not know these classes. Every refresh reinvents them, and that is why less than 1% of community labels survive.

The line at the bottom sums up the proposal: we do not need to invent the ontology, we need to write down the one the templates already use."""},
    # ------------------------------------------------------------------ 16
    {"title": {"es": "¿Cuánto se parece?", "en": "How similar is it?"},
     "es": """El veredicto.

En lo que somos iguales, que es más o menos la mitad del camino: conocimiento del dominio como grafo y no como trozos; construcción cara una vez y consulta barata y reproducible; cada nodo apunta a su fichero; está pensado para que el agente lo consulte antes de actuar; y somos honestos con la confianza, distinguiendo lo extraído de lo inferido.

En lo que nos falta para ser OAG: no hay esquema previo, así que los tipos son genéricos; no hay validación del grafo; no hay hechos tipados como «arregla», «rompe» o «protege»; devolvemos qué leer, no los hechos; y no hay acciones ligadas a la ontología.

Resumen: somos GraphRAG con disciplina de ingeniería. OAG añade el contrato del esquema.""",
     "en": """The verdict.

Where we are the same, which is roughly half of the way: domain knowledge as a graph, not as chunks; expensive build once and cheap, reproducible query; every node points to its file; it is designed for the agent to consult before acting; and we are honest about confidence, telling extracted from inferred.

What we lack to be OAG: there is no prior schema, so types are generic; there is no validation of the graph; there are no typed facts such as "fixes", "breaks" or "guards"; we return what to read, not the facts; and there are no actions tied to the ontology.

Summary: we are GraphRAG with engineering discipline. OAG adds the schema contract."""},
    # ------------------------------------------------------------------ 17
    {"title": {"es": "Parte 3 · Qué adoptar", "en": "Part 3 · What to adopt"},
     "es": """Tercera parte: qué adoptar. Lo útil de OAG, al tamaño de un equipo pequeño y sin plataforma nueva. Veremos una ontología mínima, seis adopciones concretas, la hoja de ruta con lo que no hay que hacer, y cómo medir si mejora.""",
     "en": """Part three: what to adopt. The useful parts of OAG, at the size of a small team and with no new platform. We will see a minimal ontology, six concrete adoptions, the roadmap with what not to do, and how to measure whether it improves."""},
    # ------------------------------------------------------------------ 18
    {"title": {"es": "Ocho clases, diez relaciones, un fichero", "en": "Eight classes, ten relations, one file"},
     "es": """La ontología que proponemos cabe en un fichero: ocho clases y unas diez relaciones. Es un esbozo; el detalle se decide con el corpus real.

Las clases salen de las plantillas: ticket, invariante, follow-up, componente, símbolo, test, lección y decisión. Las relaciones son las que respondemos a diario: qué arregla qué, qué rompe qué, qué sustituye a qué, qué invariante protege qué símbolo, qué test lo verifica.

Las reglas de diseño importan más que la lista. Sale de nuestras plantillas, no de un libro de OWL. Es pequeña: si una relación no responde a una pregunta real, fuera. Va versionada con los scripts del grafo. Las relaciones genéricas se permiten, pero marcadas como pista. Y en la versión que sale fuera, los clientes se convierten en roles.""",
     "en": """The ontology we propose fits in one file: eight classes and about ten relations. It is a sketch; the detail is decided with the real corpus.

The classes come from the templates: ticket, invariant, follow-up, component, symbol, test, lesson and decision. The relations are the ones we answer every day: what fixes what, what breaks what, what supersedes what, which invariant guards which symbol, which test verifies it.

The design rules matter more than the list. It comes from our templates, not from an OWL textbook. It is small: if a relation does not answer a real question, it goes. It is versioned with the graph scripts. Generic relations are allowed, but marked as hints. And in the version shared outside, clients become roles."""},
    # ------------------------------------------------------------------ 19
    {"title": {"es": "Seis cosas que tomar de OAG", "en": "Six things to take from OAG"},
     "es": """Seis adopciones concretas.

Una: extracción guiada. Pasar la ontología a los subagentes de graphify para que solo emitan clases y relaciones del esquema.

Dos: validación en finalize, al estilo SHACL. Rechazar aristas fuera del esquema y nodos sin fuente.

Tres: un backbone determinista. Con frontmatter en las plantillas y las citas a tickets, muchos hechos salen sin modelo.

Cuatro: /kg facts. Devolver los fact blocks mínimos que cubren la consulta, con el set cover de OG-RAG y con su fuente.

Cinco: invariantes como gate antes del merge, cruzando los símbolos tocados con los invariantes que los protegen.

Seis: identificadores estables, para que los nombres de comunidad sobrevivan al refresh.

Cada una es pequeña, reversible y medible: encaja con los gates del método.""",
     "en": """Six concrete adoptions.

One: guided extraction. Pass the ontology to graphify's subagents so they only emit classes and relations from the schema.

Two: validation in finalize, SHACL style. Reject edges outside the schema and nodes without a source.

Three: a deterministic backbone. With frontmatter in the templates and the ticket citations, many facts come out without a model.

Four: /kg facts. Return the minimal fact blocks that cover the query, with OG-RAG's set cover and with their source.

Five: invariants as a gate before merging, crossing the touched symbols with the invariants that guard them.

Six: stable identifiers, so that community names survive the refresh.

Each one is small, reversible and measurable: it fits the method's gates."""},
    # ------------------------------------------------------------------ 20
    {"title": {"es": "De menos a más, y qué no hacer", "en": "From less to more, and what not to do"},
     "es": """La hoja de ruta va de menos a más, en cuatro fases.

Fase A, el esquema: escribir la ontología desde las plantillas y añadir frontmatter a los tickets y sharp edges nuevos. Fase B, el backbone: un parser determinista y la validación en finalize. Fase C, la extracción: graphify guiado por el esquema, dejando la inferencia solo para lo que el parser no ve. Fase D, el consumo: /kg facts y el gate de invariantes dentro del flujo.

Y lo que no hay que hacer, que es igual de importante. No montar una plataforma como Foundry ni un triplestore OWL: nuestro tamaño no lo justifica. No meter hechos en el prompt en lugar de leer la fuente: el grafo apunta y el writeup manda. Y sobre todo, no hacer una ontología grande por completitud. El coste de mantenerla es el riesgo número uno de OAG.""",
     "en": """The roadmap goes from less to more, in four phases.

Phase A, the schema: write the ontology from the templates and add frontmatter to new tickets and sharp edges. Phase B, the backbone: a deterministic parser and validation in finalize. Phase C, extraction: graphify guided by the schema, leaving inference only for what the parser cannot see. Phase D, consumption: /kg facts and the invariants gate inside the flow.

And what not to do, which matters just as much. Do not set up a platform like Foundry or an OWL triplestore: our size does not justify it. Do not put facts in the prompt instead of reading the source: the graph points and the writeup decides. And above all, do not build a large ontology for completeness. The cost of maintaining it is OAG's number one risk."""},
    # ------------------------------------------------------------------ 21
    {"title": {"es": "Validar el instrumento antes de creerle", "en": "Validate the instrument before trusting it"},
     "es": """¿Cómo sabremos si mejora? Midiendo antes de creer.

Necesitamos un set de 15 a 20 preguntas reales con respuesta conocida, del tipo «qué tickets tocan este componente» o «qué invariante protege esto», con la respuesta escrita a mano. La métrica es el recall de contexto, la misma que usa OG-RAG. Y lo primero es medir el grafo actual: es la línea base.

El criterio para quedarnos con el cambio: que mejore el recall en las zonas densas, que no empeore en las áreas aisladas, que el refresh no cueste más, y revisar qué tickets faltan, no solo cuántos. Y decir qué no puede mostrar el set, porque lo escribe alguien con sus sesgos.

Es el mismo principio del método: un gate verde que no puede fallar no prueba nada.

Y con esto pasamos a la demo, que es una versión pequeña de esta evaluación.""",
     "en": """How will we know whether it improves? By measuring before believing.

We need a set of 15 to 20 real questions with a known answer, such as "which tickets touch this component" or "which invariant guards this", with the answer written by hand. The metric is context recall, the same one OG-RAG uses. And the first step is to measure the current graph: that is the baseline.

The criterion for keeping a change: recall improves in dense areas, it does not get worse in isolated areas, the refresh does not cost more, and we review which tickets are missing, not only how many. And we state what the set cannot show, because someone with their own biases writes it.

It is the method's principle: a green gate that cannot fail proves nothing.

And with this we move to the demo, which is a small version of this evaluation."""},
    # ------------------------------------------------------------------ 22
    {"title": {"es": "Parte 4 · La demo", "en": "Part 4 · The demo"},
     "es": """Cuarta parte: la demo. Seis skills de Claude Code, dos preguntas reales y la misma vara de medir para todas.

Veremos cómo funciona OAG en la demo, cómo evaluamos, las dos preguntas con sus ganadores, qué pasa al combinar GraphRAG y OAG, cómo evolucionó la ontología, qué pasa si preguntamos en castellano, y la conclusión: dónde gana cada técnica y si nos merece la pena.""",
     "en": """Part four: the demo. Six Claude Code skills, two real questions and the same yardstick for all of them.

We will see how OAG works in the demo, how we evaluate, the two questions with their winners, what happens when we combine GraphRAG and OAG, how the ontology evolved, what happens if we ask in Spanish, and the conclusion: where each technique wins and whether it is worth it for us."""},
    # ------------------------------------------------------------------ 23
    {"title": {"es": "La demo en Claude Code, paso a paso", "en": "The demo in Claude Code, step by step"},
     "es": """Esto es lo que vamos a ejecutar. Antes de la sesión ya he preparado el entorno: el venv activo, los hechos de OAG construidos y una pasada de la comparativa para tener la caché caliente.

Dentro de Claude Code cada técnica es una skill. Para la pregunta A lanzaré Naive RAG, Agentic RAG, GraphRAG y OAG. Para la B, GraphRAG y OAG. Si hay tiempo, OAG con la pregunta en castellano. Y al final el híbrido y la comparativa.

Dos reglas para que la comparación sea justa: hago /clear antes de cada skill, para que Claude no recuerde lo que encontró la técnica anterior, y cada técnica responde solo con lo que ella ha recuperado.

[DEMO] Cambiar a la terminal con Claude Code abierto en la raíz del repo. Si es la primera ejecución, aprobar «python demo/...» con «no volver a preguntar».""",
     "en": """This is what we are going to run. Before the session I have already prepared the environment: the venv active, the OAG facts built and one pass of the comparison to warm the cache.

Inside Claude Code each technique is a skill. For question A I will run Naive RAG, Agentic RAG, GraphRAG and OAG. For B, GraphRAG and OAG. If there is time, OAG with the question in Spanish. And at the end the hybrid and the comparison.

Two rules to keep the comparison fair: I run /clear before each skill, so Claude does not remember what the previous technique found, and each technique answers only with what it retrieved itself.

[DEMO] Switch to the terminal with Claude Code open at the repo root. On the first run, approve "python demo/..." with "don't ask again"."""},
    # ------------------------------------------------------------------ 24
    {"title": {"es": "OAG en la demo (diagrama)", "en": "OAG in the demo (diagram)"},
     "es": """Así está montado OAG en la demo, en cinco pasos.

Uno: la ontología es un YAML con cuatro clases, seis relaciones, los componentes con sus sinónimos en inglés y en castellano, y las reglas de extracción. Dos: un parser determinista lee el corpus: títulos, tablas de invariantes, citas a tickets, tests y sinónimos. Tres: la validación rechaza lo que el esquema no permite, por ejemplo las menciones genéricas, y lo cuenta en un informe. Cuatro: el resultado son hechos tipados, cada uno con su fichero fuente. Cinco: la consulta asocia la pregunta a un componente por sus sinónimos, aplica el set cover y devuelve fact blocks.

No hay modelo ni al construir ni al consultar. En producción la extracción se completaría con un modelo guiado por la misma ontología, y siempre validado.""",
     "en": """This is how OAG is set up in the demo, in five steps.

One: the ontology is a YAML file with four classes, six relations, the components with their synonyms in English and Spanish, and the extraction rules. Two: a deterministic parser reads the corpus: titles, invariant tables, ticket citations, tests and synonyms. Three: validation rejects what the schema does not allow, for example generic mentions, and counts it in a report. Four: the result is typed facts, each with its source file. Five: the query maps the question to a component through its synonyms, applies the set cover and returns fact blocks.

There is no model at build time or at query time. In production, extraction would be completed by a model guided by the same ontology, and always validated."""},
    # ------------------------------------------------------------------ 25
    {"title": {"es": "Cómo evaluamos (diagrama)", "en": "How we evaluate (diagram)"},
     "es": """Cómo evaluamos.

Pregunta A: un bug real ya resuelto, planteado como si fuera nuevo: hay un fallo en la detección del fin de carta, ¿qué no puedo romper al arreglarlo? La hoja de respuestas es el writeup de ese bug, que lista siete tickets que no había que romper. Ese writeup se excluye de todas las técnicas, para que nadie pueda copiar la respuesta.

Pregunta B: explorar un área, el memo de comentarios. La respuesta esperada sale de una regla objetiva: los writeups cuyo título menciona el área. Son 29.

Medimos dos cosas, y conviene tenerlas claras porque salen en todas las tablas. Recall: de los tickets que había que encontrar, cuántos encuentra la técnica; mide lo que se deja fuera. Precisión: de lo que devuelve, cuánto está en la lista de referencia; mide el ruido. Un ejemplo de la pregunta A: si una técnica devuelve 53 tickets y entre ellos están los 7 de referencia, tiene un recall del 100 % y una precisión del 13 %. Es como pescar con una red enorme: sacas todos los peces que buscabas, pero con mucho más. Y la lista de referencia es un mínimo, así que un ticket de más no siempre es ruido.

Además medimos el coste, en tokens de contexto y llamadas al modelo.

Una advertencia que repetiré: dos preguntas no son una evaluación. Es una demostración. La evaluación seria es el set de 15 a 20 preguntas.

[DEMO] Pregunta A: /clear y /demo-naive-rag; /clear y /demo-agentic-rag; /clear y /demo-graphrag; /clear y /demo-oag. Comentar cada salida en una frase. En OAG, enseñar lo rechazado por la validación y un fact block completo.""",
     "en": """How we evaluate.

Question A: a real bug that was already fixed, posed as if it were new: there is a failure in letter-end detection, what must I not break while fixing it? The answer key is that bug's writeup, which lists seven tickets that must not break. That writeup is excluded from every technique, so nobody can copy the answer.

Question B: exploring an area, the comment memo. The expected answer comes from an objective rule: the writeups whose title mentions the area. There are 29.

We measure two things, and they are worth getting clear because they appear in every table. Recall: of the tickets that had to be found, how many the technique finds; it measures what is left out. Precision: of what it returns, how much is in the reference list; it measures the noise. An example from question A: if a technique returns 53 tickets and the 7 reference ones are among them, it has 100% recall and 13% precision. It is like fishing with a huge net: you catch every fish you were after, but with a lot more. And the reference list is a minimum, so an extra ticket is not always noise.

We also measure cost, in context tokens and calls to the model.

A warning I will repeat: two questions are not an evaluation. It is a demonstration. The serious evaluation is the set of 15 to 20 questions.

[DEMO] Question A: /clear and /demo-naive-rag; /clear and /demo-agentic-rag; /clear and /demo-graphrag; /clear and /demo-oag. Comment on each output in one sentence. On OAG, show what validation rejected and a full fact block."""},
    # ------------------------------------------------------------------ 26
    {"title": {"es": "Dos preguntas, dos ganadores (diagrama)", "en": "Two questions, two winners (diagram)"},
     "es": """El resumen de las dos preguntas antes de entrar en las tablas.

En la A, reglas sobre un componente que la ontología modela, gana OAG: encuentra los siete tickets esperados en 15 resultados en lugar de 53, y cada uno con su porqué: qué invariante origina, qué componente toca, qué test lo fija.

En la B, un área que la ontología no modela, gana GraphRAG: descubre el área sin que nadie la haya modelado y la agrupa en temas. OAG no devuelve nada, porque no ve lo que su esquema no declara.

Dos preguntas, dos ganadores. Eso es exactamente lo que queríamos enseñar.

[DEMO] Pregunta B: /clear y /demo-graphrag comment-memo-landscape; /clear y /demo-oag comment-memo-landscape. Subrayar que OAG devuelve cero hechos y por qué.""",
     "en": """The summary of the two questions before going into the tables.

On A, rules about a component the ontology models, OAG wins: it finds the seven expected tickets in 15 results instead of 53, and each one with its reason: which invariant it originates, which component it touches, which test pins it.

On B, an area the ontology does not model, GraphRAG wins: it discovers the area without anybody modelling it and groups it into themes. OAG returns nothing, because it does not see what its schema does not declare.

Two questions, two winners. That is exactly what we wanted to show.

[DEMO] Question B: /clear and /demo-graphrag comment-memo-landscape; /clear and /demo-oag comment-memo-landscape. Stress that OAG returns zero facts and why."""},
    # ------------------------------------------------------------------ 27
    {"title": {"es": "Pregunta A: reglas sobre un componente modelado", "en": "Question A: rules about a modelled component"},
     "es": """La pregunta A en detalle. Siete tickets esperados, corpus completo de 453 ficheros.

Naive RAG encuentra cinco de los siete, con buena precisión. GraphRAG a un salto, lo mismo con menos contexto. A dos saltos lo encuentra todo, pero entre 53 tickets: la precisión cae al 13 %. OAG con la primera ontología, seis de siete. Con la ontología corregida, los siete en 15 tickets.

Un matiz importante: por F1, que mezcla recall y precisión, Naive RAG queda casi a la par. Pero se deja dos de los siete, y en una pregunta de «qué no romper», un olvido es una regresión en producción. Aquí el recall pesa más.

La última columna es la versión anterior con solo 14 ficheros: con poco corpus todo parece funcionar. Con el corpus completo es cuando se ven las diferencias.

Y Agentic RAG lo vemos en directo, porque cada ejecución es distinta.""",
     "en": """Question A in detail. Seven expected tickets, full corpus of 453 files.

Naive RAG finds five of the seven, with good precision. GraphRAG at one hop, the same with less context. At two hops it finds everything, but among 53 tickets: precision drops to 13%. OAG with the first ontology, six out of seven. With the corrected ontology, all seven in 15 tickets.

An important nuance: by F1, which mixes recall and precision, Naive RAG is almost on par. But it misses two of the seven, and on a "what not to break" question, a miss is a regression in production. Here recall weighs more.

The last column is the earlier version with only 14 files: with a small corpus everything seems to work. With the full corpus is when the differences show.

And Agentic RAG we see live, because each run is different."""},
    # ------------------------------------------------------------------ 28
    {"title": {"es": "Pregunta B: explorar un área sin modelar", "en": "Question B: exploring an unmodelled area"},
     "es": """La pregunta B. 29 tickets esperados, por una regla objetiva: los writeups cuyo título menciona el área.

Naive RAG acierta los tres que devuelve, pero se queda en el 10 % de recall: cinco trozos no bastan para un área entera. GraphRAG a un salto, el 21 %. A dos saltos, el 83 %, con una precisión razonable, y además agrupa el resultado en temas usando las comunidades del grafo. OAG, cero: la pregunta no menciona ningún componente de su ontología.

No hay que disimularlo: es el límite de la técnica. OAG solo ve lo que su esquema declara. Para cubrir esta área habría que modelarla primero, y eso solo merece la pena si la pregunta se repite.""",
     "en": """Question B. 29 expected tickets, by an objective rule: the writeups whose title mentions the area.

Naive RAG gets right the three it returns, but stays at 10% recall: five chunks are not enough for a whole area. GraphRAG at one hop, 21%. At two hops, 83%, with reasonable precision, and it also groups the result into themes using the graph's communities. OAG, zero: the question mentions no component of its ontology.

We should not hide it: it is the technique's limit. OAG only sees what its schema declares. To cover this area we would have to model it first, and that is only worth it if the question keeps coming back."""},
    # ------------------------------------------------------------------ 29
    {"title": {"es": "Híbrido: GraphRAG propone, la ontología filtra", "en": "Hybrid: GraphRAG proposes, the ontology filters"},
     "es": """La pregunta natural después de ver dos ganadores: ¿y si los combinamos?

Lo probamos de la forma más sencilla. GraphRAG a dos saltos da la lista amplia: mucho recall, poca precisión. Si la pregunta nombra un componente de la ontología, la lista se filtra: primero por clases y relaciones, y después por las reglas. Si no nombra ninguno, se queda la lista del grafo tal cual, y las comunidades que encuentra se proponen para ampliar la ontología; esa propuesta la revisa una persona.

El resultado, contado sin adornos: el híbrido iguala a la mejor técnica en cada pregunta, pero no la supera. En la A el embudo es de 53 candidatos a 22 y de ahí a 15, y el grafo no aportó ningún ticket que OAG no tuviera. En la B es la lista de GraphRAG.

Lo que aporta es no tener que elegir técnica, y una lista de qué modelar después. Su punto débil: si una pregunta de exploración nombra un componente, se filtraría por error.

[DEMO] /clear y /demo-hybrid; después /demo-hybrid comment-memo-landscape. Enseñar el embudo 53, 22, 15 y la propuesta para la ontología.""",
     "en": """The natural question after seeing two winners: what if we combine them?

We tried it in the simplest way. GraphRAG at two hops gives the broad list: high recall, low precision. If the question names an ontology component, the list is filtered: first by classes and relations, then by the rules. If it names none, the graph's list is kept as it is, and the communities it finds are proposed to extend the ontology; a person reviews that proposal.

The result, told plainly: the hybrid matches the best technique on each question, but does not beat it. On A the funnel goes from 53 candidates to 22 and from there to 15, and the graph added no ticket OAG did not already have. On B it is GraphRAG's list.

What it adds is not having to choose a technique, and a list of what to model next. Its weak point: if an exploration question names a component, it would be filtered by mistake.

[DEMO] /clear and /demo-hybrid; then /demo-hybrid comment-memo-landscape. Show the 53, 22, 15 funnel and the proposal for the ontology."""},
    # ------------------------------------------------------------------ 30
    {"title": {"es": "De OAG v1 a v2: el esquema también se depura", "en": "From OAG v1 to v2: the schema gets debugged too"},
     "es": """Una cosa que tengo que contar con honestidad: la ontología que gana en la pregunta A es la segunda versión.

La primera fallaba de dos formas, y las dos eran del esquema, no de la técnica. Uno, ruido: la relación «no romper» traía tickets de otras áreas, como numeración o PDF. La v2 añade una restricción al estilo SHACL: el ticket protegido tiene que compartir componente. Pasa de 17 a 11 tickets sin perder ninguno esperado. Dos, una dependencia sin declarar: la detección del fin de carta usa la función de títulos para mirar el título siguiente, pero la v1 trataba los componentes como islas. La v2 añade la relación «llama a» y recupera el invariante que faltaba: el recall sube del 86 % al 100 %.

La v2 se escribió después de ver el fallo. Es la forma normal de mantener una ontología, pero el resultado solo se puede atribuir a la técnica cuando se valide con preguntas nuevas.

[DEMO] Si no se vio antes: python demo/oag.py query --schema 1 para comparar con la v2.""",
     "en": """Something I have to tell honestly: the ontology that wins on question A is the second version.

The first one failed in two ways, and both were about the schema, not the technique. One, noise: the "must not break" relation brought in tickets from other areas, such as numbering or PDF. v2 adds a SHACL-style constraint: the protected ticket must share the component. It goes from 17 to 11 tickets without losing any expected one. Two, an undeclared dependency: letter-end detection uses the title function to look at the next title, but v1 treated components as islands. v2 adds the "calls" relation and recovers the missing invariant: recall goes from 86% to 100%.

v2 was written after seeing the failure. That is the normal way to maintain an ontology, but the result can only be credited to the technique once it is validated on new questions.

[DEMO] If not shown before: python demo/oag.py query --schema 1 to compare with v2."""},
    # ------------------------------------------------------------------ 31
    {"title": {"es": "La pregunta en castellano", "en": "The question in Spanish"},
     "es": """Una prueba más realista: el corpus está en inglés, pero alguien pregunta en castellano llano y sin nombres de código. Por ejemplo: «hay un fallo en el final de la carta, ¿qué no puedo romper?».

Sin capa semántica caen las tres técnicas deterministas, y en silencio: no avisan de que no han entendido. Naive RAG con palabras se queda en el 14 %. GraphRAG no encuentra ningún nodo que se llame así. OAG no reconoce ningún componente.

Con una capa semántica pequeña cambia mucho. Naive RAG con embeddings multilingües sube al 43 %. GraphRAG llega a la zona correcta, aunque no al nodo central. Y OAG recupera exactamente lo mismo que en inglés, de dos formas: añadiendo seis sinónimos en castellano a la ontología, o eligiendo el componente por significado con un modelo pequeño en CPU. El umbral de ese modelo está calibrado con estas dos preguntas, y lo digo.

La lección: el idioma solo afecta al primer paso, reconocer de qué componente se habla. Después, los hechos son los mismos.

[DEMO] Opcional: /clear y /demo-oag letter-end-runin --lang es.""",
     "en": """A more realistic test: the corpus is in English, but someone asks in plain Spanish, with no code names. For example: "there is a bug at the end of the letter, what must I not break?".

Without a semantic layer the three deterministic techniques fail, and silently: they do not warn that they did not understand. Naive RAG with words stays at 14%. GraphRAG finds no node with that name. OAG recognises no component.

With a small semantic layer it changes a lot. Naive RAG with multilingual embeddings rises to 43%. GraphRAG reaches the right area, though not the central node. And OAG recovers exactly the same as in English, in two ways: adding six Spanish synonyms to the ontology, or choosing the component by meaning with a small model on CPU. That model's threshold is calibrated on these two questions, and I say so.

The lesson: the language only affects the first step, recognising which component is meant. After that, the facts are the same.

[DEMO] Optional: /clear and /demo-oag letter-end-runin --lang es."""},
    # ------------------------------------------------------------------ 32
    {"title": {"es": "Cuándo conviene cada técnica (diagrama)", "en": "When to use each technique (diagram)"},
     "es": """Esta tabla es la guía general, más allá de nuestra demo.

Sin RAG, cuando todo cabe en la ventana del modelo, como un ticket y su writeup. Naive RAG, para preguntas puntuales sobre mucho texto. Rerank o búsqueda híbrida, cuando hay nombres exactos como IDs o funciones. Agentic RAG, para investigar algo nuevo, aceptando más coste y variabilidad. GraphRAG, para relaciones y temas: qué hay alrededor de algo. Y OAG, para hechos tipados, reglas, auditoría y atribución, pagando el precio de escribir y mantener la ontología.

La regla práctica: empezar por lo más simple que responda a las preguntas reales, y medir antes de subir de nivel.

[DEMO] /clear y /demo-compare para enseñar las dos tablas con todas las técnicas.""",
     "en": """This table is the general guide, beyond our demo.

No RAG, when everything fits in the model's window, like one ticket and its writeup. Naive RAG, for one-off questions over a lot of text. Reranking or hybrid search, when there are exact names such as IDs or functions. Agentic RAG, to investigate something new, accepting more cost and variability. GraphRAG, for relations and themes: what is around something. And OAG, for typed facts, rules, auditing and attribution, paying the price of writing and maintaining the ontology.

The practical rule: start with the simplest thing that answers the real questions, and measure before moving up a level.

[DEMO] /clear and /demo-compare to show the two tables with every technique."""},
    # ------------------------------------------------------------------ 33
    {"title": {"es": "Dónde gana cada técnica", "en": "Where each technique wins"},
     "es": """Traducido a nuestras preguntas del día a día.

Si la pregunta es «qué reglas, tickets o tests protegen este componente», OAG: hechos con su porqué, poco ruido y validables antes de llegar al modelo. Si es «qué hay en esta área y cómo se organiza», GraphRAG, nuestro /kg: descubre la estructura sin esquema previo. Si es «dónde se menciona este identificador», Naive RAG o una búsqueda: barato e inmediato. Si es «investiga este problema nuevo», Agentic RAG, sabiendo que es caro y variable. Y cualquiera de ellas, si se pregunta en castellano sin nombres de código, con la capa semántica.

La frase con la que me quedo: OAG no sustituye a GraphRAG, lo completa. Uno descubre la estructura y el otro la fija como contrato.""",
     "en": """Translated into our everyday questions.

If the question is "which rules, tickets or tests guard this component", OAG: facts with their reason, little noise and checkable before reaching the model. If it is "what is in this area and how is it organised", GraphRAG, our /kg: it discovers the structure with no prior schema. If it is "where is this identifier mentioned", Naive RAG or a search: cheap and immediate. If it is "investigate this new problem", Agentic RAG, knowing it is expensive and variable. And any of them, if asked in Spanish without code names, with the semantic layer.

The line I keep: OAG does not replace GraphRAG, it complements it. One discovers the structure and the other pins it down as a contract."""},
    # ------------------------------------------------------------------ 34
    {"title": {"es": "¿Merece la pena?", "en": "Is it worth it?"},
     "es": """¿Merece la pena? Sí, por partes, y solo para las preguntas de reglas.

Lo que ha costado en la demo: una ontología de unas 70 líneas, con cuatro clases, seis relaciones, una restricción y cuatro componentes, que sale en buena parte de las plantillas que ya tenemos. La extracción es determinista, sin llamadas al modelo. Y para preguntar en castellano bastan unos sinónimos o un modelo pequeño.

Lo que no compensa: modelar todo el dominio por completitud; sustituir /kg, porque explorar lo sigue haciendo mejor el grafo; y sacar conclusiones sin un set de 15 a 20 preguntas.

Lo que llevaríamos a la metodología: primero el set de preguntas, de reglas y de exploración; una ontología mínima con sus dependencias; validar el grafo contra el esquema en /kg-refresh; y dos modos en /kg: /kg tema para explorar y /kg facts para las reglas.

Poco esfuerzo y bien acotado.""",
     "en": """Is it worth it? Yes, in parts, and only for the rules questions.

What it cost in the demo: an ontology of about 70 lines, with four classes, six relations, one constraint and four components, largely taken from the templates we already have. Extraction is deterministic, with no calls to the model. And to ask in Spanish a few synonyms or a small model are enough.

What does not pay off: modelling the whole domain for completeness; replacing /kg, because the graph is still better at exploring; and drawing conclusions without a set of 15 to 20 questions.

What we would bring to the methodology: first the question set, with rules and exploration questions; a minimal ontology with its dependencies; validating the graph against the schema in /kg-refresh; and two modes in /kg: /kg topic to explore and /kg facts for the rules.

Small and well-bounded effort."""},
    # ------------------------------------------------------------------ 35
    {"title": {"es": "Cierre", "en": "Close"},
     "es": """Para cerrar, en una frase: nuestro grafo ya hace la mitad de OAG. La otra mitad es escribir la ontología que nuestras plantillas ya usan, y validar el grafo contra ella.

Las referencias están en la slide, y en el repo tenéis la guía de la demo, el informe completo y todo el código, para que cualquiera pueda repetir las pruebas.

Gracias. ¿Preguntas?""",
     "en": """To close, in one sentence: our graph already does half of OAG. The other half is writing down the ontology our templates already use, and validating the graph against it.

The references are on the slide, and the repo has the demo guide, the full report and all the code, so anyone can repeat the tests.

Thank you. Questions?"""},
]
