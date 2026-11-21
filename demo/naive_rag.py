#!/usr/bin/env python3
"""Naive RAG: chunk, vectorise, top-k by cosine similarity.

Vectoriser: TF-IDF (pure Python, deterministic, offline). It stands in for an
embedding model; with --embed and sentence-transformers installed it uses
all-MiniLM-L6-v2 instead. Either way the retrieval unit is a text chunk with
no notion of tickets, symbols or relations.

    python demo/naive_rag.py [--k 5] [--chunk-words 180] [--embed] [--query "..."]
"""
from __future__ import annotations

import argparse
import math
import re
from collections import Counter

import lib

WORD = re.compile(r"[a-z0-9_]+")
STOP = set("""a an the and or of to in on for is are was were be been it its this that with as by at from
not no but if then than so do does did into out up can could should would will may might has have had
which who whom what when where why how all any each other such only own same too very just also""".split())


def tokens(text: str) -> list[str]:
    return [w for w in WORD.findall(text.lower()) if w not in STOP and len(w) > 1]


def chunk(doc: lib.Doc, words: int, overlap: int) -> list[dict]:
    ws = doc.text.split()
    out, step = [], max(1, words - overlap)
    for i in range(0, max(1, len(ws)), step):
        piece = " ".join(ws[i:i + words])
        if piece.strip():
            out.append({"source": doc.name, "pos": i, "text": piece})
        if i + words >= len(ws):
            break
    return out


def tfidf_rank(chunks: list[dict], query: str) -> list[tuple[float, dict]]:
    docs_tok = [Counter(tokens(c["text"])) for c in chunks]
    n = len(chunks)
    df = Counter(t for d in docs_tok for t in d)
    idf = {t: math.log((1 + n) / (1 + df[t])) + 1 for t in df}

    def vec(tf: Counter) -> dict:
        v = {t: (1 + math.log(c)) * idf.get(t, 0.0) for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    qv = vec(Counter(tokens(query)))
    scored = []
    for d, c in zip(docs_tok, chunks):
        dv = vec(d)
        scored.append((sum(w * dv.get(t, 0.0) for t, w in qv.items()), c))
    return sorted(scored, key=lambda x: -x[0])


def embed_rank(chunks: list[dict], query: str) -> list[tuple[float, dict]]:
    from sentence_transformers import SentenceTransformer, util  # optional dependency
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode([c["text"] for c in chunks], convert_to_tensor=True, normalize_embeddings=True)
    qe = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(qe, emb)[0].tolist()
    return sorted(zip(sims, chunks), key=lambda x: -x[0])


def main() -> None:
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--chunk-words", type=int, default=180)
    ap.add_argument("--overlap", type=int, default=30)
    ap.add_argument("--embed", action="store_true", help="use sentence-transformers instead of TF-IDF")
    ap.add_argument("--query", help="override the query from data/questions.yaml")
    ap.add_argument("--quiet", action="store_true", help="only print the score")
    a = ap.parse_args()

    q = lib.load_question()
    query = a.query or q["query"]
    docs = lib.load_corpus(q)
    chunks = [c for d in docs for c in chunk(d, a.chunk_words, a.overlap)]
    ranked = (embed_rank if a.embed else tfidf_rank)(chunks, query)[: a.k]

    context = "\n\n".join(f"[{i}] {c['source']} (word {c['pos']})\n{c['text']}" for i, (_, c) in enumerate(ranked, 1))
    found = lib.ticket_ids(context, q)

    if not a.quiet:
        print(f"NAIVE RAG | {len(docs)} documentos -> {len(chunks)} chunks de ~{a.chunk_words} palabras"
              f" | vectorizador: {'embeddings' if a.embed else 'TF-IDF'} | top-{a.k}")
        print(f"Query: {query.strip()}\n")
        for i, (s, c) in enumerate(ranked, 1):
            print(f"--- [{i}] score {s:.3f}  {c['source']} (palabra {c['pos']})")
            print(c["text"])
            print()
        print(f"Contexto para el LLM: ~{lib.approx_tokens(context)} tokens, {a.k} trozos, 0 relaciones.")
        print(f"Tickets que aparecen en el contexto: {', '.join(found) or '-'}")
    s = lib.print_score(q, found)
    lib.save_run("naive_rag", {"technique": "Naive RAG", "found": found, "score": s,
                               "context_tokens": lib.approx_tokens(context), "llm_calls_retrieval": 0,
                               "sources": sorted({c["source"] for _, c in ranked})})


if __name__ == "__main__":
    main()
