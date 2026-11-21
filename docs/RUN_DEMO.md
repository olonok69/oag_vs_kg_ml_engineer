# How to run the demo in Claude Code

> Versión en castellano: [EJECUTAR_DEMO.md](EJECUTAR_DEMO.md). What to say at each step:
> [DEMO_GUIDE.md](DEMO_GUIDE.md), section 5. What each skill runs under the hood:
> [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md).

This is the cheat sheet for the session: what to prepare in the terminal, how to call each skill inside
Claude Code and what should come out. Every command has been tested on the full corpus.

## 1. Before the session (in the WSL terminal)

```bash
cd /mnt/d/repos3/oag_vs_kg_ml_engineer       # or wherever the repo lives
git pull
uv sync --group embed                        # environment with the semantic layer (without it: uv sync)
source .venv/bin/activate                    # required: the skills call `python`
python demo/oag.py build --q letter-end-runin
python demo/oag.py build --q comment-memo-landscape
python demo/compare.py                       # checks everything answers and warms the cache
claude                                       # Claude Code, from the repo root with the venv active
```

Notes:

- A plain `uv sync` uninstalls the `embed` group. If you will use the semantic layer, always run
  `uv sync --group embed`.
- The first run of the semantic layer downloads the model (about 470 MB) and embeds the corpus: it takes a
  few minutes. `python demo/compare.py` does it before the session; afterwards each query takes seconds.
- The real data must be in `data/` (corpus, graph, `questions.yaml`). See
  [`demo/README.md`](../demo/README.md#datos).

## 2. How to call a skill

Inside Claude Code, a skill is invoked by typing `/` and its name. Typing `/demo` lists all five. Whatever
follows the name is passed as arguments:

```
/demo-oag                                   default question (letter-end-runin), in English
/demo-oag comment-memo-landscape            another question, by its id
/demo-oag letter-end-runin --lang es        the question in plain Spanish, with no code names
```

You can also ask in natural language ("show OAG on the comment memo question"): Claude picks the skill from
its description. In the demo the command is better, so the audience sees what runs.

Each skill runs its script (`python demo/...`), shows the output, answers the question using only what that
technique retrieved and records the answer in `data/runs/<id>/`.

**Permissions.** The first time a skill runs `python demo/...`, Claude Code asks for permission. Choose the
option that approves it and does not ask again for that command in this project: the skills always use the
same form (`python demo/<script>.py`), so one approval covers the whole demo. To set it up beforehand, add
the rule `Bash(python demo/*)` to `permissions.allow` in `.claude/settings.local.json` (a local file, not
committed).

**Clear the context between techniques.** Type `/clear` before each skill. Otherwise Claude remembers what
the previous technique retrieved and the comparison stops being fair.

## 3. The script, command by command

### Question A: rules about a modelled component (OAG wins)

| Command | What it does | What should come out |
|---|---|---|
| `/demo-naive-rag` | 5 chunks by TF-IDF and an answer from them | 8 tickets, recall 71%, precision 62% |
| `/demo-agentic-rag` | Claude searches and reads in a loop (at most 12 calls) | Variable; in the test run, 9 calls, recall 71% |
| `/demo-graphrag` | Neighbours of `get_letter_end` at 1 hop; repeats at 2 hops | 1 hop: 71% / 50%. 2 hops: 100% / 13% (53 tickets) |
| `/demo-oag` | Ontology, `build`, query with schema v1 and v2 | v1: 86% / 35%. v2: 100% / 47% (15 tickets) |

### Question B: exploring an unmodelled area (GraphRAG wins)

| Command | What it does | What should come out |
|---|---|---|
| `/demo-graphrag comment-memo-landscape` | Extractor neighbours at 2 hops and themes (communities) | 83% / 43%, and the area's themes |
| `/demo-oag comment-memo-landscape` | Query with no components | 0 facts: the area is not in the ontology |
| `/demo-naive-rag comment-memo-landscape` (optional) | Top-5 chunks | 3 tickets, recall 10% |

### The question in plain Spanish (optional)

| Command | What it does | What should come out |
|---|---|---|
| `/demo-naive-rag letter-end-runin --lang es` | TF-IDF, then multilingual embeddings | 14%, then 43% |
| `/demo-oag letter-end-runin --lang es` | v2 (no components), v3 (Spanish synonyms) and `--semantic` | 0%, 100% and 100% |
| `/demo-graphrag comment-memo-landscape --lang es` | Seed by name, then by similarity | 0%, then 59% / 25% |

### Close

| Command | What it does | What should come out |
|---|---|---|
| `/demo-compare` | Re-runs the deterministic techniques and reads the recorded answers | Two tables per question (English and plain Spanish) and where each technique wins |

Agentic RAG figures and Claude's final answers change between runs; the scripts' figures do not.

## 4. Without Claude Code

The scripts run on their own, with the same output the skills see:

```bash
python demo/naive_rag.py --q letter-end-runin [--embed] [--lang es]
python demo/graphrag.py --q comment-memo-landscape [--hops 2] [--semantic] [--lang es]
python demo/oag.py query --q letter-end-runin [--schema 1|2|3] [--semantic] [--lang es]
python demo/compare.py
```

## 5. If something fails

| Symptom | Cause | Fix |
|---|---|---|
| Typing `/demo` shows no skills | Claude Code was not started from the repo root | Quit and start `claude` in the repo folder |
| `python: command not found`, or Claude tries `.venv/bin/python` or `uv run` | The venv was not active when `claude` started | Quit, `source .venv/bin/activate` and start `claude` again |
| It asks for permission at every step | Approved only once, or the command was not of the form `python demo/...` | Choose "don't ask again", or the rule in section 2 |
| `The semantic layer needs sentence-transformers` | The `embed` group is missing | `uv sync --group embed` |
| Model download fails | No access to huggingface.co | Try with network, or copy `~/.cache/huggingface` from another machine and use `HF_HUB_OFFLINE=1` |
| `No facts yet` | `build` was not run for that question | `python demo/oag.py build --q <id>` |
| The answer uses things the technique did not retrieve | Context from a previous skill | `/clear` before each skill |
