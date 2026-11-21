#!/usr/bin/env python3
"""Run the deterministic techniques on the same question and compare them.

    python demo/compare.py [--no-run]

Re-runs Naive RAG, GraphRAG (/kg) and OAG, then reads data/runs/*.json
(Agentic RAG and Claude's recorded answers come from /demo-agentic-rag and
record_answer.py). Writes data/runs/compare.md.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import lib

ORDER = [
    ("naive_rag", "Naive RAG", "trozos de texto por similitud"),
    ("agentic_rag", "Agentic RAG", "Claude busca y lee en bucle"),
    ("graphrag", "GraphRAG (/kg)", "vecinos en el grafo + lista de lectura"),
    ("oag", "OAG", "hechos tipados validados contra la ontología"),
]


def run(script: list[str]) -> None:
    subprocess.run([sys.executable, os.path.join(lib.ROOT, "demo", script[0]), *script[1:], "--quiet"],
                   check=True, stdout=subprocess.DEVNULL)


def main() -> None:
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-run", action="store_true", help="only read existing results")
    a = ap.parse_args()
    q = lib.load_question()

    if not a.no_run:
        run(["naive_rag.py"])
        run(["graphrag.py"])
        if not os.path.exists(os.path.join(lib.OAG_DIR, "facts.json")):
            subprocess.run([sys.executable, os.path.join(lib.ROOT, "demo", "oag.py"), "build"],
                           check=True, stdout=subprocess.DEVNULL)
        run(["oag.py", "query"])

    head = "| Técnica | Qué devuelve | Recall | Precisión | IDs | Tokens de contexto | LLM al recuperar | Recall respuesta Claude |"
    rows = [head, "|" + "---|" * 8]
    for key, name, what in ORDER:
        p = os.path.join(lib.RUNS, f"{key}.json")
        if not os.path.exists(p):
            rows.append(f"| {name} | {what} | - | - | - | - | - | sin ejecutar |")
            continue
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        s = r.get("score", {})
        ans = r.get("answer_score")
        llm = r.get("llm_calls_retrieval", 0)
        llm_txt = f"{llm} pasos" if key == "agentic_rag" else str(llm)
        ans_txt = "{:.0%}".format(ans["recall"]) if ans else "-"
        rows.append(f"| {name} | {what} | {s.get('recall', 0):.0%} | {s.get('precision', 0):.0%} | {s.get('found', 0)} "
                    f"| ~{r.get('context_tokens', 0)} | {llm_txt} | {ans_txt} |")
    table = "\n".join(rows)
    print(f"Pregunta: {q['pregunta'].strip()}\n")
    print(f"Respuesta esperada ({len(q['esperado'])}): {', '.join(q['esperado'])}\n")
    print(table)
    print("\nRecall y precisión se miden contra la respuesta esperada escrita a mano. Un ID extra no"
          " siempre es ruido: la lista esperada es un mínimo, no un techo.")
    os.makedirs(lib.RUNS, exist_ok=True)
    with open(os.path.join(lib.RUNS, "compare.md"), "w", encoding="utf-8") as f:
        f.write(f"# Comparativa\n\n{q['pregunta'].strip()}\n\nEsperado: {', '.join(q['esperado'])}\n\n{table}\n")


if __name__ == "__main__":
    main()
