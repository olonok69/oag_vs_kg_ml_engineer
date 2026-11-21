"""Shared helpers for the Naive RAG -> OAG demo.

Paths, corpus loading with hold-out, ticket-id extraction and scoring.
All techniques read the same corpus (data/corpus) minus the hold-out files,
so their results are comparable.
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


def load_question(path: str = QUESTIONS) -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml is required: pip install pyyaml")
    if not os.path.exists(path):
        sys.exit(f"No question file at {path}. Copy demo/questions.example.yaml to data/questions.yaml.")
    with open(path, encoding="utf-8") as f:
        q = yaml.safe_load(f)
    q["holdout"] = [h.upper() for h in q.get("holdout", [])]
    q["esperado"] = [e.upper() for e in q.get("esperado", [])]
    q.setdefault("holdout_files", [])
    return q


@dataclass
class Doc:
    name: str
    text: str


def load_corpus(q: dict | None = None) -> list[Doc]:
    if not os.path.isdir(CORPUS):
        sys.exit(f"No corpus at {CORPUS}. Copy the .md files into data/corpus/.")
    skip = set(q["holdout_files"]) if q else set()
    docs = []
    for name in sorted(os.listdir(CORPUS)):
        if not name.endswith(".md") or name in skip:
            continue
        with open(os.path.join(CORPUS, name), encoding="utf-8", errors="replace") as f:
            docs.append(Doc(name, f.read()))
    return docs


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


def save_run(technique: str, payload: dict) -> str:
    os.makedirs(RUNS, exist_ok=True)
    path = os.path.join(RUNS, f"{technique}.json")
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
