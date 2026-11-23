"""Semantic layer for the demo: multilingual sentence embeddings.

The three deterministic techniques match words. A question in Spanish over an
English corpus shares almost no words with it, so they fail before they start.
This module maps text in any language to vectors where "fin de carta" and
"letter end" are close, and each technique uses it at the step where it
compares the question with the corpus:

- Naive RAG ranks chunks by cosine similarity (naive_rag.py --embed).
- GraphRAG picks the seed node by similarity to node labels (graphrag.py --semantic).
- OAG picks ontology components by similarity to their labels (oag.py query --semantic).

Model: paraphrase-multilingual-MiniLM-L12-v2 (50+ languages, 384 dimensions,
~470 MB on disk, runs on CPU). Override with DEMO_EMBED_MODEL or --model. Needs the
`embed` dependency group (uv sync --group embed) and, the first time, access
to huggingface.co to download the model. Embeddings of the corpus are cached in
data/cache/embeddings/ so later runs are fast.
"""
from __future__ import annotations

import hashlib
import os
import sys

import lib

DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CACHE = os.path.join(lib.DATA, "cache", "embeddings")

_models: dict = {}  # loaded SentenceTransformer models, by name (loading takes seconds)


def model_name(override: str | None = None) -> str:
    """Model to use: ``--model``, else $DEMO_EMBED_MODEL, else ``DEFAULT_MODEL``."""
    return override or os.environ.get("DEMO_EMBED_MODEL") or DEFAULT_MODEL


def _model(name: str):
    """Load the model once per process, on CPU. Exits with the install hint if the group is missing."""
    if name not in _models:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            sys.exit("The semantic layer needs sentence-transformers: uv sync --group embed")
        _models[name] = SentenceTransformer(name, device="cpu")
    return _models[name]


def encode(texts: list[str], name: str | None = None, cache: bool = True):
    """Unit-normalised embeddings, one row per text.

    The cache key is a hash of all the texts plus the model name, so the corpus is embedded once and
    any change to the corpus or the model recomputes it. Queries are encoded with ``cache=False``.

    Returns:
        A numpy array of shape (len(texts), dimensions). Rows have length 1, so a dot product is
        the cosine similarity.
    """
    import numpy as np
    name = model_name(name)
    key = hashlib.sha1(("\x00".join(texts) + "\x01" + name).encode("utf-8")).hexdigest()[:16]
    path = os.path.join(CACHE, name.replace("/", "_"), f"{key}.npy")
    if cache and os.path.exists(path):
        return np.load(path)
    # normalize_embeddings=True makes every row unit-length; similarities() relies on it.
    emb = _model(name).encode(texts, batch_size=64, normalize_embeddings=True,
                              convert_to_numpy=True, show_progress_bar=len(texts) > 500)
    if cache:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.save(path, emb)
    return emb


def similarities(query: str, texts: list[str], name: str | None = None) -> list[float]:
    """Cosine similarity of the query with each text, in the order of texts."""
    q = encode([query], name, cache=False)[0]
    return (encode(texts, name) @ q).tolist()


def rank(query: str, texts: list[str], name: str | None = None) -> list[tuple[float, int]]:
    """(similarity, index) pairs, best first."""
    return sorted(((s, i) for i, s in enumerate(similarities(query, texts, name))), key=lambda x: -x[0])
