#!/usr/bin/env python3
"""Hybrid: GraphRAG proposes, the ontology filters, and what the ontology does not cover goes to GraphRAG.

    python demo/hybrid.py [--q <id>] [--hops 2] [--lang es] [--semantic] [--schema 3]

Three steps, no LLM:

1. GraphRAG (/kg, 2 hops by default) gives the broad candidate list: high recall, low precision.
2. The question is mapped to ontology components, as in OAG. If it names at least one, the candidates
   go through two filters: first by classes and relations (the ticket touches the component, or
   originates an invariant that guards it), then by the ontology's rules (the OAG v2 query, with the
   same-component constraint and `calls`). What survives is the answer. If OAG finds a ticket the
   graph did not propose, it is added and reported.
3. If the question names no component, the ontology has nothing to say: the answer is GraphRAG's list,
   unfiltered. The communities the graph found are printed as candidates to extend the ontology,
   for a person to review (the ontology is never changed automatically).

The script runs graphrag.py and oag.py (same flags, --quiet) and reads their results from
data/runs/<id>/, so the numbers are exactly those of the two techniques.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict

import lib


def run(script: list[str]) -> None:
    subprocess.run([sys.executable, os.path.join(lib.ROOT, "demo", script[0]), *script[1:], "--quiet"],
                   check=True, stdout=subprocess.DEVNULL)


def read_run(q: dict, key: str) -> dict:
    with open(os.path.join(lib.run_dir(q), f"{key}.json"), encoding="utf-8") as f:
        return json.load(f)


def linked_to(facts: dict, comps: list[str]) -> dict[str, str]:
    """ticket -> how the ontology links it to the question's components (classes and relations only)."""
    guards = {e["from"] for e in facts["edges"] if e["rel"] == "guards" and e["to"] in comps}
    link = {}
    for e in facts["edges"]:
        if e["rel"] == "touches" and e["to"] in comps:
            link[e["from"]] = f"touches {e['to']}"
        elif e["rel"] == "originates" and e["to"] in guards:
            link.setdefault(e["from"], f"originates {e['to']}")
    return link


def main() -> None:
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hops", type=int, default=2, help="GraphRAG depth for the candidate list (default 2)")
    ap.add_argument("--schema", type=int, default=2, choices=[1, 2, 3], help="ontology version for the filter")
    ap.add_argument("--semantic", action="store_true",
                    help="GraphRAG seed and OAG components by meaning (demo/semantic.py)")
    ap.add_argument("--quiet", action="store_true")
    lib.add_question_arg(ap)
    lib.add_lang_arg(ap)
    a = ap.parse_args()
    q = lib.load_question(a.qid)

    common = ["--q", q["id"], "--lang", a.lang] + (["--semantic"] if a.semantic else [])
    if not os.path.exists(lib.facts_path(q)):
        subprocess.run([sys.executable, os.path.join(lib.ROOT, "demo", "oag.py"), "build", "--q", q["id"]],
                       check=True, stdout=subprocess.DEVNULL)
    run(["graphrag.py", "--hops", str(a.hops), *common])
    run(["oag.py", "query", "--schema", str(a.schema), *common])
    g = read_run(q, lib.run_key("graphrag" if a.hops == 1 else f"graphrag_{a.hops}h", a.lang, a.semantic))
    o = read_run(q, lib.run_key("oag" if a.schema == 2 else f"oag_v{a.schema}", a.lang, a.semantic))
    with open(lib.facts_path(q), encoding="utf-8") as f:
        facts = json.load(f)

    cand, comps = g["found"], o["components"]
    out = print if not a.quiet else (lambda *_, **__: None)
    out(f"HÍBRIDO | GraphRAG ({a.hops} saltos, semilla {g['seed'] or '-'}) propone, la ontología (v{a.schema}) filtra"
        f"{' | pregunta en castellano' if a.lang == 'es' else ''}\n")
    out(f"1. Candidatos de GraphRAG: {len(cand)} tickets.")

    if comps:
        link = linked_to(facts, comps)
        soft = [t for t in cand if t in link or t in o["found"]]
        strict = [t for t in cand if t in o["found"]]
        added = [t for t in o["found"] if t not in cand]
        found = strict + added
        route = "ontology"
        out(f"2. La pregunta se asocia a componentes de la ontología: {', '.join(comps)}. Se filtra.")
        out(f"   a) Por clases y relaciones (toca el componente o se conecta a él en la ontología):"
            f" {len(cand)} -> {len(soft)}.  {lib.score(soft, q['esperado'])['precision']:.0%} de precisión")
        out(f"   b) Por las reglas de la ontología (restricción de mismo componente, `calls`):"
            f" {len(soft)} -> {len(strict)}.  {lib.score(strict, q['esperado'])['precision']:.0%} de precisión")
        dropped = [t for t in cand if t not in o["found"]]
        out(f"   Descartados: {len(dropped)}. Ejemplos sin relación con el componente: "
            f"{', '.join([t for t in dropped if t not in link][:6]) or '-'}")
        out(f"   Añadidos por la ontología que el grafo no propuso: {', '.join(added) or 'ninguno'}")
        for t in found:
            out(f"     {t:10} {link.get(t, 'regla de la ontología')}")
        proposal = []
    else:
        found = cand
        route = "graphrag"
        out("2. La pregunta no se asocia a ningún componente de la ontología: no hay nada que filtrar.")
        out("   La respuesta es la lista de GraphRAG sin tocar.")
        proposal = [name for name, _ in (g.get("themes") or [])[:5]]
        out("3. Propuesta para ampliar la ontología (la revisa una persona; no se aplica sola):")
        out(f"   Componente candidato a partir de la semilla del grafo: {g['seed'] or '-'}")
        if proposal:
            out("   Comunidades del vecindario que podrían ser sinónimos o subcomponentes: " + "; ".join(proposal))
        out("   Si la misma área vuelve a salir en otras preguntas, merece entrar en la ontología con sus reglas.")

    out(f"\nRuta: {'ontología (OAG filtra a GraphRAG)' if route == 'ontology' else 'GraphRAG sin filtrar'}."
        " 0 llamadas LLM al recuperar.")
    out(f"Tickets en el resultado: {', '.join(found) or '-'}")
    s = lib.print_score(q, found) if not a.quiet else lib.score(found, q["esperado"])
    key = lib.run_key("hybrid", a.lang, a.semantic)
    lib.save_run(q, key, {"technique": "Híbrido (GraphRAG propone, OAG filtra)", "route": route, "hops": a.hops,
                          "schema": a.schema, "lang": a.lang, "components": comps, "candidates": len(cand),
                          "found": found, "score": s, "proposal": proposal,
                          "context_tokens": o["context_tokens"] if route == "ontology" else g["context_tokens"],
                          "llm_calls_retrieval": 0,
                          "sources": o["sources"] if route == "ontology" else g["sources"]})


if __name__ == "__main__":
    main()
