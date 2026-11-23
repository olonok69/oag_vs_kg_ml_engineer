#!/usr/bin/env python3
"""Run the deterministic techniques on each demo question and compare them.

    python demo/compare.py [--q <id>] [--no-run]

For every question in data/questions.yaml (or only --q), re-runs Naive RAG,
GraphRAG (/kg) at one and two hops, OAG with schema v1 and v2 and the hybrid
(demo/hybrid.py), then reads
data/runs/<id>/*.json (Agentic RAG and Claude's recorded answers come from
/demo-agentic-rag and record_answer.py).

A second table asks the same question in plain Spanish (--lang es), first with
word matching only and then with the semantic layer (multilingual embeddings,
demo/semantic.py) or Spanish labels in the ontology (schema v3). The semantic
rows need the `embed` group; without it they show as not run.

Writes data/runs/compare.md.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import lib

# Rows of the main table: (run key in data/runs/<id>/, technique, what it returns).
ORDER = [
    ("naive_rag", "Naive RAG", "trozos de texto por similitud"),
    ("agentic_rag", "Agentic RAG", "Claude busca y lee en bucle"),
    ("graphrag", "GraphRAG (/kg, 1 salto)", "vecinos en el grafo + lista de lectura"),
    ("graphrag_2h", "GraphRAG (/kg, 2 saltos)", "vecindario ampliado"),
    ("oag_v1", "OAG, esquema v1", "hechos tipados, primera ontología"),
    ("oag", "OAG, esquema v2", "hechos tipados, ontología corregida"),
    ("naive_rag_sem", "Naive RAG, embeddings", "trozos por similitud de significado"),
    ("hybrid", "Híbrido GraphRAG + OAG", "GraphRAG propone, la ontología filtra si cubre la pregunta"),
]


def order_es(q: dict) -> list[tuple[str, str, str]]:
    """Rows of the plain-Spanish table. GraphRAG uses the question's ``hops``, so its keys depend on it."""
    g = "graphrag" if q.get("hops", 1) == 1 else f"graphrag_{q['hops']}h"
    h = f"{q.get('hops', 1)} salto{'s' if q.get('hops', 1) > 1 else ''}"
    return [
        ("naive_rag_es", "Naive RAG, TF-IDF", "coincidencia de palabras"),
        ("naive_rag_es_sem", "Naive RAG, embeddings", "similitud de significado"),
        ("agentic_rag_es", "Agentic RAG", "Claude traduce, busca y lee en bucle"),
        (f"{g}_es", f"GraphRAG ({h}), semilla por nombre", "el tema tiene que llamarse como un nodo"),
        (f"{g}_es_sem", f"GraphRAG ({h}), semilla por similitud", "el nodo más parecido al tema"),
        ("oag_es", "OAG v2, etiquetas en inglés", "componentes por coincidencia de palabras"),
        ("oag_v3_es", "OAG v3, etiquetas en castellano", "sinónimos escritos en la ontología"),
        ("oag_es_sem", "OAG v2, componentes por similitud", "componentes por significado"),
    ]


def has_embed() -> bool:
    """True if the ``embed`` group is installed, so the semantic-layer variants can run."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def run(qid: str, script: list[str], check: bool = True) -> bool:
    """Run a technique script for one question with ``--quiet``; it saves its own result.

    ``check=False`` is used for the semantic variants, which may fail without network on first use.
    Returns True if the script exited cleanly.
    """
    r = subprocess.run([sys.executable, os.path.join(lib.ROOT, "demo", script[0]), *script[1:], "--q", qid, "--quiet"],
                       check=check, stdout=subprocess.DEVNULL)
    return r.returncode == 0


def f1(s: dict) -> float:
    """Harmonic mean of recall and precision. Used to sort mentally, not to decide on its own."""
    r, p = s.get("recall", 0), s.get("precision", 0)
    return 2 * r * p / (r + p) if r + p else 0.0


def table(q: dict, order: list[tuple[str, str, str]]) -> str:
    """Markdown table for one question from the saved runs; a missing run shows as not executed."""
    head = ("| Técnica | Qué devuelve | Recall | Precisión | F1 | IDs | Tokens de contexto "
            "| LLM al recuperar | Recall respuesta Claude |")
    rows = [head, "|" + "---|" * 9]
    for key, name, what in order:
        p = os.path.join(lib.run_dir(q), f"{key}.json")
        if not os.path.exists(p):
            rows.append(f"| {name} | {what} | - | - | - | - | - | - | sin ejecutar |")
            continue
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        s = r.get("score", {})
        ans = r.get("answer_score")
        llm = r.get("llm_calls_retrieval", 0)
        llm_txt = f"{llm} pasos" if key.startswith("agentic_rag") else str(llm)
        ans_txt = "{:.0%}".format(ans["recall"]) if ans else "-"
        rows.append(f"| {name} | {what} | {s.get('recall', 0):.0%} | {s.get('precision', 0):.0%} | {f1(s):.2f} "
                    f"| {s.get('found', 0)} | ~{r.get('context_tokens', 0)} | {llm_txt} | {ans_txt} |")
    return "\n".join(rows)


def main() -> None:
    """Re-run every deterministic variant (unless ``--no-run``), print the tables and write compare.md."""
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-run", action="store_true", help="only read existing results")
    lib.add_question_arg(ap)
    a = ap.parse_args()
    qs = [lib.load_question(a.qid)] if a.qid else lib.list_questions()

    out = ["# Comparativa\n"]
    for q in qs:
        if not a.no_run:
            run(q["id"], ["naive_rag.py"])
            run(q["id"], ["graphrag.py", "--hops", "1"])
            run(q["id"], ["graphrag.py", "--hops", "2"])
            if not os.path.exists(lib.facts_path(q)):
                subprocess.run([sys.executable, os.path.join(lib.ROOT, "demo", "oag.py"), "build", "--q", q["id"]],
                               check=True, stdout=subprocess.DEVNULL)
            run(q["id"], ["oag.py", "query", "--schema", "1"])
            run(q["id"], ["oag.py", "query", "--schema", "2"])
            run(q["id"], ["hybrid.py"])
            hops = str(q.get("hops", 1))
            run(q["id"], ["naive_rag.py", "--lang", "es"])
            run(q["id"], ["graphrag.py", "--lang", "es", "--hops", hops])
            run(q["id"], ["oag.py", "query", "--lang", "es"])
            run(q["id"], ["oag.py", "query", "--lang", "es", "--schema", "3"])
            if has_embed():
                run(q["id"], ["naive_rag.py", "--embed"], check=False)
                run(q["id"], ["naive_rag.py", "--embed", "--lang", "es"], check=False)
                run(q["id"], ["graphrag.py", "--semantic", "--lang", "es", "--hops", hops], check=False)
                run(q["id"], ["oag.py", "query", "--semantic", "--lang", "es"], check=False)
        t = table(q, ORDER)
        t_es = table(q, order_es(q))
        block = (f"## {q['id']}\n\n{q.get('scenario', '')}\n\n{q['pregunta'].strip()}\n\n"
                 f"Respuesta esperada ({len(q['esperado'])}): {', '.join(q['esperado'])}\n\n{t}\n\n"
                 f"### En castellano llano, sin nombres de código\n\n{lib.spanish_question(q)}\n\n"
                 f"Tema para GraphRAG: {lib.spanish_topic(q)}\n\n{t_es}\n")
        print(block)
        out.append(block)
    print("Recall y precisión se miden contra la respuesta esperada. F1 resume las dos. Un ID extra no siempre"
          " es ruido: la lista esperada es un mínimo, no un techo.")
    os.makedirs(lib.RUNS, exist_ok=True)
    with open(os.path.join(lib.RUNS, "compare.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    main()
