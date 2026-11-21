#!/usr/bin/env python3
"""Generate the diagrams for the guide and the deck, in Spanish and English.

    python docs/img/build_diagrams.py          # SVG only
    python docs/img/build_diagrams.py --png    # SVG + PNG (needs cairosvg; the deck uses the PNGs)

Output: docs/img/<name>.<lang>.svg (+ .png). Same palette as the deck.
"""
from __future__ import annotations

import argparse
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))

BG, PANEL, PANEL_2, STROKE = "#0F141A", "#1A212B", "#222B38", "#2E3948"
CORAL, BLUE, GREEN, AMBER = "#D97757", "#7AA2C7", "#8CC28C", "#D9B25F"
TEXT, MUTED, FAINT = "#E8EAED", "#9AA4B2", "#66707E"
FONT = "Segoe UI, Inter, Helvetica, Arial, sans-serif"
MONO = "Consolas, DejaVu Sans Mono, monospace"


# ----------------------------------------------------------------------------- primitives
class SVG:
    def __init__(self, w: int, h: int):
        self.w, self.h, self.parts = w, h, []

    def add(self, s: str) -> None:
        self.parts.append(s)

    def render(self) -> str:
        defs = (f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker>'
                f'<marker id="arrc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{CORAL}"/></marker></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="{FONT}">{defs}'
                f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>' + "".join(self.parts) + "</svg>")


def wrap(text: str, width_px: float, size: float) -> list[str]:
    per = max(4, int(width_px / (size * 0.54)))
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + (1 if line else 0) > per:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        out.append(line)
    return out


def text(s: SVG, x, y, txt, size=14, color=TEXT, weight="normal", anchor="start", width=None, lh=1.3,
         font=None):
    lines = wrap(txt, width, size) if width else [txt]
    fam = f' font-family="{font}"' if font else ""
    for i, ln in enumerate(lines):
        s.add(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-size="{size}" fill="{color}" '
              f'font-weight="{weight}" text-anchor="{anchor}"{fam}>{escape(ln)}</text>')
    return y + len(lines) * size * lh


def box(s: SVG, x, y, w, h, fill=PANEL, stroke=STROKE, r=12, sw=1.2):
    s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" '
          f'stroke-width="{sw}"/>')


def card(s: SVG, x, y, w, h, title, body, accent=CORAL, num=None, hl=False, size=13):
    box(s, x, y, w, h, fill=PANEL_2 if hl else PANEL, stroke=accent if hl else STROKE, sw=2 if hl else 1.2)
    ty = y + 28
    if num is not None:
        text(s, x + 16, ty, num, 12, accent, "bold")
        ty += 22
    ty = text(s, x + 16, ty, title, 16, TEXT, "bold", width=w - 30)
    text(s, x + 16, ty + 6, body, size, MUTED, width=w - 30)


def arrow(s: SVG, x1, y1, x2, y2, color=MUTED, dash=False):
    mk = "arrc" if color == CORAL else "arr"
    d = ' stroke-dasharray="6 5"' if dash else ""
    s.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d} '
          f'marker-end="url(#{mk})"/>')


SIDE_BAR = True  # off for the deck PNGs: the slide already has its own bar


def header(s: SVG, eyebrow, title):
    if SIDE_BAR:
        s.add(f'<rect x="0" y="0" width="8" height="{s.h}" fill="{CORAL}"/>')
    text(s, 40, 44, eyebrow.upper(), 13, CORAL, "bold")
    text(s, 40, 80, title, 26, TEXT, "bold")


def footer_note(s: SVG, note):
    text(s, 40, s.h - 22, note, 12, FAINT)


# ----------------------------------------------------------------------------- diagrams
def rag_evolution(L):
    s = SVG(1400, 450)
    header(s, L["evo_eyebrow"], L["evo_title"])
    steps = L["evo_steps"]
    n, x0, gap, w = len(steps), 40, 18, (1400 - 80 - 18 * 5) / 6
    for i, (t, b, what) in enumerate(steps):
        x = x0 + i * (w + gap)
        hl = i == n - 1
        card(s, x, 115, w, 205, t, b, accent=CORAL if hl else BLUE, num=f"{i + 1:02d}", hl=hl)
        text(s, x + 16, 282, what, 12, CORAL if hl else GREEN, "bold", width=w - 30)
        if i < n - 1:
            arrow(s, x + w + 2, 218, x + w + gap - 2, 218)
    # axis
    arrow(s, 40, 355, 1360, 355, color=CORAL)
    text(s, 40, 383, L["evo_axis_left"], 13, MUTED)
    text(s, 1360, 383, L["evo_axis_right"], 13, MUTED, anchor="end")
    footer_note(s, L["evo_note"])
    return s


def ontology(L):
    s = SVG(1400, 620)
    header(s, L["onto_eyebrow"], L["onto_title"])
    # schema panel
    box(s, 40, 115, 640, 435, fill=PANEL)
    text(s, 64, 148, L["onto_schema"], 16, BLUE, "bold")
    text(s, 64, 172, L["onto_schema_sub"], 13, MUTED)
    cls = {"Ticket": (90, 230), "Invariant": (420, 230), "Component": (255, 360), "Test": (90, 450)}
    for name, (x, y) in cls.items():
        box(s, x, y - 26, 170, 44, fill=PANEL_2, stroke=BLUE, r=22)
        text(s, x + 85, y + 2, name, 15, TEXT, "bold", anchor="middle")
    def rel(a, b, label, lx, ly):
        (x1, y1), (x2, y2) = cls[a], cls[b]
        arrow(s, x1 + 85 + (40 if x2 > x1 else -40 if x2 < x1 else 0), y1 + 18,
              x2 + 85 - (40 if x2 > x1 else -40 if x2 < x1 else 0), y2 - 28, color=BLUE)
        text(s, lx, ly, label, 13, BLUE, font=MONO)
    arrow(s, 260, 230, 418, 230, color=BLUE)
    text(s, 300, 220, "originates", 13, BLUE, font=MONO)
    rel("Ticket", "Component", "touches", 272, 292)
    rel("Invariant", "Component", "guards", 440, 300)
    arrow(s, 175, 252, 175, 422, color=BLUE)
    text(s, 185, 395, "verified_by", 13, BLUE, font=MONO)
    text(s, 64, 508, L["onto_constraint"], 13, AMBER, width=590)
    # instances panel
    box(s, 720, 115, 640, 435, fill=PANEL)
    text(s, 744, 148, L["onto_facts"], 16, GREEN, "bold")
    text(s, 744, 172, L["onto_facts_sub"], 13, MUTED)
    facts = [("TKT-104", "touches", "letter_end_detection"),
             ("TKT-101", "originates", "INV-07  (DOC != PDF lists)"),
             ("INV-07", "guards", "letter_end_detection"),
             ("TKT-104", "verified_by", "tests/test_tkt_104_*.py"),
             ("TKT-157", "must_not_break", "TKT-104")]
    y = 220
    for a, r, b in facts:
        box(s, 744, y - 24, 592, 40, fill=BG, stroke=STROKE, r=8)
        text(s, 760, y + 2, a, 14, TEXT, "bold", font=MONO)
        text(s, 880, y + 2, r, 14, GREEN, font=MONO)
        text(s, 1030, y + 2, b, 14, TEXT, font=MONO)
        y += 56
    text(s, 744, 508, L["onto_alt"], 13, MUTED, width=590)
    footer_note(s, L["onto_note"])
    return s


def ograg_pipeline(L):
    s = SVG(1400, 470)
    header(s, L["og_eyebrow"], L["og_title"])
    steps = L["og_steps"]
    w, gap = (1400 - 80 - 4 * 24) / 5, 24
    for i, (t, b) in enumerate(steps):
        x = 40 + i * (w + gap)
        card(s, x, 115, w, 160, t, b, accent=CORAL if i in (0, 3) else BLUE, num=f"{i + 1:02d}", hl=i == 0)
        if i < 4:
            arrow(s, x + w + 2, 195, x + w + gap - 2, 195)
    box(s, 40, 300, 1320, 120, fill="#0A0E13")
    text(s, 64, 330, L["og_block_title"], 13, BLUE, "bold")
    text(s, 64, 360, '{"@type": "Crop", "name": "Soybean",', 15, TEXT, font=MONO)
    text(s, 64, 385, ' "isGrownIn": {"@type": "CropRegion", "name": "Madhya Pradesh"},', 15, TEXT, font=MONO)
    text(s, 64, 410, ' "sowingTime": "mid-June to early July"}', 15, TEXT, font=MONO)
    text(s, 1330, 410, L["og_block_note"], 13, MUTED, anchor="end")
    footer_note(s, L["og_note"])
    return s


def kg_pipeline(L):
    s = SVG(1400, 560)
    header(s, L["kg_eyebrow"], L["kg_title"])
    text(s, 40, 120, L["kg_build"], 14, CORAL, "bold")
    build = L["kg_build_steps"]
    w, gap = (1400 - 80 - 4 * 22) / 5, 22
    for i, (t, b) in enumerate(build):
        x = 40 + i * (w + gap)
        card(s, x, 135, w, 130, t, b, accent=CORAL if i == 2 else BLUE, hl=i == 2, size=12)
        if i < 4:
            arrow(s, x + w + 2, 200, x + w + gap - 2, 200)
    text(s, 40, 305, L["kg_query"], 14, GREEN, "bold")
    q = L["kg_query_steps"]
    w2 = (1400 - 80 - 3 * 22) / 4
    for i, (t, b) in enumerate(q):
        x = 40 + i * (w2 + 22)
        card(s, x, 320, w2, 115, t, b, accent=GREEN, hl=i == 3, size=12)
        if i < 3:
            arrow(s, x + w2 + 2, 377, x + w2 + 20, 377)
    arrow(s, 1290, 267, 1290, 318, dash=True)
    text(s, 40, 478, L["kg_lesson"], 13, AMBER, width=1320)
    footer_note(s, L["kg_note"])
    return s


def demo_oag_pipeline(L):
    s = SVG(1400, 420)
    header(s, L["do_eyebrow"], L["do_title"])
    steps = L["do_steps"]
    w, gap = (1400 - 80 - 4 * 24) / 5, 24
    for i, (t, b) in enumerate(steps):
        x = 40 + i * (w + gap)
        card(s, x, 115, w, 160, t, b, accent=AMBER if i == 2 else BLUE, num=f"{i + 1:02d}", hl=i == 0)
        if i < 4:
            arrow(s, x + w + 2, 195, x + w + gap - 2, 195)
    box(s, 40, 300, 1320, 64, fill=PANEL_2)
    text(s, 64, 338, L["do_bottom"], 14, TEXT, width=1280)
    footer_note(s, L["do_note"])
    return s


def evaluation(L):
    s = SVG(1400, 600)
    header(s, L["ev_eyebrow"], L["ev_title"])
    box(s, 40, 130, 300, 140, fill=PANEL_2, stroke=CORAL, sw=2)
    text(s, 60, 165, L["ev_q"], 16, TEXT, "bold")
    text(s, 60, 192, L["ev_q_body"], 13, MUTED, width=265)
    box(s, 40, 320, 300, 170, fill=PANEL, stroke=AMBER, sw=2)
    text(s, 60, 355, L["ev_key"], 16, AMBER, "bold")
    text(s, 60, 382, L["ev_key_body"], 13, MUTED, width=265)
    techs = L["ev_techs"]
    for i, (t, b) in enumerate(techs):
        y = 120 + i * 92
        box(s, 430, y, 420, 76)
        text(s, 450, y + 30, t, 15, TEXT, "bold")
        text(s, 450, y + 54, b, 12, MUTED, width=390)
        arrow(s, 342, 200, 428, y + 38)
        arrow(s, 852, y + 38, 948, 300)
    box(s, 950, 200, 410, 200, fill=PANEL_2, stroke=GREEN, sw=2)
    text(s, 972, 235, L["ev_metrics"], 16, GREEN, "bold")
    y = 265
    for m in L["ev_metric_lines"]:
        y = text(s, 972, y, m, 13, TEXT, width=370) + 6
    arrow(s, 342, 405, 948, 360, color=AMBER, dash=True)
    text(s, 40, 545, L["ev_warn"], 13, AMBER, width=1320)
    footer_note(s, L["ev_note"])
    return s


def when_to_use(L):
    s = SVG(1400, 720)
    header(s, L["wu_eyebrow"], L["wu_title"])
    cols = L["wu_cols"]
    xs = [40, 270, 600, 930]
    ws = [220, 320, 320, 430]
    y = 120
    for x, w, c in zip(xs, ws, cols):
        box(s, x, y, w - 10, 42, fill=PANEL_2)
        text(s, x + 14, y + 27, c, 14, CORAL if x > 40 else MUTED, "bold")
    for r, row in enumerate(L["wu_rows"]):
        yy = y + 52 + r * 82
        for i, (x, w, cell) in enumerate(zip(xs, ws, row)):
            box(s, x, yy, w - 10, 72, fill=PANEL_2 if r == len(L["wu_rows"]) - 1 and i == 0 else PANEL,
                stroke=CORAL if r == len(L["wu_rows"]) - 1 and i == 0 else STROKE)
            text(s, x + 14, yy + 26, cell, 14 if i == 0 else 12.5, BLUE if i == 0 else TEXT,
                 "bold" if i == 0 else "normal", width=w - 36)
    footer_note(s, L["wu_note"])
    return s


# ----------------------------------------------------------------------------- strings
ES = dict(
    evo_eyebrow="De RAG a OAG", evo_title="Seis generaciones de recuperación aumentada",
    evo_steps=[
        ("Naive RAG", "Trocear, vectorizar y recuperar el top-k por similitud.", "Recupera: trozos"),
        ("RAG + rerank", "Un segundo modelo reordena lo recuperado.", "Recupera: trozos mejor ordenados"),
        ("Modular RAG", "Reescritura de la consulta, búsqueda híbrida, routing.", "Recupera: trozos de varias fuentes"),
        ("Agentic RAG", "El agente planifica, busca en bucle y se corrige.", "Recupera: lo que el agente decide leer"),
        ("GraphRAG", "Grafo de entidades y comunidades extraído por un LLM; esquema libre.", "Recupera: vecinos y resúmenes"),
        ("OAG", "Una ontología definida antes guía extracción, validación y recuperación.", "Recupera: hechos tipados con fuente"),
    ],
    evo_axis_left="Menos estructura: barato de montar, el LLM interpreta",
    evo_axis_right="Más estructura: el dominio decide qué es un hecho",
    evo_note="Gao et al. 2023 (arXiv 2312.10997), Singh et al. 2025 (arXiv 2501.09136), Edge et al. 2024 (arXiv 2404.16130), Sharma et al. 2024 (arXiv 2412.15235).",
    onto_eyebrow="Conceptos", onto_title="Ontología: el esquema y los hechos",
    onto_schema="Esquema (qué PUEDE existir)", onto_schema_sub="Clases y relaciones con dominio y rango",
    onto_constraint="Restricción: «guards» solo sale de un Invariant y llega a un Component; toda arista tiene fichero fuente.",
    onto_facts="Hechos (qué ES verdad hoy)", onto_facts_sub="Instancias que cumplen el esquema",
    onto_alt="Sinónimos (altLabels): get_letter_end, LETTER_END_*, «fin de carta» y «end-of-letter» son el mismo Component.",
    onto_note="Ejemplo sanitizado del dominio de tickets. Definición clásica: «especificación explícita de una conceptualización» (Gruber, 1993).",
    og_eyebrow="OG-RAG (Microsoft Research)", og_title="El pipeline de OG-RAG",
    og_steps=[
        ("Ontología", "Triples (sujeto, atributo, valor) escritos o revisados por expertos."),
        ("Preproceso", "Un LLM mapea cada documento a la ontología y emite fact blocks JSON-LD."),
        ("Hipergrafo", "Cada fact block es una hiperarista; cada par clave-valor, un hipernodo."),
        ("Recuperación", "Top-k nodos por clave y por valor; greedy: mínimo conjunto de hiperaristas que los cubre."),
        ("Generación", "Los hechos van al prompt. Cero llamadas LLM extra al consultar."),
    ],
    og_block_title="Un fact block (simplificado, del paper)", og_block_note="un fact block = una hiperarista",
    og_note="Sharma, Kumar y Li, OG-RAG, arXiv 2412.15235 (2024), EMNLP 2025.",
    kg_eyebrow="Nuestro sistema", kg_title="La pipeline del grafo de tickets (/kg-refresh y /kg)",
    kg_build="Construcción: /kg-refresh (se paga una vez)",
    kg_build_steps=[
        ("Manifest", "build_manifest.py elige ~341 ficheros: writeups, hubs, procesos, memoria."),
        ("Corpus", "stage_corpus.py aplana con nombres que guardan la procedencia (sst-NNNN__…)."),
        ("/graphify", "~22 subagentes LLM extraen nodos y aristas. El prompt fija la convención de IDs."),
        ("Canonicalizar", "Fusión de IDs duplicados, censo de convención, leak-check."),
        ("Nombres", "community_labels.json: nombres de comunidad, remap y auditoría manual."),
    ],
    kg_query="Consulta: /kg (determinista, sin LLM)",
    kg_query_steps=[
        ("Tema", "/kg get_letter_end, /kg SST-A SST-B, /kg find <texto>"),
        ("graph.json", "explain (vecinos), path (camino), find (subcadena)."),
        ("Danger zone", "Comunidad con nombre + conexiones: tickets, sharp edges, rationales."),
        ("Leer el writeup", "El grafo apunta; el writeup manda (regla history-first)."),
    ],
    kg_lesson="Lo aprendido: sin esquema, cada refresh reinventa IDs y tipos. Supervivencia de IDs entre reconstrucciones: 12,6 % antes de fijar la convención en el prompt, 35-43 % después. Unas tres cuartas partes de las aristas son genéricas (references).",
    kg_note="Fuente: KG_PROCEDURES.md y EXTRACTION_PROMPT del repo lambda; reference/KNOWLEDGE_GRAPH.md.",
    do_eyebrow="Demo", do_title="OAG en la demo: ontología primero, hechos después",
    do_steps=[
        ("ontology.yaml", "4 clases, 5 relaciones, componentes con sinónimos y reglas de extracción."),
        ("Extracción", "Parser determinista: títulos, tablas de invariantes, citas, tests y sinónimos."),
        ("Validación", "Se rechaza lo que el esquema no permite (p. ej. menciones genéricas) y se informa."),
        ("facts.json", "Nodos y aristas tipados, cada uno con su fichero fuente."),
        ("Consulta", "Pregunta → componente (altLabels) → set cover greedy → fact blocks."),
    ],
    do_bottom="Sin LLM al construir ni al consultar. En producción la extracción se completaría con un LLM guiado por la misma ontología (Fase C), siempre validado.",
    do_note="demo/oag.py y demo/oag/ontology.yaml.",
    ev_eyebrow="Demo", ev_title="Cómo evaluamos: una pregunta real, una hoja de respuestas",
    ev_q="Pregunta", ev_q_body="Bug real ya resuelto, planteado como si fuera nuevo.",
    ev_key="Hoja de respuestas", ev_key_body="El writeup del bug lista lo que no hay que romper. Se excluye de todas las técnicas (hold-out).",
    ev_techs=[("Naive RAG", "trozos por similitud"), ("Agentic RAG", "Claude busca y lee en bucle"),
              ("GraphRAG (/kg)", "vecinos + lista de lectura"), ("OAG", "hechos tipados validados")],
    ev_metrics="Métricas",
    ev_metric_lines=["Recall: esperados encontrados / esperados", "Precisión: esperados encontrados / devueltos",
                     "Coste: tokens de contexto y llamadas LLM", "Respuesta final de Claude, registrada"],
    ev_warn="Una pregunta no es una evaluación: la lista esperada es un mínimo y el corpus es pequeño. La evaluación seria es el Paso 0 (15-20 preguntas).",
    ev_note="demo/compare.py y demo/record_answer.py.",
    wu_eyebrow="Guía de uso", wu_title="Cuándo conviene cada técnica",
    wu_cols=["Técnica", "Conviene cuando", "Coste y riesgo", "Ejemplo en nuestro trabajo"],
    wu_rows=[
        ["Sin RAG", "Todo el contexto cabe en la ventana del modelo.", "Ninguno extra; coste por tokens.", "Un ticket y su writeup en una sesión."],
        ["Naive RAG", "Preguntas puntuales sobre mucho texto sin estructura.", "Barato; recupera trozos sueltos y ruido.", "Buscar dónde se menciona un error concreto."],
        ["RAG + rerank / híbrido", "Vocabulario variado o nombres exactos (IDs, símbolos).", "Un modelo más; mejor precisión.", "IDs de ticket y nombres de función."],
        ["Agentic RAG", "Preguntas exploratorias o de varios pasos.", "Más tokens y pasos; varía entre ejecuciones.", "Investigar la causa raíz de un bug nuevo."],
        ["GraphRAG", "Relaciones y temas globales; «qué hay alrededor de X».", "Construcción cara; esquema inestable.", "/kg: zona de peligro antes de tocar código."],
        ["OAG", "Hechos tipados, reglas, auditoría y atribución.", "Escribir y mantener la ontología.", "Invariantes a respetar antes del merge."],
    ],
    wu_note="Regla práctica: empezar por lo más simple que responda las preguntas reales, y medir antes de subir de nivel.",
)

EN = dict(
    evo_eyebrow="From RAG to OAG", evo_title="Six generations of retrieval augmentation",
    evo_steps=[
        ("Naive RAG", "Chunk, vectorise and retrieve the top-k by similarity.", "Retrieves: chunks"),
        ("RAG + rerank", "A second model reorders what was retrieved.", "Retrieves: better-ordered chunks"),
        ("Modular RAG", "Query rewriting, hybrid search, routing.", "Retrieves: chunks from several sources"),
        ("Agentic RAG", "The agent plans, searches in a loop and self-corrects.", "Retrieves: what the agent chooses to read"),
        ("GraphRAG", "LLM-extracted entity graph and communities; free schema.", "Retrieves: neighbours and summaries"),
        ("OAG", "An ontology defined up front guides extraction, validation and retrieval.", "Retrieves: typed facts with sources"),
    ],
    evo_axis_left="Less structure: cheap to set up, the LLM interprets",
    evo_axis_right="More structure: the domain decides what a fact is",
    evo_note="Gao et al. 2023 (arXiv 2312.10997), Singh et al. 2025 (arXiv 2501.09136), Edge et al. 2024 (arXiv 2404.16130), Sharma et al. 2024 (arXiv 2412.15235).",
    onto_eyebrow="Concepts", onto_title="Ontology: the schema and the facts",
    onto_schema="Schema (what CAN exist)", onto_schema_sub="Classes and relations with domain and range",
    onto_constraint="Constraint: «guards» only goes from an Invariant to a Component; every edge has a source file.",
    onto_facts="Facts (what IS true today)", onto_facts_sub="Instances that conform to the schema",
    onto_alt="Synonyms (altLabels): get_letter_end, LETTER_END_*, «fin de carta» and «end-of-letter» are the same Component.",
    onto_note="Sanitised example from the ticket domain. Classic definition: «an explicit specification of a conceptualization» (Gruber, 1993).",
    og_eyebrow="OG-RAG (Microsoft Research)", og_title="The OG-RAG pipeline",
    og_steps=[
        ("Ontology", "Triples (subject, attribute, value) written or reviewed by experts."),
        ("Preprocessing", "An LLM maps each document to the ontology and emits JSON-LD fact blocks."),
        ("Hypergraph", "Each fact block is a hyperedge; each key-value pair, a hypernode."),
        ("Retrieval", "Top-k nodes by key and by value; greedy: the smallest set of hyperedges covering them."),
        ("Generation", "The facts go into the prompt. No extra LLM calls at query time."),
    ],
    og_block_title="A fact block (simplified, from the paper)", og_block_note="one fact block = one hyperedge",
    og_note="Sharma, Kumar and Li, OG-RAG, arXiv 2412.15235 (2024), EMNLP 2025.",
    kg_eyebrow="Our system", kg_title="The ticket graph pipeline (/kg-refresh and /kg)",
    kg_build="Build: /kg-refresh (paid once)",
    kg_build_steps=[
        ("Manifest", "build_manifest.py picks ~341 files: writeups, hubs, process notes, memory."),
        ("Corpus", "stage_corpus.py flattens with provenance-preserving names (sst-NNNN__…)."),
        ("/graphify", "~22 LLM subagents extract nodes and edges. The prompt pins the ID convention."),
        ("Canonicalise", "Merge duplicate IDs, convention census, leak check."),
        ("Names", "community_labels.json: community names, remap and manual audit."),
    ],
    kg_query="Query: /kg (deterministic, no LLM)",
    kg_query_steps=[
        ("Topic", "/kg get_letter_end, /kg SST-A SST-B, /kg find <text>"),
        ("graph.json", "explain (neighbours), path (shortest path), find (substring)."),
        ("Danger zone", "Named community + connections: tickets, sharp edges, rationales."),
        ("Read the writeup", "The graph points; the writeup rules (history-first)."),
    ],
    kg_lesson="Lesson: without a schema every refresh reinvents IDs and types. Node-ID survival across rebuilds: 12.6% before pinning the convention in the prompt, 35-43% after. About three quarters of the edges are generic (references).",
    kg_note="Source: KG_PROCEDURES.md and EXTRACTION_PROMPT in the lambda repo; reference/KNOWLEDGE_GRAPH.md.",
    do_eyebrow="Demo", do_title="OAG in the demo: ontology first, facts second",
    do_steps=[
        ("ontology.yaml", "4 classes, 5 relations, components with synonyms and extraction rules."),
        ("Extraction", "Deterministic parser: titles, invariant tables, citations, tests and synonyms."),
        ("Validation", "Whatever the schema does not allow is rejected (e.g. generic mentions) and reported."),
        ("facts.json", "Typed nodes and edges, each with its source file."),
        ("Query", "Question → component (altLabels) → greedy set cover → fact blocks."),
    ],
    do_bottom="No LLM at build or query time. In production, extraction would be completed by an LLM guided by the same ontology (Phase C), always validated.",
    do_note="demo/oag.py and demo/oag/ontology.yaml.",
    ev_eyebrow="Demo", ev_title="How we evaluate: one real question, one answer key",
    ev_q="Question", ev_q_body="A real, already solved bug, asked as if it were new.",
    ev_key="Answer key", ev_key_body="The bug's writeup lists what must not break. It is excluded from every technique (hold-out).",
    ev_techs=[("Naive RAG", "chunks by similarity"), ("Agentic RAG", "Claude searches and reads in a loop"),
              ("GraphRAG (/kg)", "neighbours + reading list"), ("OAG", "validated typed facts")],
    ev_metrics="Metrics",
    ev_metric_lines=["Recall: expected found / expected", "Precision: expected found / returned",
                     "Cost: context tokens and LLM calls", "Claude's final answer, recorded"],
    ev_warn="One question is not an evaluation: the expected list is a floor and the corpus is small. The real evaluation is Step 0 (15-20 questions).",
    ev_note="demo/compare.py and demo/record_answer.py.",
    wu_eyebrow="Usage guide", wu_title="When each technique fits",
    wu_cols=["Technique", "Fits when", "Cost and risk", "Example in our work"],
    wu_rows=[
        ["No RAG", "The whole context fits in the model window.", "Nothing extra; token cost.", "One ticket and its writeup in a session."],
        ["Naive RAG", "Point questions over lots of unstructured text.", "Cheap; returns loose chunks and noise.", "Find where a specific error is mentioned."],
        ["RAG + rerank / hybrid", "Varied vocabulary or exact names (IDs, symbols).", "One more model; better precision.", "Ticket IDs and function names."],
        ["Agentic RAG", "Exploratory or multi-step questions.", "More tokens and steps; varies between runs.", "Investigate the root cause of a new bug."],
        ["GraphRAG", "Relations and global themes; «what is around X».", "Costly build; unstable schema.", "/kg: danger zone before touching code."],
        ["OAG", "Typed facts, rules, auditing and attribution.", "Writing and maintaining the ontology.", "Invariants to respect before a merge."],
    ],
    wu_note="Rule of thumb: start with the simplest technique that answers the real questions, and measure before moving up.",
)

DIAGRAMS = {
    "rag_evolution": rag_evolution,
    "ontology": ontology,
    "ograg_pipeline": ograg_pipeline,
    "kg_pipeline": kg_pipeline,
    "demo_oag_pipeline": demo_oag_pipeline,
    "evaluation": evaluation,
    "when_to_use": when_to_use,
}


def main() -> None:
    global SIDE_BAR
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="also write the PNGs the deck uses (needs cairosvg)")
    a = ap.parse_args()
    for lang, L in (("es", ES), ("en", EN)):
        for name, fn in DIAGRAMS.items():
            SIDE_BAR = True
            svg = fn(L).render()
            path = os.path.join(HERE, f"{name}.{lang}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            print("wrote", os.path.relpath(path, os.path.dirname(os.path.dirname(HERE))))
            if a.png:
                import cairosvg
                SIDE_BAR = False
                deck_svg = fn(L).render()
                cairosvg.svg2png(bytestring=deck_svg.encode("utf-8"),
                                 write_to=os.path.join(HERE, f"{name}.{lang}.png"), output_width=2400)


if __name__ == "__main__":
    main()
