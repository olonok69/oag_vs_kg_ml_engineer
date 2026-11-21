#!/usr/bin/env python3
"""Record Claude's final answer for a technique so /demo-compare can score it.

    python demo/record_answer.py <technique> "SST-4280, SST-4472 ..." [--tool-calls N] [--tokens N]

technique: naive_rag | agentic_rag | graphrag | oag
For agentic_rag this is also the retrieval result (Claude did the retrieval itself).
"""
from __future__ import annotations

import argparse
import json
import os

import lib


def main() -> None:
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("technique", choices=["naive_rag", "agentic_rag", "graphrag", "oag"])
    ap.add_argument("ids", help="ticket ids in the final answer, any separator")
    ap.add_argument("--tool-calls", type=int, default=0, help="tool calls Claude used to retrieve (agentic)")
    ap.add_argument("--tokens", type=int, default=0, help="approx tokens Claude read to retrieve (agentic)")
    a = ap.parse_args()

    q = lib.load_question()
    found = lib.ticket_ids(a.ids, q)
    s = lib.print_score(q, found)
    payload = {"technique": a.technique, "answer": found, "answer_score": s}
    if a.technique == "agentic_rag":
        path = os.path.join(lib.RUNS, "agentic_rag.json")
        payload.update({"technique": "Agentic RAG", "found": found, "score": s,
                        "context_tokens": a.tokens, "llm_calls_retrieval": a.tool_calls})
        lib.save_run("agentic_rag", payload)
    else:
        path = os.path.join(lib.RUNS, f"{a.technique}.json")
        run = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                run = json.load(f)
        run.update({"answer": found, "answer_score": s})
        lib.save_run(a.technique, run)
    print(f"Guardado en {os.path.relpath(path, lib.ROOT)}")


if __name__ == "__main__":
    main()
