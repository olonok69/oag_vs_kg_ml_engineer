# Presentation script

> Versión en castellano: [GUION_PRESENTACION.md](GUION_PRESENTACION.md).

This script is the text to present the deck live or to record it on video. It is the same text the speaker notes of each slide carry in `presentacion/OAG_vs_KG_Presentation_EN.pptx`, so it can be read in presenter view while moving through the slides. It is generated from `presentacion/speaker_notes.py` when the deck is rebuilt; do not edit it by hand.

Lines that start with **[DEMO]** are actions in Claude Code, not text to read. The commands, the setup and what each step should show are in [RUN_DEMO.md](RUN_DEMO.md). For a video, record the demo runs separately and edit them in over those lines.

Approximate length: about 40 minutes of talk at a calm pace, plus about 25 of demo and questions.

## Slide 1 · Cover (1 min)

Hello. Today we talk about Ontology-Augmented Generation, OAG, and whether it makes sense for us.

The starting question is simple: we already have a ticket knowledge graph that we use through /kg. Is that OAG? Are we missing something? Is it worth it?

The session has four parts: what OAG is, how it compares with our graph, what we would adopt, and a live demo with Claude Code. In the demo we will see five ways of retrieving information for the same real questions, from the simplest, Naive RAG, up to OAG, and we will measure where each one wins.

I am not here to sell OAG. I am here to show, with data, where it helps and where it does not.

## Slide 2 · Is OAG what we already do? (1.5 min)

I start with the short answer, so nobody has to wait for the end: OAG and our graph are cousins, not twins.

They share the goal, which is to ground the agent in domain knowledge with a source it can cite, and the cost trick: the expensive part is paid when the graph is built, and a query calls no model.

The key difference is the schema. OAG defines beforehand which kinds of things and relations exist; we call that schema-first. Our graph lets those types emerge from what the model extracts. That is why our graph is closer to GraphRAG than to OAG.

The interesting part is that our ticket, sharp edges and follow-up templates are already an ontology, only an implicit one. On the right is what we would take; we will see it in part 3.

## Slide 3 · Part 1 · What OAG is (0.5 min)

Part one: what OAG is.

The idea in one sentence: moving from retrieving chunks of text to retrieving typed facts, according to an ontology. We will see where it comes from, what the term means depending on who uses it, what an ontology is, and what the reference paper, OG-RAG, says.

## Slide 4 · From RAG to OAG (diagram) (1.5 min)

This diagram lays out the generations of RAG, from left to right, from less to more structure.

Naive RAG chunks the documents, embeds them and retrieves the chunks most similar to the question. Reranking adds a second model that reorders them. Modular RAG rewrites the question and combines sources. Agentic RAG lets the agent plan and search in a loop. GraphRAG extracts a graph of entities and communities with a model, with no fixed schema. And OAG uses an ontology defined beforehand to guide extraction, validation and retrieval.

Look at the bottom row, what each one retrieves: from chunks of text to typed facts with a source.

On the left, setting up is cheap and the model interprets. On the right, the domain decides what a fact is. None is better in the abstract: it depends on the question, and that is what we will measure in the demo.

## Slide 5 · One name, three different things (1 min)

Careful with the term, because OAG means different things depending on who uses it.

In Ling Huang's Medium article it is a conceptual view: the ontology as the normative layer of knowledge, with OWL and SHACL, but with no method or numbers.

In OG-RAG, from Microsoft Research, it is a concrete, evaluated method: documents become fact blocks mapped to the ontology and are retrieved with a greedy algorithm. It is the serious paper and the one we use as reference.

In Palantir Foundry it is a platform: the ontology is the operational layer of the business, with objects, links and actions, and the model queries objects and proposes actions.

What the three share is at the bottom: a domain schema that the model respects when retrieving, reasoning and acting.

## Slide 6 · What an ontology is (1 min)

What is an ontology? It is the explicit, shared specification of a domain: which kinds of things exist, how they relate and which rules they must follow. And it is written so that a machine can use it and check it.

It has four pieces. Classes, the kinds of things: ticket, invariant, symbol, test. Named relations: a ticket fixes a symbol, an invariant guards a symbol. Attributes, the properties of each class. And constraints, the rules: for instance, the "guards" relation can only start from an invariant, and every node must have a source file.

On the right is the important distinction: the schema says what can exist; the facts say what is true today.

And the line at the bottom: an ontology is not a list of tags. It is a contract on what counts as a valid fact.

## Slide 7 · Schema and facts (diagram) (1 min)

The same thing, with our domain. The examples are sanitized.

At the top, the schema: four classes, ticket, invariant, component and test, and the relations allowed between them, each with its source and its target.

At the bottom, the facts: a ticket touches the letter-end component, another ticket originates an invariant, that invariant guards the component, a test verifies the ticket. Every fact complies with the schema.

And a detail that will be key in the demo: the synonyms. get_letter_end, LETTER_END, "fin de carta" and "end-of-letter" are the same component. That list of synonyms is what lets a question find the component, and it is the part written by whoever knows the domain.

## Slide 8 · OWL and SHACL (1.5 min)

Two acronyms you will always hear when ontologies come up: OWL and SHACL. Both are W3C standards.

OWL is for writing the ontology: classes, properties, hierarchies and axioms, such as "every invariant has a ticket of origin". With OWL, a reasoner can infer new facts. And it works under an open world: if a piece of data is missing, it is not false, it is unknown.

SHACL is for validating data against shapes: which node types exist, which relations are allowed, which fields are required. It works under a closed world: if a required value is missing, that is an error, and it returns a report of what does not conform.

In our demo we do not use the standards, only their idea with light tools: a YAML file plays the role of OWL and the script's validation plays the role of SHACL. If the domain grows one day, that YAML translates to the standards.

## Slide 9 · The OG-RAG pipeline (diagram) (1 min)

This is how OG-RAG works, in five steps.

One: experts write or review the ontology. Two: a model reads each document and turns it into fact blocks, small JSON blocks that follow the ontology; at the bottom there is one from the paper, about crops. Three: each fact block is a hyperedge of a hypergraph. Four: to retrieve, it finds the nodes that match the question and greedily picks the smallest set of fact blocks that covers them. It is a set cover; we will see it working in the demo. Five: those facts go into the prompt.

The important point: the model works at build time, not at query time. A query makes no extra calls to the model. That is where it resembles our graph.

## Slide 10 · What the numbers say (and what they do not) (1 min)

The paper's results. The table measures context recall: how much of the needed facts reaches the model.

OG-RAG clearly wins on the two agricultural domains, soybean and wheat, against classic RAG, RAPTOR and GraphRAG. On news it ties with RAPTOR, and GraphRAG did not even finish within a day.

The abstract's headlines are striking: 55% more fact recall, 40% more correct answers and faster attribution.

But read the small print: proprietary data, only two domains, hand-made ontologies, and answer relevance does not always improve.

The honest conclusion is the one at the bottom: the gain is in retrieving the right facts, and the price is building and maintaining the ontology. That is the sum we have to do ourselves.

## Slide 11 · Part 2 · Our graph vs OAG (0.5 min)

Part two: our ticket graph, built with graphify, next to OG-RAG and Palantir. First a reminder of how it works, then the comparison.

## Slide 12 · The ticket graph in one slide (1.5 min)

Our graph in one slide.

On the left, the flow: kg_refresh prepares the corpus, graphify launches subagents that extract nodes and edges, finalize writes it to output and checks that no data leaks, and /kg queries the graph without calling any model.

The figures are those of the current graph, the same one the demo uses: 453 files and about 690,000 words become almost 4,000 nodes, about 8,000 edges and 213 communities. 93% of the edges are extracted directly from the text; 7% are inferred.

Look at the types that came out: concepts, rationales, symbols, tickets. And at the edges: about two thirds are generic, of the "references" or "relates to" kind. They say that two things are related, but not how. That is the gap an ontology would fill.

## Slide 13 · The graph pipeline (diagram) (1 min)

The same flow, in detail.

At the top, the build with /kg-refresh, which is paid once: the manifest picks the files, the corpus flattens them while keeping their provenance, graphify extracts with about twenty subagents, then duplicate identifiers are merged and finally the communities are named.

At the bottom, the query with /kg, which is deterministic: a topic, the graph returns neighbours, paths or matches, the danger zone with its community, and in the end you read the writeup. The rule is that the graph points and the writeup decides.

The lesson is at the very bottom: without a schema, every refresh reinvents the types, and that is why almost no community name survives from one version to the next.

## Slide 14 · Side by side (1 min)

The comparison, dimension by dimension. No need to read the whole table; I keep four rows.

Schema: in OG-RAG and in Palantir it is defined beforehand; in ours it emerges, the model decides it while extracting. That is the underlying difference.

Retrieval: OG-RAG uses the set cover; we use deterministic queries over the graph. Both are cheap at query time: zero calls to the model.

Output: OG-RAG puts the facts inside the prompt. We return a reading list: which tickets to read and where the danger zone is. It is more cautious, but the agent has to read.

Actions: Palantir ties typed actions to the ontology. We have skills and gates in the methodology, which play a similar role.

## Slide 15 · An implicit ontology in the templates (1 min)

Here is the good news: we already have an ontology, only it lives in the templates.

The ticket template defines what a ticket is: symptom, root cause, fix, tests and status. SHARP_EDGES defines the invariants, the "do not touch" rules, each with its ticket of origin. FOLLOWUPS, the open debt. Components and symbols are our extractors and functions. TEST_MAP says what tests what. And lessons and decisions live in the playbook and memory.

The gap is that graphify does not know these classes. Every refresh reinvents them, and that is why less than 1% of community labels survive.

The line at the bottom sums up the proposal: we do not need to invent the ontology, we need to write down the one the templates already use.

## Slide 16 · How similar is it? (1 min)

The verdict.

Where we are the same, which is roughly half of the way: domain knowledge as a graph, not as chunks; expensive build once and cheap, reproducible query; every node points to its file; it is designed for the agent to consult before acting; and we are honest about confidence, telling extracted from inferred.

What we lack to be OAG: there is no prior schema, so types are generic; there is no validation of the graph; there are no typed facts such as "fixes", "breaks" or "guards"; we return what to read, not the facts; and there are no actions tied to the ontology.

Summary: we are GraphRAG with engineering discipline. OAG adds the schema contract.

## Slide 17 · Part 3 · What to adopt (0.5 min)

Part three: what to adopt. The useful parts of OAG, at the size of a small team and with no new platform. We will see a minimal ontology, six concrete adoptions, the roadmap with what not to do, and how to measure whether it improves.

## Slide 18 · Eight classes, ten relations, one file (1 min)

The ontology we propose fits in one file: eight classes and about ten relations. It is a sketch; the detail is decided with the real corpus.

The classes come from the templates: ticket, invariant, follow-up, component, symbol, test, lesson and decision. The relations are the ones we answer every day: what fixes what, what breaks what, what supersedes what, which invariant guards which symbol, which test verifies it.

The design rules matter more than the list. It comes from our templates, not from an OWL textbook. It is small: if a relation does not answer a real question, it goes. It is versioned with the graph scripts. Generic relations are allowed, but marked as hints. And in the version shared outside, clients become roles.

## Slide 19 · Six things to take from OAG (1 min)

Six concrete adoptions.

One: guided extraction. Pass the ontology to graphify's subagents so they only emit classes and relations from the schema.

Two: validation in finalize, SHACL style. Reject edges outside the schema and nodes without a source.

Three: a deterministic backbone. With frontmatter in the templates and the ticket citations, many facts come out without a model.

Four: /kg facts. Return the minimal fact blocks that cover the query, with OG-RAG's set cover and with their source.

Five: invariants as a gate before merging, crossing the touched symbols with the invariants that guard them.

Six: stable identifiers, so that community names survive the refresh.

Each one is small, reversible and measurable: it fits the method's gates.

## Slide 20 · From less to more, and what not to do (1.5 min)

The roadmap goes from less to more, in four phases.

Phase A, the schema: write the ontology from the templates and add frontmatter to new tickets and sharp edges. Phase B, the backbone: a deterministic parser and validation in finalize. Phase C, extraction: graphify guided by the schema, leaving inference only for what the parser cannot see. Phase D, consumption: /kg facts and the invariants gate inside the flow.

And what not to do, which matters just as much. Do not set up a platform like Foundry or an OWL triplestore: our size does not justify it. Do not put facts in the prompt instead of reading the source: the graph points and the writeup decides. And above all, do not build a large ontology for completeness. The cost of maintaining it is OAG's number one risk.

## Slide 21 · Validate the instrument before trusting it (1.5 min)

How will we know whether it improves? By measuring before believing.

We need a set of 15 to 20 real questions with a known answer, such as "which tickets touch this component" or "which invariant guards this", with the answer written by hand. The metric is context recall, the same one OG-RAG uses. And the first step is to measure the current graph: that is the baseline.

The criterion for keeping a change: recall improves in dense areas, it does not get worse in isolated areas, the refresh does not cost more, and we review which tickets are missing, not only how many. And we state what the set cannot show, because someone with their own biases writes it.

It is the method's principle: a green gate that cannot fail proves nothing.

And with this we move to the demo, which is a small version of this evaluation.

## Slide 22 · Part 4 · The demo (0.5 min)

Part four: the demo. Six Claude Code skills, two real questions and the same yardstick for all of them.

We will see how OAG works in the demo, how we evaluate, the two questions with their winners, what happens when we combine GraphRAG and OAG, how the ontology evolved, what happens if we ask in Spanish, and the conclusion: where each technique wins and whether it is worth it for us.

## Slide 23 · The demo in Claude Code, step by step (1 min)

This is what we are going to run. Before the session I have already prepared the environment: the venv active, the OAG facts built and one pass of the comparison to warm the cache.

Inside Claude Code each technique is a skill. For question A I will run Naive RAG, Agentic RAG, GraphRAG and OAG. For B, GraphRAG and OAG. If there is time, OAG with the question in Spanish. And at the end the hybrid and the comparison.

Two rules to keep the comparison fair: I run /clear before each skill, so Claude does not remember what the previous technique found, and each technique answers only with what it retrieved itself.

**[DEMO]** Switch to the terminal with Claude Code open at the repo root. On the first run, approve "python demo/..." with "don't ask again".

## Slide 24 · OAG in the demo (diagram) (1 min)

This is how OAG is set up in the demo, in five steps.

One: the ontology is a YAML file with four classes, six relations, the components with their synonyms in English and Spanish, and the extraction rules. Two: a deterministic parser reads the corpus: titles, invariant tables, ticket citations, tests and synonyms. Three: validation rejects what the schema does not allow, for example generic mentions, and counts it in a report. Four: the result is typed facts, each with its source file. Five: the query maps the question to a component through its synonyms, applies the set cover and returns fact blocks.

There is no model at build time or at query time. In production, extraction would be completed by a model guided by the same ontology, and always validated.

## Slide 25 · How we evaluate (diagram) (2 min)

How we evaluate.

Question A: a real bug that was already fixed, posed as if it were new: there is a failure in letter-end detection, what must I not break while fixing it? The answer key is that bug's writeup, which lists seven tickets that must not break. That writeup is excluded from every technique, so nobody can copy the answer.

Question B: exploring an area, the comment memo. The expected answer comes from an objective rule: the writeups whose title mentions the area. There are 29.

We measure two things, and they are worth getting clear because they appear in every table. Recall: of the tickets that had to be found, how many the technique finds; it measures what is left out. Precision: of what it returns, how much is in the reference list; it measures the noise. An example from question A: if a technique returns 53 tickets and the 7 reference ones are among them, it has 100% recall and 13% precision. It is like fishing with a huge net: you catch every fish you were after, but with a lot more. And the reference list is a minimum, so an extra ticket is not always noise.

We also measure cost, in context tokens and calls to the model.

A warning I will repeat: two questions are not an evaluation. It is a demonstration. The serious evaluation is the set of 15 to 20 questions.

**[DEMO]** Question A: /clear and /demo-naive-rag; /clear and /demo-agentic-rag; /clear and /demo-graphrag; /clear and /demo-oag. Comment on each output in one sentence. On OAG, show what validation rejected and a full fact block.

## Slide 26 · Two questions, two winners (diagram) (1 min)

The summary of the two questions before going into the tables.

On A, rules about a component the ontology models, OAG wins: it finds the seven expected tickets in 15 results instead of 53, and each one with its reason: which invariant it originates, which component it touches, which test pins it.

On B, an area the ontology does not model, GraphRAG wins: it discovers the area without anybody modelling it and groups it into themes. OAG returns nothing, because it does not see what its schema does not declare.

Two questions, two winners. That is exactly what we wanted to show.

**[DEMO]** Question B: /clear and /demo-graphrag comment-memo-landscape; /clear and /demo-oag comment-memo-landscape. Stress that OAG returns zero facts and why.

## Slide 27 · Question A: rules about a modelled component (1.5 min)

Question A in detail. Seven expected tickets, full corpus of 452 files.

Naive RAG finds five of the seven, with good precision. GraphRAG at one hop, the same with less context. At two hops it finds everything, but among 53 tickets: precision drops to 13%. OAG with the first ontology, six out of seven. With the corrected ontology, all seven in 15 tickets.

An important nuance: by F1, which mixes recall and precision, Naive RAG is almost on par. But it misses two of the seven, and on a "what not to break" question, a miss is a regression in production. Here recall weighs more.

The last column is the earlier version with only 14 files: with a small corpus everything seems to work. With the full corpus is when the differences show.

And Agentic RAG we see live, because each run is different.

## Slide 28 · Question B: exploring an unmodelled area (1 min)

Question B. 29 expected tickets, by an objective rule: the writeups whose title mentions the area.

Naive RAG gets right the three it returns, but stays at 10% recall: five chunks are not enough for a whole area. GraphRAG at one hop, 21%. At two hops, 83%, with reasonable precision, and it also groups the result into themes using the graph's communities. OAG, zero: the question mentions no component of its ontology.

We should not hide it: it is the technique's limit. OAG only sees what its schema declares. To cover this area we would have to model it first, and that is only worth it if the question keeps coming back.

## Slide 29 · Hybrid: GraphRAG proposes, the ontology filters (1.5 min)

The natural question after seeing two winners: what if we combine them?

We tried it in the simplest way. GraphRAG at two hops gives the broad list: high recall, low precision. If the question names an ontology component, the list is filtered: first by classes and relations, then by the rules. If it names none, the graph's list is kept as it is, and the communities it finds are proposed to extend the ontology; a person reviews that proposal.

The result, told plainly: the hybrid matches the best technique on each question, but does not beat it. On A the funnel goes from 53 candidates to 22 and from there to 15, and the graph added no ticket OAG did not already have. On B it is GraphRAG's list.

What it adds is not having to choose a technique, and a list of what to model next. Its weak point: if an exploration question names a component, it would be filtered by mistake.

**[DEMO]** /clear and /demo-hybrid; then /demo-hybrid comment-memo-landscape. Show the 53, 22, 15 funnel and the proposal for the ontology.

## Slide 30 · From OAG v1 to v2: the schema gets debugged too (1.5 min)

Something I have to tell honestly: the ontology that wins on question A is the second version.

The first one failed in two ways, and both were about the schema, not the technique. One, noise: the "must not break" relation brought in tickets from other areas, such as numbering or PDF. v2 adds a SHACL-style constraint: the protected ticket must share the component. It goes from 17 to 11 tickets without losing any expected one. Two, an undeclared dependency: letter-end detection uses the title function to look at the next title, but v1 treated components as islands. v2 adds the "calls" relation and recovers the missing invariant: recall goes from 86% to 100%.

v2 was written after seeing the failure. That is the normal way to maintain an ontology, but the result can only be credited to the technique once it is validated on new questions.

**[DEMO]** If not shown before: python demo/oag.py query --schema 1 to compare with v2.

## Slide 31 · The question in Spanish (1.5 min)

A more realistic test: the corpus is in English, but someone asks in plain Spanish, with no code names. For example: "there is a bug at the end of the letter, what must I not break?".

Without a semantic layer the three deterministic techniques fail, and silently: they do not warn that they did not understand. Naive RAG with words stays at 14%. GraphRAG finds no node with that name. OAG recognises no component.

With a small semantic layer it changes a lot. Naive RAG with multilingual embeddings rises to 43%. GraphRAG reaches the right area, though not the central node. And OAG recovers exactly the same as in English, in two ways: adding six Spanish synonyms to the ontology, or choosing the component by meaning with a small model on CPU. That model's threshold is calibrated on these two questions, and I say so.

The lesson: the language only affects the first step, recognising which component is meant. After that, the facts are the same.

**[DEMO]** Optional: /clear and /demo-oag letter-end-runin --lang es.

## Slide 32 · When to use each technique (diagram) (1 min)

This table is the general guide, beyond our demo.

No RAG, when everything fits in the model's window, like one ticket and its writeup. Naive RAG, for one-off questions over a lot of text. Reranking or hybrid search, when there are exact names such as IDs or functions. Agentic RAG, to investigate something new, accepting more cost and variability. GraphRAG, for relations and themes: what is around something. And OAG, for typed facts, rules, auditing and attribution, paying the price of writing and maintaining the ontology.

The practical rule: start with the simplest thing that answers the real questions, and measure before moving up a level.

**[DEMO]** /clear and /demo-compare to show the two tables with every technique.

## Slide 33 · Where each technique wins (1 min)

Translated into our everyday questions.

If the question is "which rules, tickets or tests guard this component", OAG: facts with their reason, little noise and checkable before reaching the model. If it is "what is in this area and how is it organised", GraphRAG, our /kg: it discovers the structure with no prior schema. If it is "where is this identifier mentioned", Naive RAG or a search: cheap and immediate. If it is "investigate this new problem", Agentic RAG, knowing it is expensive and variable. And any of them, if asked in Spanish without code names, with the semantic layer.

The line I keep: OAG does not replace GraphRAG, it complements it. One discovers the structure and the other pins it down as a contract.

## Slide 34 · Is it worth it? (1.5 min)

Is it worth it? Yes, in parts, and only for the rules questions.

What it cost in the demo: an ontology of about 70 lines, with four classes, six relations, one constraint and four components, largely taken from the templates we already have. Extraction is deterministic, with no calls to the model. And to ask in Spanish a few synonyms or a small model are enough.

What does not pay off: modelling the whole domain for completeness; replacing /kg, because the graph is still better at exploring; and drawing conclusions without a set of 15 to 20 questions.

What we would bring to the methodology: first the question set, with rules and exploration questions; a minimal ontology with its dependencies; validating the graph against the schema in /kg-refresh; and two modes in /kg: /kg topic to explore and /kg facts for the rules.

Small and well-bounded effort.

## Slide 35 · Close (0.5 min)

To close, in one sentence: our graph already does half of OAG. The other half is writing down the ontology our templates already use, and validating the graph against it.

The references are on the slide, and the repo has the demo guide, the full report and all the code, so anyone can repeat the tests.

Thank you. Questions?
