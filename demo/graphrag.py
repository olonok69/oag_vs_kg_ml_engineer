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

Seed resolution is lexical (exact name, then substring), like /kg. With
--semantic the seed is the node whose label is closest in meaning to the topic
(multilingual embeddings, demo/semantic.py), so a topic in Spanish can still
land on an English node. --lang es uses the question's Spanish topic (`tema`).

    python demo/graphrag.py [--q <id>] [--topic get_letter_end] [--hops 1] [--lang es] [--semantic]
                            [--full] [--native]
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
    """The graph minus the hold-out, with the same rule as lib.holdout_view.

    A node goes if its source file is excluded (the reserved files and the notes about the reserved
    ticket), if its id or label names the reserved ticket or one of those notes, or if every
    neighbour it had was removed (a fact that only made sense next to the reserved ticket).

    Args:
        q: the question, for its hold-out.
        full: keep nodes from any source file; by default only nodes whose source file is in the
            demo corpus, so GraphRAG sees the same documents as the other techniques.

    Returns:
        ``(nodes, links)``: nodes by id, and the graph.json links whose two ends survived.
    """
    with open(lib.GRAPH, encoding="utf-8") as f:
        g = json.load(f)
    excluded = lib.excluded_files(q)
    pat = lib.holdout_pattern(q)
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    # graphify names a note's node after its file (knowledge__<author>_<slug>), so the file stem finds it.
    stems = [norm(n.split("__", 1)[-1][:-3]) for n in excluded]
    corpus = {d.name for d in lib.load_corpus(q)}

    def held(n: dict) -> bool:
        """True if the node comes from, or names, something in the hold-out."""
        src = n.get("source_file") or ""
        hay = f"{n.get('id', '')} {n.get('label', '')}"
        return src in excluded or bool(pat and pat.search(hay.replace("_", "-"))) \
            or any(st and st in norm(hay) for st in stems)

    gone = {n["id"] for n in g["nodes"] if held(n)}
    # Second pass: nodes whose every neighbour is gone, e.g. a symbol only the reserved fix introduced.
    nbrs: dict[str, set] = {}
    for e in g["links"]:
        nbrs.setdefault(e["source"], set()).add(e["target"])
        nbrs.setdefault(e["target"], set()).add(e["source"])
    gone |= {nid for nid, ns in nbrs.items() if nid not in gone and ns and ns <= gone}

    nodes = {n["id"]: n for n in g["nodes"]
             if n["id"] not in gone and (full or (n.get("source_file") or "") in corpus)}
    links = [e for e in g["links"] if e["source"] in nodes and e["target"] in nodes]
    return nodes, links


def community_names() -> dict[str, str]:
    """Map node id -> hand-written community name, from /kg-refresh's ``community_labels.json``.

    Returns an empty dict when the file is missing. The names give the "themes" of a neighbourhood,
    which is what makes GraphRAG useful for exploration questions.
    """
    path = os.path.join(os.path.dirname(lib.GRAPH), "community_labels.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        labels = json.load(f)
    return {m: c["name"] for c in labels.get("communities", []) for m in c.get("members", [])}


def resolve(nodes: dict, links: list[dict], topic: str) -> str | None:
    """Pick the seed node for a topic, as /kg does: by name, not by meaning.

    Exact id or label match first, then substring match ignoring punctuation and case. Ties go to the
    node with most edges. Returns ``None`` when no node is named like the topic, which is why a topic
    in Spanish finds nothing in an English graph.
    """
    t = topic.lower().strip()
    deg = Counter([e["source"] for e in links] + [e["target"] for e in links])
    exact = [i for i, n in nodes.items() if t in (i.lower(), n.get("label", "").lower())]
    norm = re.sub(r"[^a-z0-9]", "", t)
    sub = [i for i, n in nodes.items()
           if norm and norm in re.sub(r"[^a-z0-9]", "", f"{i} {n.get('label', '')}".lower())]
    pool = exact or sub
    return max(pool, key=lambda i: deg[i]) if pool else None


def resolve_semantic(nodes: dict, topic: str, model: str | None = None, show: int = 5
                     ) -> tuple[str | None, list[tuple[float, str]]]:
    """Pick the seed by meaning (``--semantic``): the node whose label is closest to the topic.

    Returns:
        ``(seed, top)``: the seed id and the ``show`` best ``(similarity, id)`` pairs, printed so the
        audience can see why that node was chosen.
    """
    import semantic  # optional dependency group `embed`
    ids = sorted(nodes)
    ranked = semantic.rank(topic, [nodes[i].get("label") or i for i in ids], model)
    top = [(sim, ids[i]) for sim, i in ranked[:show]]
    return (top[0][1] if top else None), top


def main() -> None:
    """Resolve the seed, walk its neighbourhood, print the reading list, score and save the run."""
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topic", help="override the topic from data/questions.yaml")
    ap.add_argument("--hops", type=int, help="neighbourhood depth (default: the question's `hops`, else 1)")
    ap.add_argument("--full", action="store_true", help="whole graph instead of the demo corpus")
    ap.add_argument("--native", action="store_true", help="run data/kg/kg_query.sh (needs graphify)")
    ap.add_argument("--semantic", action="store_true", help="resolve the seed by meaning, not by name")
    ap.add_argument("--model", help="embedding model (default: demo/semantic.py DEFAULT_MODEL)")
    ap.add_argument("--quiet", action="store_true")
    lib.add_question_arg(ap)
    lib.add_lang_arg(ap)
    a = ap.parse_args()

    q = lib.load_question(a.qid)
    topic = a.topic or (lib.spanish_topic(q) if a.lang == "es" else q.get("graph_topic") or q["topic"])
    a.hops = a.hops or q.get("hops", 1)

    if a.native:
        sh = os.path.join(lib.DATA, "kg", "kg_query.sh")
        subprocess.run(["bash", sh, topic], check=False)
        return

    nodes, links = load_graph(q, a.full)
    candidates = []
    if a.semantic:
        seed, candidates = resolve_semantic(nodes, topic, a.model)
    else:
        seed = resolve(nodes, links, topic)
    key = lib.run_key("graphrag" if a.hops == 1 else f"graphrag_{a.hops}h", a.lang, a.semantic)
    name = f"GraphRAG (/kg, {a.hops} hop)" + (", semilla semántica" if a.semantic else "") \
        + (" en castellano" if a.lang == "es" else "")
    if not seed:
        if not a.quiet:
            print(f"GRAPHRAG (/kg) | semilla: ninguna. Ningún nodo se llama {topic!r} ni lo contiene.")
            print("La búsqueda es por nombre: sin semilla no hay vecindario ni lista de lectura.")
        s = lib.print_score(q, [])
        lib.save_run(q, key, {"technique": name, "hops": a.hops, "lang": a.lang, "topic": topic, "seed": None,
                              "found": [], "score": s, "context_tokens": 0, "llm_calls_retrieval": 0,
                              "sources": [], "themes": []})
        return

    # Undirected adjacency: /kg explain shows edges in both directions.
    adj: dict[str, list[tuple[str, dict]]] = {}
    for e in links:
        adj.setdefault(e["source"], []).append((e["target"], e))
        adj.setdefault(e["target"], []).append((e["source"], e))

    # Breadth-first walk up to --hops. Each row is (hop, relation, confidence, neighbour node).
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

    # The context /kg would give the model: one line per neighbour with its relation and source file.
    lines = [f"{nodes[seed]['label']}  <- {nodes[seed].get('source_file')}"]
    for hop, rel, conf, n in rows:
        lines.append(f"  {'  ' * (hop - 1)}--{rel} [{conf}]--> {n.get('label', '')[:90]}  <- {n.get('source_file')}")
    context = "\n".join(lines)
    reading = sorted({n.get("source_file") for *_, n in rows if n.get("source_file")})
    found = lib.ticket_ids(context, q)               # returned = ticket ids in the neighbourhood
    names = community_names()
    themes = Counter(names[n["id"]] for *_, n in rows if n["id"] in names).most_common(8)

    if not a.quiet:
        rels = Counter(r for _, r, _, _ in rows)
        generic = sum(c for r, c in rels.items() if r in ("references", "conceptually_related_to",
                                                          "semantically_similar_to", "relates_to"))
        print(f"GRAPHRAG (/kg) | {'grafo completo' if a.full else 'grafo restringido al corpus de la demo'}"
              f" | {len(nodes)} nodos, {len(links)} aristas | tema: {topic!r} | semilla: {seed} | saltos: {a.hops}\n")
        if candidates:
            print("Semilla por similitud (coseno con la etiqueta del nodo):")
            for sim, nid in candidates:
                print(f"  {sim:.3f}  {nid}  ({nodes[nid].get('label', '')[:70]})")
            print()
        print(context)
        print(f"\nLista de lectura ({len(reading)} ficheros): {', '.join(reading)}")
        print(f"Relaciones: {dict(rels.most_common())}")
        print(f"Aristas genéricas: {generic}/{len(rows)} ({generic / max(1, len(rows)):.0%})."
              " El grafo dice qué leer, no qué hecho aporta cada fichero.")
        if themes:
            print("Temas (comunidades del grafo con nombre): "
                  + "; ".join(f"{name} ({c})" for name, c in themes))
        print(f"Contexto para el LLM: ~{lib.approx_tokens(context)} tokens, 0 llamadas LLM al consultar.")
        print(f"Tickets en el resultado: {', '.join(found) or '-'}")
    s = lib.print_score(q, found)
    lib.save_run(q, key, {"technique": name, "hops": a.hops, "lang": a.lang, "topic": topic, "seed": seed,
                          "found": found, "score": s,
                              "context_tokens": lib.approx_tokens(context), "llm_calls_retrieval": 0,
                              "sources": reading, "themes": themes})


if __name__ == "__main__":
    main()
