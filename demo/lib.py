"""Shared helpers for the Naive RAG -> OAG demo.

Every technique script imports this module, so they all share:

- paths to the data in ``data/`` (git-ignored) and to the ontology in ``demo/oag/``;
- the questions in ``data/questions.yaml`` (``list_questions``, ``load_question``);
- the corpus as each technique sees it (``holdout_view``, ``load_corpus``): the reserved files,
  the notes written about the reserved ticket and every passage that mentions it are removed,
  so no technique can score by quoting the answer sheet;
- ticket-id extraction (``ticket_ids``) and scoring against the expected answer (``score``);
- where results go (``save_run`` writes ``data/runs/<question id>/<technique>.json``, which
  ``compare.py`` reads back).
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass

# Repository layout. Everything under DATA comes from the real project and stays out of git.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CORPUS = os.path.join(DATA, "corpus")
GRAPH = os.path.join(DATA, "kg", "output", "graph.json")
QUESTIONS = os.path.join(DATA, "questions.yaml")
RUNS = os.path.join(DATA, "runs")
OAG_DIR = os.path.join(DATA, "oag")
ONTOLOGY = os.path.join(ROOT, "demo", "oag", "ontology.yaml")

# A ticket id: SST-1234 in the real corpus, TKT-123 in the sanitised examples.
TICKET_RE = re.compile(r"(?<![A-Za-z0-9])(?:SST|TKT)-\d{3,5}(?!\d)", re.IGNORECASE)


def utf8_stdout() -> None:
    """Windows consoles default to cp1252; the corpus is UTF-8."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def add_question_arg(ap) -> None:
    """Add ``--q <id>`` to an argparse parser. Defaults to $DEMO_Q, then to the file's ``default``."""
    ap.add_argument("--q", dest="qid", default=os.environ.get("DEMO_Q"),
                    help="question id in data/questions.yaml (default: the file's `default`)")


def add_lang_arg(ap) -> None:
    """Add ``--lang en|es``. ``es`` asks the plain-Spanish version of the question (no code names)."""
    ap.add_argument("--lang", choices=["en", "es"], default="en",
                    help="es: ask in Spanish without code names (pregunta_llana, tema), as a user would")


def spanish_question(q: dict) -> str:
    """The question in plain Spanish: pregunta_llana if the file has it, else pregunta."""
    return (q.get("pregunta_llana") or q["pregunta"]).strip()


def spanish_topic(q: dict) -> str:
    """The topic in plain Spanish (``tema``), used as the graph seed with ``--lang es``."""
    return (q.get("tema") or spanish_question(q)).strip()


def run_key(base: str, lang: str = "en", semantic: bool = False) -> str:
    """Name of the result file for a technique variant.

    Examples: ``naive_rag``, ``naive_rag_sem``, ``naive_rag_es``, ``naive_rag_es_sem``. ``compare.py``
    looks the variants up by these names.
    """
    return base + ("_es" if lang == "es" else "") + ("_sem" if semantic else "")


def list_questions(path: str = QUESTIONS) -> list[dict]:
    """Read every question from ``data/questions.yaml``.

    The file holds either one question or ``questions: [...]`` with an optional ``default`` id.
    Ticket ids are upper-cased and missing lists become empty, so callers can use ``q["holdout"]``,
    ``q["holdout_files"]`` and ``q["esperado"]`` without checks.

    Returns:
        A list of question dicts with the fields of the file plus ``_default``.
    """
    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml is required: uv sync (or pip install pyyaml)")
    if not os.path.exists(path):
        sys.exit(f"No question file at {path}. Copy demo/questions.example.yaml to data/questions.yaml.")
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    qs = doc["questions"] if "questions" in doc else [doc]
    for q in qs:
        q["holdout"] = [h.upper() for h in q.get("holdout", []) or []]
        q["esperado"] = [e.upper() for e in q.get("esperado", []) or []]
        q["holdout_files"] = q.get("holdout_files", []) or []
        q["_default"] = doc.get("default", qs[0]["id"])
    return qs


def load_question(qid: str | None = None, path: str = QUESTIONS) -> dict:
    """Return one question by id, or the default one. Exits with the available ids if not found."""
    qs = list_questions(path)
    want = qid or qs[0]["_default"]
    for q in qs:
        if q["id"] == want:
            return q
    sys.exit(f"No question {want!r}. Available: {', '.join(q['id'] for q in qs)}")


def run_dir(q: dict) -> str:
    """Folder for the results of one question: ``data/runs/<id>/``."""
    return os.path.join(RUNS, q["id"])


def facts_path(q: dict) -> str:
    """Where ``oag.py build`` writes the validated facts of one question."""
    return os.path.join(OAG_DIR, q["id"], "facts.json")


@dataclass
class Doc:
    """One corpus file: its file name (used as the source in every citation) and its text."""
    name: str
    text: str


def holdout_pattern(q: dict | None) -> re.Pattern | None:
    """Regex that finds a mention of a hold-out ticket.

    It matches the full id (``TKT-104``) and also the bare number, because notes often list tickets
    as ``104/157`` or ``(104, 157)``. Returns ``None`` when the question has no hold-out.
    """
    nums = [h.split("-")[-1] for h in (q or {}).get("holdout", [])]
    if not nums:
        return None
    return re.compile(r"(?<![A-Za-z0-9.])(?:(?:SST|TKT)-?)?(?:" + "|".join(nums) + r")(?![0-9])", re.IGNORECASE)


def derived_file(text: str, pat: re.Pattern) -> bool:
    """True if the whole file is a note about the hold-out ticket.

    Such a note is dropped entirely, not just redacted: its frontmatter ``tickets:`` or ``title:``
    names the ticket, or its first Markdown heading does. Only the first 1,500 characters are read.
    """
    head = text[:1500]
    if head.startswith("---"):
        fm = head.split("---", 2)[1] if head.count("---") >= 2 else head
        for line in fm.splitlines():
            if line.lower().startswith(("tickets:", "title:")) and pat.search(line):
                return True
    first = text.lstrip().splitlines()[0] if text.strip() else ""
    return first.startswith("#") and bool(pat.search(first))


def redact(text: str, pat: re.Pattern) -> tuple[str, int]:
    """Drop every passage that mentions the hold-out ticket.

    A passage is a section whose heading names it, a table row, a list item (with its continuation
    lines) or a paragraph. Returns the text and the number of passages dropped.
    """
    lines = text.splitlines()
    out: list[str] = []
    dropped = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        h = re.match(r"(#{1,6})\s", line)
        if h and pat.search(line):            # whole section
            level = len(h.group(1))
            i += 1
            while i < len(lines):
                h2 = re.match(r"(#{1,6})\s", lines[i])
                if h2 and len(h2.group(1)) <= level:
                    break
                i += 1
            dropped += 1
            continue
        if line.lstrip().startswith("|"):     # table row
            if pat.search(line):
                dropped += 1
            else:
                out.append(line)
            i += 1
            continue
        item = re.match(r"(\s*(?:>\s*)*)(?:[-*+]|\d+\.)\s", line)
        if item:                              # list item and its indented continuation
            indent = len(item.group(1)) + 1
            block = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"\s*(?:>\s*)*(?:[-*+]|\d+\.)\s", lines[i]) \
                    and not lines[i].lstrip().startswith(("#", "|")) and len(lines[i]) - len(lines[i].lstrip()) >= indent:
                block.append(lines[i])
                i += 1
            if pat.search("\n".join(block)):
                dropped += 1
            else:
                out.extend(block)
            continue
        if line.strip():                      # paragraph
            block = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,6})\s|\s*(?:>\s*)*(?:[-*+]|\d+\.)\s", lines[i]) \
                    and not lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            if pat.search("\n".join(block)):
                dropped += 1
            else:
                out.extend(block)
            continue
        out.append(line)
        i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), dropped


def holdout_view(q: dict | None = None) -> tuple[list[Doc], dict]:
    """The corpus every technique sees for question ``q``.

    Three rules, applied in order:

    1. files listed in ``holdout_files`` are skipped;
    2. files that are notes about the hold-out ticket are skipped (``derived_file``);
    3. in every other file, each passage that mentions the ticket is removed (``redact``).

    Args:
        q: the question; ``None`` loads the whole corpus.

    Returns:
        ``(docs, report)``. ``report`` lists the skipped files and, per redacted file, how many
        passages were removed. ``holdout.py`` writes it next to the view.
    """
    if not os.path.isdir(CORPUS):
        sys.exit(f"No corpus at {CORPUS}. Copy the .md files into data/corpus/.")
    skip = set(q["holdout_files"]) if q else set()
    pat = holdout_pattern(q)
    docs: list[Doc] = []
    report = {"holdout_files": sorted(skip), "derived_files": [], "redacted": {}}
    for name in sorted(os.listdir(CORPUS)):
        if not name.endswith(".md") or name in skip:
            continue
        with open(os.path.join(CORPUS, name), encoding="utf-8", errors="replace") as f:
            text = f.read()
        if pat and pat.search(text):          # only files that mention the ticket need work
            if derived_file(text, pat):
                report["derived_files"].append(name)
                continue
            text, n = redact(text, pat)
            report["redacted"][name] = n
        docs.append(Doc(name, text))
    return docs, report


def excluded_files(q: dict | None) -> set[str]:
    """Files no technique may read or cite: the hold-out files and the notes derived from them."""
    _, rep = holdout_view(q)
    return set(rep["holdout_files"]) | set(rep["derived_files"])


def load_corpus(q: dict | None = None) -> list[Doc]:
    """The documents of ``holdout_view`` without the report. Used by every technique script."""
    return holdout_view(q)[0]


def ticket_ids(text: str, q: dict | None = None) -> list[str]:
    """Ticket ids in ``text`` in order of first appearance, upper-cased and de-duplicated.

    The hold-out ids of ``q`` are dropped, as a second line of defence after ``holdout_view``.
    """
    hold = set(q["holdout"]) if q else set()
    seen: list[str] = []
    for m in TICKET_RE.findall(text):
        t = m.upper()
        if t not in hold and t not in seen:
            seen.append(t)
    return seen


def score(found: list[str], expected: list[str]) -> dict:
    """Compare returned ticket ids with the expected answer.

    Recall = expected found / expected (what was missed). Precision = expected found / returned
    (the noise). The expected list is a minimum, not a ceiling, so precision is a lower bound.

    Returns:
        ``found`` (how many ids were returned), ``hits``, ``missed``, ``recall`` and ``precision``.
    """
    f, e = set(found), set(expected)
    hit = sorted(f & e)
    return {
        "found": len(f),
        "hits": hit,
        "missed": sorted(e - f),
        "recall": len(hit) / len(e) if e else 0.0,
        "precision": len(hit) / len(f) if f else 0.0,
    }


def approx_tokens(text: str) -> int:
    """Rough token count (characters / 4) of the context a technique would hand to the model."""
    return max(1, len(text) // 4)


def save_run(q: dict, technique: str, payload: dict) -> str:
    """Write a technique's result to ``data/runs/<id>/<technique>.json`` and return the path.

    ``technique`` is a ``run_key`` such as ``oag_v1_es``. ``compare.py`` builds its tables from these
    files, so the payload should carry ``technique``, ``found``, ``score``, ``context_tokens`` and
    ``llm_calls_retrieval``.
    """
    os.makedirs(run_dir(q), exist_ok=True)
    path = os.path.join(run_dir(q), f"{technique}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def print_score(q: dict, found: list[str]) -> dict:
    """Score ``found`` against the question's expected answer, print it and return the score."""
    s = score(found, q["esperado"])
    print(f"\nRecall {s['recall']:.0%} ({len(s['hits'])}/{len(q['esperado'])})"
          f" | precision {s['precision']:.0%} | ids devueltos: {s['found']}")
    print(f"  aciertos: {', '.join(s['hits']) or '-'}")
    print(f"  faltan:   {', '.join(s['missed']) or '-'}")
    return s
