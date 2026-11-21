# Demo technical guide: what runs and where it lives

> Versión en castellano: [GUIA_TECNICA.md](GUIA_TECNICA.md). Guide to presenting the demo:
> [DEMO_GUIDE.md](DEMO_GUIDE.md). Quick usage reference: [`demo/README.md`](../demo/README.md).

This guide explains, step by step, what each demo skill runs, which file and function holds each step, and what
it reads and writes. It is meant for anyone who wants to change the demo, reproduce it in another repo or take a
piece of it to `/kg` and `/kg-refresh`. Code links point to the line where each function starts in the current
version of the repo.

## 1. Overview

```mermaid
flowchart LR
    Q[data/questions.yaml] --> L[demo/lib.py]
    C[data/corpus/*.md] --> L
    L --> N[naive_rag.py]
    L --> G[graphrag.py]
    L --> O[oag.py]
    K[data/kg/output/graph.json<br/>community_labels.json] --> G
    ON[demo/oag/ontology.yaml] --> O
    O -- build --> F[data/oag/&lt;id&gt;/facts.json]
    F -- query --> O
    N --> R[data/runs/&lt;id&gt;/*.json]
    G --> R
    O --> R
    A[Claude: Grep/Read] -- record_answer.py --> R
    R --> CMP[compare.py] --> MD[data/runs/compare.md]
```

Four techniques read the same corpus and the same question, and each leaves its result in the same format.
`compare.py` runs them again and puts them in a table. No technique calls an LLM to retrieve; the only LLM is
Claude, which in each skill reads what was retrieved and answers.

| Piece | File | What it does |
|---|---|---|
| Shared helpers | [`demo/lib.py`](../demo/lib.py) | Paths, questions, corpus with hold-out, ID extraction, metrics, saving results |
| Naive RAG | [`demo/naive_rag.py`](../demo/naive_rag.py) | Text chunks, TF-IDF (or embeddings) and top-k |
| GraphRAG | [`demo/graphrag.py`](../demo/graphrag.py) | The `/kg` query over `graph.json`: neighbours, reading list and themes |
| OAG | [`demo/oag.py`](../demo/oag.py) | `build`: typed facts validated against the ontology. `query`: set cover of fact blocks |
| Ontology | [`demo/oag/ontology.yaml`](../demo/oag/ontology.yaml) | Classes, relations, constraints, components with synonyms and extraction rules |
| Agentic RAG | [`.claude/skills/demo-agentic-rag/SKILL.md`](../.claude/skills/demo-agentic-rag/SKILL.md) | Claude searches and reads with Grep/Read; records its answer |
| Answer recording | [`demo/record_answer.py`](../demo/record_answer.py) | Saves the IDs Claude gives as its final answer |
| Comparison | [`demo/compare.py`](../demo/compare.py) | Re-runs the deterministic techniques and builds the tables |
| Skills | [`.claude/skills/demo-*`](../.claude/skills/) | Script for each step, for Claude Code |

## 2. Environment and data

**Environment.** [`pyproject.toml`](../pyproject.toml) defines the uv project: `pyyaml` for the demo, the `deck`
group (python-pptx, pillow, cairosvg) by default and the optional `embed` group (sentence-transformers). Without
uv, [`demo/requirements.txt`](../demo/requirements.txt) is enough.

```bash
uv sync && source .venv/bin/activate     # activate before starting claude: the skills call `python`
```

**Data.** Everything real lives in `data/`, which is in [`.gitignore`](../.gitignore). The paths are defined in
[`lib.py`, lines 15-22](../demo/lib.py#L15).

| Path | Origin | Used by |
|---|---|---|
| `data/corpus/*.md` | `/kg`'s `_corpus/` in the lambda repo (452 files after the hold-out) | All four techniques |
| `data/kg/output/graph.json` | `output/graph.json` from `/kg-refresh` | `graphrag.py` |
| `data/kg/output/community_labels.json` | `community_labels.json` from `/kg-refresh` | `graphrag.py` (themes) |
| `data/kg/kg_query.sh` | `/kg` wrapper | `graphrag.py --native` |
| `data/questions.yaml` | hand-written (template: [`demo/questions.example.yaml`](../demo/questions.example.yaml)) | All |
| `data/oag/<id>/facts.json` | `oag.py build` | `oag.py query` |
| `data/runs/<id>/*.json`, `data/runs/compare.md` | each technique and `compare.py` | `compare.py` |

## 3. Questions and hold-out

`data/questions.yaml` holds a `questions:` list and a `default`. Each question has:

| Field | Purpose |
|---|---|
| `id` | Question name; passed with `--q <id>` and names the folders under `data/oag/` and `data/runs/` |
| `scenario` | What kind of question it is (rules or exploration) |
| `pregunta` | The text Claude reads |
| `query` | English search text for Naive RAG and OAG (the corpus is in English) |
| `topic` | OAG seed and, without `graph_topic`, GraphRAG seed |
| `graph_topic` | GraphRAG seed when the node name differs from the topic |
| `holdout`, `holdout_files` | Tickets and files that are the answer key; excluded from everything |
| `esperado` | IDs of the expected answer |
| `esperado_regla` | How the expected answer was obtained, when it comes from a rule |

Functions involved:

- [`add_question_arg`](../demo/lib.py#L36) adds `--q` to every script (the `DEMO_Q` environment variable works
  too).
- [`list_questions`](../demo/lib.py#L41) and [`load_question`](../demo/lib.py#L60) read the file. They accept
  the older single-question format.
- [`load_corpus`](../demo/lib.py#L83) loads `data/corpus/*.md` skipping `holdout_files`.
- [`ticket_ids`](../demo/lib.py#L96) extracts IDs with [`TICKET_RE`](../demo/lib.py#L24) and drops the
  `holdout` ones, so no technique can "score" by quoting the answer key.

The two current questions and why they were chosen are in the
[demo guide, section 5](DEMO_GUIDE.md#the-two-questions).

## 4. Naive RAG

**Skill:** [`/demo-naive-rag`](../.claude/skills/demo-naive-rag/SKILL.md). **Script:**
[`demo/naive_rag.py`](../demo/naive_rag.py).

```bash
python demo/naive_rag.py [--q <id>] [--k 5] [--chunk-words 180] [--overlap 30] [--embed]
```

1. Loads the corpus without the hold-out ([`main`](../demo/naive_rag.py#L70)).
2. Splits each document into 180-word chunks with a 30-word overlap ([`chunk`](../demo/naive_rag.py#L30)).
3. Ranks the chunks by similarity to `query`: pure-Python TF-IDF, deterministic and offline
   ([`tfidf_rank`](../demo/naive_rag.py#L42)), or `all-MiniLM-L6-v2` embeddings with `--embed`
   ([`embed_rank`](../demo/naive_rag.py#L61)).
4. Keeps the top `k` ([line 86](../demo/naive_rag.py#L86)) and prints them with their file and position.
5. Returned = the ticket IDs that appear in those chunks ([line 89](../demo/naive_rag.py#L89)).

Output: `data/runs/<id>/naive_rag.json`. What it shows: the retrieval unit is a text chunk, with no notion of
ticket, component or relation.

## 5. Agentic RAG

**Skill:** [`/demo-agentic-rag`](../.claude/skills/demo-agentic-rag/SKILL.md). There is no retrieval script:
Claude plans, searches with Grep and reads with Read, with at most 12 calls and no access to `data/kg/`,
`data/oag/`, `data/runs/` or the hold-out files. At the end it records its answer:

```bash
python demo/record_answer.py [--q <id>] agentic_rag "<ids>" --tool-calls <n> --tokens <approx>
```

[`record_answer.py`](../demo/record_answer.py#L18) stores the IDs as both the retrieval result and the answer. It
is the only technique whose result changes between runs.

## 6. GraphRAG (our `/kg`)

**Skill:** [`/demo-graphrag`](../.claude/skills/demo-graphrag/SKILL.md). **Script:**
[`demo/graphrag.py`](../demo/graphrag.py).

```bash
python demo/graphrag.py [--q <id>] [--topic <topic>] [--hops 1|2] [--full] [--native]
```

It is the same query `/kg` runs (`kg_query.sh <topic>`, equivalent to `graphify explain`), reimplemented in
Python to apply the hold-out and restrict it to the demo corpus.

1. Loads `graph.json` and drops hold-out nodes and nodes that do not come from the demo corpus
   ([`load_graph`](../demo/graphrag.py#L29)). `--full` uses the whole graph.
2. Resolves the topic to a seed node: exact id or label match, otherwise substring; ties go to the node with
   most edges ([`resolve`](../demo/graphrag.py#L58)).
3. Walks the neighbours breadth-first up to `--hops` hops ([line 100](../demo/graphrag.py#L100)), keeping each
   edge's relation and confidence.
4. Builds the context (seed and neighbours with their source file) and the reading list
   ([lines 115-116](../demo/graphrag.py#L115)).
5. Groups the neighbours into themes with the community names in `community_labels.json`
   ([`community_names`](../demo/graphrag.py#L48), [line 119](../demo/graphrag.py#L119)). That is what answers
   "how do they group into themes" in the exploration question.
6. Prints the relation mix and how many edges are generic (`references`, `relates_to`...).
7. Returned = the ticket IDs in the context.

Output: `data/runs/<id>/graphrag.json` (1 hop) or `graphrag_2h.json` (2 hops). `--native` calls
`data/kg/kg_query.sh` and does not score.

## 7. OAG

**Skill:** [`/demo-oag`](../.claude/skills/demo-oag/SKILL.md). **Script:** [`demo/oag.py`](../demo/oag.py).
**Ontology:** [`demo/oag/ontology.yaml`](../demo/oag/ontology.yaml).

```bash
python demo/oag.py build [--q <id>]              # corpus -> validated facts
python demo/oag.py query [--q <id>] [--schema 1]  # facts that answer the question
```

### 7.1 The ontology

| Section | Content |
|---|---|
| `classes` | `Ticket`, `Invariant`, `Component`, `Test`, with id pattern and required fields |
| `relations` | `touches`, `guards`, `originates`, `verified_by`, `must_not_break` and, since v2, `calls` |
| `constraints` | `must_not_break_same_component` (v2): a "must not break" ticket must share a component with the question |
| `components` | `letter_end_detection`, `title_detection`, `numbering`, `letter_start`, with their synonyms (`alt_labels`) and, in v2, `calls` |
| `extraction` | Mention threshold for `touches` and phrases that mark `must_not_break` |

The `since` field marks which schema version added each relation or constraint. `--schema 1` ignores them and
reproduces the first ontology. The plain-language explanation of v1 and v2 is in the
[demo guide](DEMO_GUIDE.md#from-oag-v1-to-v2-the-schema-gets-debugged-too).

### 7.2 `build`: from the corpus to validated facts

[`build`](../demo/oag.py#L69) walks the corpus and proposes candidate edges, then validates them.

1. **Components** of the ontology as nodes, plus the `calls` edges it declares ([line 87](../demo/oag.py#L87)).
2. **Ticket writeups** (`sst-NNNN__*.md`): the ticket is a node; `touches` if the text names a component at
   least 3 times ([`components_in`](../demo/oag.py#L45)); every other ticket cited on a line yields
   `must_not_break` if the line contains a warning phrase, or `mentions` otherwise
   ([lines 93-104](../demo/oag.py#L93)).
3. **`SHARP_EDGES`**: each row of the invariant index and each `- **TKT-NNN ...**` bullet is an `Invariant`,
   with `originates` from its ticket of origin and `guards` towards the components it names
   ([`parse_invariants`](../demo/oag.py#L54), [line 105](../demo/oag.py#L105)).
4. **Tests**: each cited `tests/test_tkt_NNN_*.py` yields `verified_by` from its ticket
   ([line 115](../demo/oag.py#L115)).
5. **SHACL-style validation** ([line 125](../demo/oag.py#L125)): any edge whose relation is not in the ontology
   (the `mentions`), whose domain or range is not the declared one, or that has no source, is rejected. Nodes
   whose id does not match the pattern or that miss a required field are reported.
6. Writes `data/oag/<id>/facts.json` with nodes, accepted edges and a report (accepted and rejected by reason).
   Zero LLM calls.

### 7.3 `query`: from the question to fact blocks

[`query`](../demo/oag.py#L164):

1. Maps the question (`topic` + `query`) to ontology components through their synonyms. If none matches, there
   are no facts to give: that is what happens in the exploration question.
2. Relevant = invariants that guard those components (`guards`).
3. **v2, `calls`**: follows the dependency to the called component and adds only the invariants that name the
   called symbol (`get_titles`), noting `reached_via` ([lines 177-185](../demo/oag.py#L177)).
4. Tickets that the component's writeups ask not to break (`must_not_break`). **v2, constraint:** they only
   count if they touch the component or originate an invariant that guards it
   ([lines 187-193](../demo/oag.py#L187)).
5. **Greedy set cover**, as in OG-RAG: each ticket is a block covering itself and its invariants; blocks are
   picked until everything relevant is covered ([lines 196-210](../demo/oag.py#L196)).
6. Each fact block carries the ticket, its invariants (text, origin, components, `reached_via`), who names it as
   "must not break", its tests and its source ([line 212](../demo/oag.py#L212)).
7. Returned = subject of each block + origins of its invariants. Tickets that only appear as provenance
   (`named_as_must_not_break_by`) do not count ([line 276](../demo/oag.py#L276)).

Output: `data/runs/<id>/oag.json` (v2) or `oag_v1.json` (v1).

## 8. Metrics and comparison

**Scoring** ([`score`](../demo/lib.py#L107)): recall = expected found / expected; precision = expected found /
returned. F1 is computed in [`compare.py`](../demo/compare.py#L36). Context tokens = characters / 4
([`approx_tokens`](../demo/lib.py#L119)).

**What counts as returned** depends on what each technique asserts: the IDs in the chunks (Naive RAG), those in
the graph context (GraphRAG), the subjects and origins of the fact blocks (OAG) and those Claude gives as its
answer (Agentic RAG). The criterion and its limits are in the
[demo guide, section 6](DEMO_GUIDE.md#6-how-we-evaluate).

**`compare.py`** ([`main`](../demo/compare.py#L62)), for every question or only `--q`:

1. Re-runs Naive RAG, GraphRAG at 1 and 2 hops, OAG v1 and v2 ([lines 72-80](../demo/compare.py#L72)); if there
   are no facts yet, it runs `oag.py build` first.
2. Reads `data/runs/<id>/*.json`, including Agentic RAG and Claude's recorded answers
   ([`table`](../demo/compare.py#L41)).
3. Prints one table per question and saves them to `data/runs/compare.md`.

`record_answer.py` adds Claude's final answer (`answer`, `answer_score`) to each result; it shows in the table's
last column.

## 9. Result format

Each `data/runs/<id>/<technique>.json` has at least:

```json
{
  "technique": "OAG (esquema v2)",
  "found": ["TKT-101", "TKT-102"],
  "score": {"found": 2, "hits": ["TKT-101"], "missed": ["TKT-103"], "recall": 0.5, "precision": 0.5},
  "context_tokens": 2500,
  "llm_calls_retrieval": 0,
  "sources": ["hub__SHARP_EDGES.md"]
}
```

GraphRAG adds `hops` and `themes`; OAG adds `schema` and `components`; a recorded answer adds `answer` and
`answer_score`.

## 10. How to extend it

**Add a question.** Add an entry to `data/questions.yaml` (see the template). For a rules question, write the
expected answer from a writeup and declare it as `holdout`. Then: `python demo/oag.py build --q <id>` and
`python demo/compare.py --q <id>`.

**Add a component to the ontology.** Add its entry under `components:` with `label` and `alt_labels` (and
`calls` if it calls another), rebuild the facts and check in the `build` report which new edges it accepts. That
is what would let OAG answer the exploration question.

**Change the ontology without breaking the comparison.** Mark what is new with `since: <version>` and extend the
`--schema` `choices` in [`oag.py`](../demo/oag.py#L239). The demo can then show the before and after.

**Take it to `/kg`.** The map of which piece goes to which phase (Step 0 and Phases A to D) is in the
[demo guide, section 8](DEMO_GUIDE.md#8-lessons-for-the-methodology-skills) and in
[`HANDOVER.md`](../HANDOVER.md#5-qué-adoptar-plan-accionable).

## 11. Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `No question file at data/questions.yaml` | The question file is missing | Copy `demo/questions.example.yaml` and fill it in |
| `No facts yet` | `build` has not run for that question | `python demo/oag.py build --q <id>` |
| `No node matches ...` | The topic does not exist in the graph | Use `--topic` or `graph_topic` with a node name |
| Results do not change after updating the corpus | Stale facts | Run `build` again for every question |
| Garbled characters on Windows | cp1252 console | The scripts force UTF-8 ([`utf8_stdout`](../demo/lib.py#L27)); use Windows Terminal or WSL |
| `python: command not found` in WSL | venv not activated | `source .venv/bin/activate` before starting `claude` |
| No themes in GraphRAG | `community_labels.json` is missing | Copy it from `/kg-refresh` into `data/kg/output/` |
