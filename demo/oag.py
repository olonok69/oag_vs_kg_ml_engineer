#!/usr/bin/env python3
"""OAG: ontology-first facts over the ticket memory.

    python demo/oag.py build [--q <id>]                # corpus -> typed facts, validated against the ontology
    python demo/oag.py query [--q <id>] [--schema 1]   # facts that answer the question, with their sources

build: deterministic backbone (no LLM). Each document is mapped to the classes
and relations the ontology declares. Candidates outside the schema are
rejected and counted, not silently kept.

query: the question is mapped to ontology components through their altLabels.
The relevant nodes are the invariants that guard those components and the
tickets they come from. A greedy set cover (as in OG-RAG) picks the smallest
set of fact blocks that covers them. Output: facts, not chunks, each with its
source file.

Schema versions: v1 is the first ontology; v2 adds the `calls` relation between
components and the must_not_break_same_component constraint; v3 adds Spanish
labels for the components (alt_labels_es). `--schema N` ignores what later
versions added, so the demo can show what each change buys.

Language: the question is mapped to components by matching words, so a
question in Spanish without code names finds none unless the ontology has
Spanish labels (v3). With --semantic the components are chosen by meaning
instead (multilingual embeddings, demo/semantic.py), without touching the
ontology. --lang es asks the question in plain Spanish (pregunta_llana).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict

import lib

TEST_RE = re.compile(r"tests/test_[a-z0-9_]+\.py")
TEST_TICKET_RE = re.compile(r"tests/test_(sst|tkt)_(\d{3,5})_")


def load_ontology() -> dict:
    import yaml
    with open(lib.ONTOLOGY, encoding="utf-8") as f:
        return yaml.safe_load(f)


def alt_regex(labels: list[str]) -> re.Pattern:
    return re.compile("|".join(re.escape(x) for x in sorted(labels, key=len, reverse=True)), re.IGNORECASE)


def components_in(text: str, onto: dict, min_hits: int = 1, schema: int = 2) -> list[str]:
    """Components named in the text through their altLabels (and Spanish ones from schema v3)."""
    es = schema >= onto.get("labels", {}).get("alt_labels_es", {}).get("since", 99)
    out = []
    for cid, c in onto["components"].items():
        labels = c["alt_labels"] + ((c.get("alt_labels_es") or []) if es else [])
        if len(alt_regex(labels).findall(text)) >= min_hits:
            out.append(cid)
    return out


def components_semantic(text: str, onto: dict, min_sim: float, model: str | None = None
                        ) -> tuple[list[str], dict[str, tuple[float, str]]]:
    """Components whose description is close in meaning to some clause of the question.

    Each component is described by its label and English altLabels (no Spanish labels needed).
    The question is split into clauses, because a long question dilutes any single concept.
    Returns the components above min_sim and, for every component, its best (similarity, clause).
    """
    import semantic  # optional dependency group `embed`
    clauses = [c.strip() for c in re.split(r"[.;:?!¿¡\n]|,\s", text) if len(c.strip()) > 3] or [text]
    best = {}
    for cid, c in onto["components"].items():
        desc = f"{c['label']}: {', '.join(c['alt_labels'])}"
        sims = semantic.similarities(desc, clauses, model)
        i = max(range(len(sims)), key=sims.__getitem__)
        best[cid] = (sims[i], clauses[i])
    return [cid for cid, (sim, _) in best.items() if sim >= min_sim], best


# ----------------------------------------------------------------------------- build
def parse_invariants(doc: lib.Doc, q: dict) -> list[dict]:
    """Rows of the invariant index table and '- **SST-NNNN ...**' bullets of SHARP_EDGES."""
    invs = []
    for line in doc.text.splitlines():
        s = line.strip()
        if s.startswith("|") and not s.startswith("|---") and "Ticket of origin" not in s:
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 3 and lib.ticket_ids(cells[1], q):
                invs.append({"text": f"{cells[0]}. {cells[2]}", "origin": lib.ticket_ids(cells[1], q)})
        elif s.startswith("- **") and lib.ticket_ids(s[:40], q):
            head = s[4:].split("**", 1)[0]
            invs.append({"text": s[2:400], "origin": lib.ticket_ids(head, q)})
    return invs


def build(q: dict, onto: dict) -> dict:
    docs = lib.load_corpus(q)
    rules = onto["extraction"]
    cue_re = re.compile("|".join(re.escape(c) for c in rules["must_not_break_cues"]), re.IGNORECASE)

    nodes: dict[str, dict] = {}
    cand: list[dict] = []   # candidate edges before validation

    def node(nid: str, cls: str, **attrs) -> None:
        if nid not in nodes:
            nodes[nid] = {"id": nid, "class": cls, **attrs}
        else:
            for k, v in attrs.items():
                nodes[nid].setdefault(k, v)

    for cid, c in onto["components"].items():
        node(cid, "Component", label=c["label"])
    for cid, c in onto["components"].items():
        for target, via in (c.get("calls") or {}).items():
            cand.append({"rel": "calls", "from": cid, "to": target, "via": via, "source": "demo/oag/ontology.yaml"})

    inv_n = 0
    for d in docs:
        m = re.match(r"((?:sst|tkt)-\d{3,5})__", d.name, re.IGNORECASE)
        if m:  # a ticket writeup
            tid = m.group(1).upper()
            title = d.text.strip().splitlines()[0].lstrip("# ").strip()[:160]
            node(tid, "Ticket", title=title, source=d.name)
            for comp in components_in(d.text, onto, rules["touches_min_mentions"]):
                cand.append({"rel": "touches", "from": tid, "to": comp, "source": d.name})
            for line in d.text.splitlines():
                others = [t for t in lib.ticket_ids(line, q) if t != tid]
                rel = "must_not_break" if cue_re.search(line) else "mentions"  # 'mentions' is not in the schema
                for o in others:
                    node(o, "Ticket", source=d.name)
                    cand.append({"rel": rel, "from": tid, "to": o, "source": d.name})
        if d.name.startswith("hub__SHARP_EDGES"):
            for inv in parse_invariants(d, q):
                inv_n += 1
                iid = f"INV-{inv_n:03d}"
                node(iid, "Invariant", text=inv["text"], source=d.name)
                for o in inv["origin"]:
                    node(o, "Ticket", source=d.name)
                    cand.append({"rel": "originates", "from": o, "to": iid, "source": d.name})
                for comp in components_in(inv["text"], onto):
                    cand.append({"rel": "guards", "from": iid, "to": comp, "source": d.name})
        for test in set(TEST_RE.findall(d.text)):
            tm = TEST_TICKET_RE.match(test)
            if tm:
                tid = f"{tm.group(1).upper()}-{tm.group(2)}"
                if tid in set(q["holdout"]):
                    continue
                node(tid, "Ticket", source=d.name)
                node(test, "Test", source=d.name)
                cand.append({"rel": "verified_by", "from": tid, "to": test, "source": d.name})

    # --------------------------------------------------------------- validation (SHACL-like)
    rels = onto["relations"]
    classes = onto["classes"]
    accepted, rejected = [], Counter()
    seen = set()
    for e in cand:
        key = (e["rel"], e["from"], e["to"])
        if key in seen:
            continue
        seen.add(key)
        spec = rels.get(e["rel"])
        if spec is None:
            rejected[f"relation not in ontology: {e['rel']}"] += 1
            continue
        f, t = nodes.get(e["from"]), nodes.get(e["to"])
        if not f or not t or f["class"] != spec["from"] or t["class"] != spec["to"]:
            rejected[f"wrong domain/range for {e['rel']}"] += 1
            continue
        if not e.get("source"):
            rejected["edge without source"] += 1
            continue
        accepted.append(e)
    bad_nodes = Counter()
    for n in nodes.values():
        pat = classes[n["class"]].get("id_pattern")
        if pat and not re.match(pat, n["id"]):
            bad_nodes[f"{n['class']} id does not match pattern"] += 1
        for r in classes[n["class"]].get("required", []):
            if r not in n:
                bad_nodes[f"{n['class']} missing {r}"] += 1

    return {"nodes": list(nodes.values()), "edges": accepted,
            "report": {"documents": len(docs), "candidates": len(seen), "accepted": len(accepted),
                       "rejected": dict(rejected), "node_issues": dict(bad_nodes),
                       "by_class": dict(Counter(n["class"] for n in nodes.values())),
                       "by_relation": dict(Counter(e["rel"] for e in accepted))}}


# ----------------------------------------------------------------------------- query
def query(q: dict, onto: dict, facts: dict, text: str, schema: int = 2, comps: list[str] | None = None
          ) -> tuple[list[dict], list[str], list[dict]]:
    nodes = {n["id"]: n for n in facts["nodes"]}
    out_e, in_e = defaultdict(list), defaultdict(list)
    for e in facts["edges"]:
        if schema < onto["relations"].get(e["rel"], {}).get("since", 1):
            continue
        out_e[e["from"]].append(e)
        in_e[e["to"]].append(e)

    if comps is None:
        comps = components_in(text, onto, schema=schema)
    # relevant = invariants that guard the component + tickets the writeups say not to break
    invariants = {e["from"] for c in comps for e in in_e[c] if e["rel"] == "guards"}
    # v2: follow `calls` to the called component, keeping only invariants that pin the called symbols
    via_note = {}
    for c in comps:
        for call in (e for e in out_e[c] if e["rel"] == "calls"):
            sym = alt_regex(call["via"])
            for g in in_e[call["to"]]:
                if g["rel"] == "guards" and g["from"] not in invariants and sym.search(nodes[g["from"]]["text"]):
                    invariants.add(g["from"])
                    via_note[g["from"]] = f"{c} calls {', '.join(call['via'])} ({call['to']})"
    touching = [e["from"] for c in comps for e in in_e[c] if e["rel"] == "touches"]
    protected = {e["to"] for t in touching for e in out_e[t] if e["rel"] == "must_not_break"}
    if schema >= onto.get("constraints", {}).get("must_not_break_same_component", {}).get("since", 99):
        def on_component(t: str) -> bool:
            own = {e["to"] for e in out_e[t] if e["rel"] == "touches"}
            own |= {g["to"] for e in out_e[t] if e["rel"] == "originates" for g in out_e[e["to"]] if g["rel"] == "guards"}
            return bool(own & set(comps))
        protected = {t for t in protected if on_component(t)}
    relevant = invariants | protected

    # fact blocks: one per ticket = the ticket + what it originates + what it protects
    blocks = {}
    for tid, n in nodes.items():
        if n["class"] != "Ticket":
            continue
        cover = {tid} | {e["to"] for e in out_e[tid] if e["rel"] == "originates"}
        blocks[tid] = cover & relevant

    chosen, uncovered = [], set(relevant)
    while uncovered:
        best = max(blocks, key=lambda b: (len(blocks[b] & uncovered), b), default=None)
        if not best or not blocks[best] & uncovered:
            break
        chosen.append(best)
        uncovered -= blocks[best]

    fact_blocks = []
    for tid in chosen:
        n = nodes[tid]
        fb = {"@type": "Ticket", "id": tid}
        if n.get("title"):
            fb["title"] = n["title"]
        fb["originates"] = [{k: v for k, v in {
                                "invariant": nodes[e["to"]]["text"][:220],
                                "origin": sorted(x["from"] for x in in_e[e["to"]] if x["rel"] == "originates"),
                                "guards": sorted(g["to"] for g in out_e[e["to"]] if g["rel"] == "guards"),
                                "reached_via": via_note.get(e["to"])}.items() if v}
                            for e in out_e[tid] if e["rel"] == "originates" and e["to"] in relevant]
        why = sorted({e["from"] for t in touching for e in out_e[t]
                      if e["rel"] == "must_not_break" and e["to"] == tid})
        if why:
            fb["named_as_must_not_break_by"] = why
        fb["verified_by"] = [e["to"] for e in out_e[tid] if e["rel"] == "verified_by"]
        fb["source"] = n.get("source")
        fact_blocks.append({k: v for k, v in fb.items() if v})
    return fact_blocks, comps, [nodes[i] for i in sorted(uncovered)]


def main() -> None:
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build", "query"])
    ap.add_argument("--query", help="override the query (default: topic + query from data/questions.yaml)")
    ap.add_argument("--schema", type=int, default=2, choices=[1, 2, 3],
                    help="ontology version for the query (1 = without v2, 3 = with Spanish labels)")
    ap.add_argument("--semantic", action="store_true", help="map the question to components by meaning")
    ap.add_argument("--min-sim", type=float, default=0.42,
                    help="similarity threshold for --semantic (calibrated on the two demo questions)")
    ap.add_argument("--model", help="embedding model (default: demo/semantic.py DEFAULT_MODEL)")
    ap.add_argument("--quiet", action="store_true")
    lib.add_question_arg(ap)
    lib.add_lang_arg(ap)
    a = ap.parse_args()

    q = lib.load_question(a.qid)
    onto = load_ontology()
    path = lib.facts_path(q)

    if a.cmd == "build":
        facts = build(q, onto)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(facts, f, ensure_ascii=False, indent=1)
        r = facts["report"]
        print(f"OAG build | ontología: {os.path.relpath(lib.ONTOLOGY, lib.ROOT)} | {r['documents']} documentos")
        print(f"Nodos por clase: {r['by_class']}")
        print(f"Aristas candidatas: {r['candidates']} -> aceptadas {r['accepted']}")
        print(f"Aceptadas por relación: {r['by_relation']}")
        print("Rechazadas por la validación:")
        for k, v in sorted(r["rejected"].items(), key=lambda x: -x[1]):
            print(f"  {v:5}  {k}")
        if r["node_issues"]:
            print(f"Avisos de nodos: {r['node_issues']}")
        print(f"\nHechos escritos en {os.path.relpath(path, lib.ROOT)} (0 llamadas LLM).")
        return

    if not os.path.exists(path):
        raise SystemExit(f"No facts yet. Run: python demo/oag.py build --q {q['id']}")
    with open(path, encoding="utf-8") as f:
        facts = json.load(f)
    text = a.query or (lib.spanish_question(q) if a.lang == "es" else f"{q['topic']} {q['query']}")
    comps, sims = None, {}
    if a.semantic:
        comps, sims = components_semantic(text, onto, a.min_sim, a.model)
    blocks, comps, left = query(q, onto, facts, text, a.schema, comps)
    context = json.dumps(blocks, ensure_ascii=False, indent=1)
    # The answer is the subject of each fact block plus the declared origins of its invariants.
    # Ids under named_as_must_not_break_by are provenance (who said so), not part of the answer.
    answer = " ".join([b["id"] for b in blocks] + [o for b in blocks for i in b.get("originates", []) for o in i["origin"]])
    found = lib.ticket_ids(answer, q)
    if not a.quiet:
        mode = f"semántico, umbral {a.min_sim}" if a.semantic else "por etiquetas"
        print(f"OAG query | esquema v{a.schema} | {'pregunta en castellano | ' if a.lang == 'es' else ''}"
              f"componentes ({mode}): {', '.join(comps) or '-'}")
        for cid, (sim, clause) in sorted(sims.items(), key=lambda x: -x[1][0]):
            print(f"  {sim:.3f}  {cid:22} <- \"{clause[:80]}\"")
        if not comps:
            print("La pregunta no se asocia a ningún componente de la ontología: OAG no tiene hechos que dar.")
        print(f"Set cover: {len(blocks)} fact blocks cubren los nodos relevantes"
              f"{'' if not left else f' (sin cubrir: {len(left)})'}\n")
        print(context)
        print(f"\nContexto para el LLM: ~{lib.approx_tokens(context)} tokens, hechos tipados con fuente,"
              " 0 llamadas LLM al consultar.")
        print(f"Tickets que afirman los hechos: {', '.join(found) or '-'}")
    s = lib.print_score(q, found)
    key = lib.run_key("oag" if a.schema == 2 else f"oag_v{a.schema}", a.lang, a.semantic)
    name = f"OAG (esquema v{a.schema})" + (", componentes por similitud" if a.semantic else "") \
        + (" en castellano" if a.lang == "es" else "")
    lib.save_run(q, key, {"technique": name, "schema": a.schema, "lang": a.lang, "components": comps,
                         "similarities": {k: round(v[0], 3) for k, v in sims.items()}, "found": found, "score": s,
                         "context_tokens": lib.approx_tokens(context), "llm_calls_retrieval": 0,
                         "sources": sorted({b.get('source') for b in blocks if b.get('source')})})


if __name__ == "__main__":
    main()
