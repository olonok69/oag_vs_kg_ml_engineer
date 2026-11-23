#!/usr/bin/env python3
"""Record Claude's final answer for a technique so /demo-compare can score it.

    python demo/record_answer.py [--q <id>] <technique> "TKT-101, TKT-102 ..." [--tool-calls N] [--tokens N]

technique: naive_rag | agentic_rag | graphrag | oag, or a variant key from data/runs/<id>/
(oag_v3_es, graphrag_es_sem, naive_rag_es_sem...)
For agentic_rag this is also the retrieval result (Claude did the retrieval itself).
"""
from __future__ import annotations

import argparse
import re
import json
import os

import lib


def main() -> None:
    """Score the ids in Claude's answer and store them in the technique's run file.

    For Agentic RAG the answer is also the retrieval result, so a new run file is written with the
    tool calls and tokens Claude reported. For the other techniques the script result already exists
    and the answer is added to it as ``answer`` and ``answer_score``.
    """
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("technique", help="naive_rag, agentic_rag, graphrag, oag or a variant such as oag_v3_es")
    ap.add_argument("ids", help="ticket ids in the final answer, any separator")
    ap.add_argument("--tool-calls", type=int, default=0, help="tool calls Claude used to retrieve (agentic)")
    ap.add_argument("--tokens", type=int, default=0, help="approx tokens Claude read to retrieve (agentic)")
    lib.add_question_arg(ap)
    a = ap.parse_args()
    if not re.fullmatch(r"(naive_rag|agentic_rag|graphrag|oag)[a-z0-9_]*", a.technique):
        ap.error(f"unknown technique {a.technique!r}")

    q = lib.load_question(a.qid)
    found = lib.ticket_ids(a.ids, q)
    s = lib.print_score(q, found)
    payload = {"technique": a.technique, "answer": found, "answer_score": s}
    if a.technique.startswith("agentic_rag"):
        path = os.path.join(lib.run_dir(q), f"{a.technique}.json")
        name = "Agentic RAG" + (" en castellano" if "_es" in a.technique else "")
        payload.update({"technique": name, "found": found, "score": s,
                        "context_tokens": a.tokens, "llm_calls_retrieval": a.tool_calls})
        lib.save_run(q, a.technique, payload)
    else:
        path = os.path.join(lib.run_dir(q), f"{a.technique}.json")
        run = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                run = json.load(f)
        run.update({"answer": found, "answer_score": s})
        lib.save_run(q, a.technique, run)
    print(f"Guardado en {os.path.relpath(path, lib.ROOT)}")


if __name__ == "__main__":
    main()
