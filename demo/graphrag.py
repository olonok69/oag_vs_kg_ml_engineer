#!/usr/bin/env python3
"""GraphRAG: the existing /kg skill (graphify explain) over the ticket graph.

This is the same query /kg runs (`kg_query.sh <topic>`): resolve a topic to a
node, return its neighbours with relation and confidence, and the source files
they come from (the reading list). Implemented here in pure Python over
data/kg/output/graph.json so it runs without graphify and can apply the
hold-out; `--native` calls data/kg/kg_query.sh instead when graphify is
installed.

Scope: by default only nodes whose source file is in data/corpus are kept, so
the comparison with the other techniques uses the same documents. `--full`
uses the whole graph (what /kg sees in the lambda repo).

    python demo/graphrag.py [--topic get_letter_end] [--hops 1] [--full] [--native]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter

import lib


def load_graph(q: dict, full: bool) -> tuple[dict, list[dict]]:
    with open(lib.GRAPH, encoding="utf-8") as f:
        g = json.load(f)
    hold_files = set(q["holdout_files"])
    hold_ids = [h.lower() for h in q["holdout"]]
    corpus = {d.name for d in lib.load_corpus(q)}

    def keep(n: dict) -> bool:
        src = n.get("source_file") or ""
        hay = f"{n.get('id', '')} {n.get('label', '')} {src}".lower().replace("-", "")
        if src in hold_files or any(h.replace("-", "") in hay for h in hold_ids):
            return False
        return full or src in corpus

    nodes = {n["id"]: n for n in g["nodes"] if keep(n)}
    links = [e for e in g["links"] if e["source"] in nodes and e["target"] in nodes]
    return nodes, links


def resolve(nodes: dict, links: list[dict], topic: str) -> str | None:
    """Exact id/label first, then substring; ties go to the best-connected node."""
    t = topic.lower().strip()
    deg = Counter([e["source"] for e in links] + [e["target"] for e in links])
    exact = [i for i, n in nodes.items() if t in (i.lower(), n.get("label", "").lower())]
    norm = re.sub(r"[^a-z0-9]", "", t)
    sub = [i for i, n in nodes.items()
           if norm and norm in re.sub(r"[^a-z0-9]", "", f"{i} {n.get('label', '')}".lower())]
    pool = exact or sub
    return max(pool, key=lambda i: deg[i]) if pool else None


def main() -> None:
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topic", help="override the topic from data/questions.yaml")
    ap.add_argument("--hops", type=int, default=1)
    ap.add_argument("--full", action="store_true", help="whole graph instead of the demo corpus")
    ap.add_argument("--native", action="store_true", help="run data/kg/kg_query.sh (needs graphify)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    q = lib.load_question()
    topic = a.topic or q["topic"]

    if a.native:
        sh = os.path.join(lib.DATA, "kg", "kg_query.sh")
        subprocess.run(["bash", sh, topic], check=False)
        return

    nodes, links = load_graph(q, a.full)
    seed = resolve(nodes, links, topic)
    if not seed:
        raise SystemExit(f"No node matches {topic!r}. Try another --topic.")

    adj: dict[str, list[tuple[str, dict]]] = {}
    for e in links:
        adj.setdefault(e["source"], []).append((e["target"], e))
        adj.setdefault(e["target"], []).append((e["source"], e))

    frontier, seen, rows = [seed], {seed}, []
    for hop in range(1, a.hops + 1):
        nxt = []
        for u in frontier:
            for v, e in adj.get(u, []):
                if v in seen:
                    continue
                seen.add(v)
                nxt.append(v)
                rows.append((hop, e["relation"], e.get("confidence", ""), nodes[v]))
        frontier = nxt

    lines = [f"{nodes[seed]['label']}  <- {nodes[seed].get('source_file')}"]
    for hop, rel, conf, n in rows:
        lines.append(f"  {'  ' * (hop - 1)}--{rel} [{conf}]--> {n.get('label', '')[:90]}  <- {n.get('source_file')}")
    context = "\n".join(lines)
    reading = sorted({n.get("source_file") for *_, n in rows if n.get("source_file")})
    found = lib.ticket_ids(context, q)

    if not a.quiet:
        rels = Counter(r for _, r, _, _ in rows)
        generic = sum(c for r, c in rels.items() if r in ("references", "conceptually_related_to",
                                                          "semantically_similar_to", "relates_to"))
        print(f"GRAPHRAG (/kg) | {'grafo completo' if a.full else 'grafo restringido al corpus de la demo'}"
              f" | {len(nodes)} nodos, {len(links)} aristas | semilla: {seed} | saltos: {a.hops}\n")
        print(context)
        print(f"\nLista de lectura ({len(reading)} ficheros): {', '.join(reading)}")
        print(f"Relaciones: {dict(rels.most_common())}")
        print(f"Aristas genéricas: {generic}/{len(rows)} ({generic / max(1, len(rows)):.0%})."
              " El grafo dice qué leer, no qué hecho aporta cada fichero.")
        print(f"Contexto para el LLM: ~{lib.approx_tokens(context)} tokens, 0 llamadas LLM al consultar.")
        print(f"Tickets en el resultado: {', '.join(found) or '-'}")
    s = lib.print_score(q, found)
    lib.save_run("graphrag", {"technique": "GraphRAG (/kg)", "found": found, "score": s,
                              "context_tokens": lib.approx_tokens(context), "llm_calls_retrieval": 0,
                              "sources": reading})


if __name__ == "__main__":
    main()
