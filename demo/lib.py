"""Shared helpers for the Naive RAG -> OAG demo.

Paths, corpus loading with hold-out, ticket-id extraction and scoring.
All techniques read the same corpus (data/corpus) minus the hold-out: the reserved
files, the notes written about the reserved ticket, and every passage that mentions it
(see holdout_view). Their results are therefore comparable and free of the answer sheet.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CORPUS = os.path.join(DATA, "corpus")
GRAPH = os.path.join(DATA, "kg", "output", "graph.json")
QUESTIONS = os.path.join(DATA, "questions.yaml")
RUNS = os.path.join(DATA, "runs")
OAG_DIR = os.path.join(DATA, "oag")
ONTOLOGY = os.path.join(ROOT, "demo", "oag", "ontology.yaml")

TICKET_RE = re.compile(r"(?<![A-Za-z0-9])(?:SST|TKT)-\d{3,5}(?!\d)", re.IGNORECASE)


def utf8_stdout() -> None:
    """Windows consoles default to cp1252; the corpus is UTF-8."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def add_question_arg(ap) -> None:
    ap.add_argument("--q", dest="qid", default=os.environ.get("DEMO_Q"),
                    help="question id in data/questions.yaml (default: the file's `default`)")


def add_lang_arg(ap) -> None:
    ap.add_argument("--lang", choices=["en", "es"], default="en",
                    help="es: ask in Spanish without code names (pregunta_llana, tema), as a user would")


def spanish_question(q: dict) -> str:
    """The question in plain Spanish: pregunta_llana if the file has it, else pregunta."""
    return (q.get("pregunta_llana") or q["pregunta"]).strip()


def spanish_topic(q: dict) -> str:
    return (q.get("tema") or spanish_question(q)).strip()


def run_key(base: str, lang: str = "en", semantic: bool = False) -> str:
    """naive_rag, naive_rag_sem, naive_rag_es, naive_rag_es_sem, ..."""
    return base + ("_es" if lang == "es" else "") + ("_sem" if semantic else "")


def list_questions(path: str = QUESTIONS) -> list[dict]:
    """All questions. data/questions.yaml holds either one question or `questions: [...]`."""
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
    qs = list_questions(path)
    want = qid or qs[0]["_default"]
    for q in qs:
        if q["id"] == want:
            return q
    sys.exit(f"No question {want!r}. Available: {', '.join(q['id'] for q in qs)}")


def run_dir(q: dict) -> str:
    return os.path.join(RUNS, q["id"])


def facts_path(q: dict) -> str:
    return os.path.join(OAG_DIR, q["id"], "facts.json")


@dataclass
class Doc:
    name: str
    text: str


def holdout_pattern(q: dict | None) -> re.Pattern | None:
    """Matches a hold-out ticket by id (TKT-104) or by bare number in a list (104/157)."""
    nums = [h.split("-")[-1] for h in (q or {}).get("holdout", [])]
    if not nums:
        return None
    return re.compile(r"(?<![A-Za-z0-9.])(?:(?:SST|TKT)-?)?(?:" + "|".join(nums) + r")(?![0-9])", re.IGNORECASE)


def derived_file(text: str, pat: re.Pattern) -> bool:
    """A note written about the hold-out ticket: its frontmatter `tickets:` or its title names it."""
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
    """The corpus every technique sees: hold-out files out, notes about the hold-out ticket out,
    and every passage that mentions it removed from the rest. Returns the docs and a report."""
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
        if pat and pat.search(text):
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
    return holdout_view(q)[0]


def ticket_ids(text: str, q: dict | None = None) -> list[str]:
    """Ticket ids in order of first appearance, hold-out removed."""
    hold = set(q["holdout"]) if q else set()
    seen: list[str] = []
    for m in TICKET_RE.findall(text):
        t = m.upper()
        if t not in hold and t not in seen:
            seen.append(t)
    return seen


def score(found: list[str], expected: list[str]) -> dict:
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
    return max(1, len(text) // 4)


def save_run(q: dict, technique: str, payload: dict) -> str:
    os.makedirs(run_dir(q), exist_ok=True)
    path = os.path.join(run_dir(q), f"{technique}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def print_score(q: dict, found: list[str]) -> dict:
    s = score(found, q["esperado"])
    print(f"\nRecall {s['recall']:.0%} ({len(s['hits'])}/{len(q['esperado'])})"
          f" | precision {s['precision']:.0%} | ids devueltos: {s['found']}")
    print(f"  aciertos: {', '.join(s['hits']) or '-'}")
    print(f"  faltan:   {', '.join(s['missed']) or '-'}")
    return s
