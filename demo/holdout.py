#!/usr/bin/env python3
"""Write the hold-out view of the corpus to disk and report what it removed.

Every scripted technique reads the corpus through lib.holdout_view(q), which drops the reserved
files, the notes written about the reserved ticket, and every passage that mentions it. Agentic RAG
reads files with Grep and Read instead, so it needs the same view on disk: data/holdout/<id>/.

    python demo/holdout.py [--q <id>]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil

import lib


def main() -> None:
    """Write ``data/holdout/<id>/`` (replacing it) plus ``_holdout_report.json`` and print a summary."""
    lib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    lib.add_question_arg(ap)
    a = ap.parse_args()
    q = lib.load_question(a.qid)
    docs, rep = lib.holdout_view(q)

    out = os.path.join(lib.DATA, "holdout", q["id"])
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for d in docs:
        with open(os.path.join(out, d.name), "w", encoding="utf-8") as f:
            f.write(d.text)
    with open(os.path.join(out, "_holdout_report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)

    print(f"Hold-out view for {q['id']}: {len(docs)} files in {os.path.relpath(out, lib.ROOT)}")
    print(f"  reserved files out:      {len(rep['holdout_files'])}")
    print(f"  notes about it out:      {len(rep['derived_files'])}")
    print(f"  passages removed:        {sum(rep['redacted'].values())} in {len(rep['redacted'])} files")


if __name__ == "__main__":
    main()
