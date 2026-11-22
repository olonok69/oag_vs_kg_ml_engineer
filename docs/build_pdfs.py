#!/usr/bin/env python3
"""Render the guides in docs/ to PDF (docs/pdf/).

    python docs/build_pdfs.py [GUIA_DEMO.md ...]

Markdown -> HTML with pandoc, then HTML -> PDF with headless Chrome/Chromium.
Relative links to the repo become GitHub links, so the code references in the
technical guides still work from the PDF. Mermaid blocks are rendered in the
browser with mermaid.js (MERMAID_JS=<path or URL>, default: jsDelivr CDN).

Requirements: pandoc, and Chrome or Chromium (CHROME=<path> if it is not on PATH).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

DOCS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DOCS, "pdf")
REPO_URL = "https://github.com/olonok69/oag_vs_kg_ml_engineer/blob/main/"
GUIDES = ["GUIA_DEMO.md", "DEMO_GUIDE.md", "EJECUTAR_DEMO.md", "RUN_DEMO.md",
          "GUIA_TECNICA.md", "TECHNICAL_GUIDE.md", "OAG_VS_KG.md",
          "GUION_PRESENTACION.md", "PRESENTATION_SCRIPT.md"]
MERMAID_JS = os.environ.get("MERMAID_JS", "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js")

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font-family: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif; font-size: 10.5pt;
       line-height: 1.5; color: #1b1f24; max-width: none; margin: 0; }
h1 { font-size: 21pt; margin: 0 0 6pt; color: #11161c; border-bottom: 3px solid #E07A5F; padding-bottom: 6pt; }
h2 { font-size: 15pt; margin: 20pt 0 6pt; color: #11161c; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 14pt 0 4pt; color: #C4553A; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: #2F6FA8; text-decoration: none; }
code { font-family: "JetBrains Mono", "Consolas", monospace; font-size: 9pt; background: #F2F4F7;
       padding: 0 3px; border-radius: 3px; }
pre { background: #0F141A; color: #E6EDF3; padding: 9pt 11pt; border-radius: 6px; font-size: 8.8pt;
      line-height: 1.4; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; }
pre.mermaid { background: none; color: inherit; text-align: center; }
blockquote { margin: 8pt 0; padding: 4pt 12pt; border-left: 3px solid #E07A5F; color: #4a5560;
             background: #FBF4F1; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; page-break-inside: auto; }
th { background: #1F2630; color: #fff; text-align: left; padding: 4pt 6pt; }
td { border-bottom: 1px solid #D9DEE4; padding: 4pt 6pt; vertical-align: top; }
tr { page-break-inside: avoid; }
img { max-width: 100%; display: block; margin: 8pt auto; page-break-inside: avoid; }
hr { border: none; border-top: 1px solid #D9DEE4; margin: 14pt 0; }
"""


def chrome() -> str:
    for c in [os.environ.get("CHROME"), "google-chrome", "chromium", "chromium-browser",
              "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"]:
        if c and (shutil.which(c) or os.path.exists(c)):
            return shutil.which(c) or c
    sys.exit("Chrome/Chromium not found: set CHROME=<path>")


def preprocess(md: str) -> str:
    # mermaid fences -> raw HTML the browser renders
    md = re.sub(r"```mermaid\n(.*?)```", lambda m: f'<pre class="mermaid">\n{m.group(1)}</pre>', md, flags=re.S)

    # relative links to repo files -> GitHub (images stay local)
    def link(m: re.Match) -> str:
        text, target = m.group(1), m.group(2)
        if re.match(r"^(https?:|#|mailto:)", target) or target.startswith("img/"):
            return m.group(0)
        path = os.path.normpath(os.path.join("docs", target.split("#")[0])).replace(os.sep, "/")
        anchor = "#" + target.split("#", 1)[1] if "#" in target else ""
        return f"[{text}]({REPO_URL}{path}{anchor})"
    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)", link, md)


def build(name: str) -> str:
    src = os.path.join(DOCS, name)
    with open(src, encoding="utf-8") as f:
        md = preprocess(f.read())
    title = re.search(r"^# (.+)$", md, re.M).group(1)
    html = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5", "--standalone",
                           "--metadata", f"title={title}", "--variable", "title=",
                           "--css", "/dev/null"],
                          input=md, capture_output=True, text=True, check=True).stdout
    html = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    head = f"<style>{CSS}</style>"
    if 'class="mermaid"' in html:
        head += (f'<script src="{MERMAID_JS}"></script>'
                 "<script>mermaid.initialize({startOnLoad:true, theme:'neutral'});</script>")
    html = html.replace("</head>", head + "</head>")
    html = re.sub(r'<header id="title-block-header">.*?</header>', "", html, flags=re.S)
    # write next to the guide so img/ resolves
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=DOCS)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, name.replace(".md", ".pdf"))
    try:
        subprocess.run([chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", "--virtual-time-budget=15000",
                        f"--print-to-pdf={out}", f"file://{tmp}"],
                       check=True, capture_output=True)
    finally:
        os.remove(tmp)
    return out


def main() -> None:
    for name in sys.argv[1:] or GUIDES:
        print("wrote", os.path.relpath(build(name), os.path.dirname(DOCS)))


if __name__ == "__main__":
    main()
