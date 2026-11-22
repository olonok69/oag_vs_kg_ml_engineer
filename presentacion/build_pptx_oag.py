#!/usr/bin/env python3
"""
Generador del deck "Ontology-Augmented Generation vs el grafo de tickets".

Mismo estilo que presentacion/build_pptx.py (paleta, eyebrow + título, tarjetas,
franja de conclusión, footer). Idempotente: re-ejecutar regenera el .pptx.

    pip install python-pptx
    python build_pptx_oag.py

Salida: OAG_vs_KG_Presentacion.pptx (16:9, 13.33 x 7.5").
"""
from __future__ import annotations
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

# ----------------------------------------------------------------------------- paleta
BG       = RGBColor(0x0F, 0x14, 0x1A)   # slate casi negro
PANEL    = RGBColor(0x1A, 0x21, 0x2B)   # tarjeta
PANEL_2  = RGBColor(0x22, 0x2B, 0x38)   # tarjeta alt / highlight
STROKE   = RGBColor(0x2E, 0x39, 0x48)   # borde sutil
CORAL    = RGBColor(0xD9, 0x77, 0x57)   # acento primario (Anthropic)
BLUE     = RGBColor(0x7A, 0xA2, 0xC7)   # acento secundario
GREEN    = RGBColor(0x8C, 0xC2, 0x8C)
AMBER    = RGBColor(0xD9, 0xB2, 0x5F)
TEXT     = RGBColor(0xE8, 0xEA, 0xED)   # texto principal
MUTED    = RGBColor(0x9A, 0xA4, 0xB2)   # texto secundario
FAINT    = RGBColor(0x66, 0x70, 0x7E)   # footer
FONT     = "Segoe UI"
MONO     = "Consolas"

EMU_W, EMU_H = Inches(13.333), Inches(7.5)

# ----------------------------------------------------------------------------- idioma
# El deck se dibuja SIEMPRE en castellano; `--lang en` traduce línea a línea al
# emitir, usando presentacion/translations_en.py. Así hay UN solo layout que
# mantener: añadir una slide la añade en los dos idiomas, y lo único que puede
# faltar es su traducción (que se reporta al final, no se traga en silencio).
LANG = "es"
_MISSES: list[str] = []
_SOFT: list[str] = []


def _translate(para):
    """para: lista de tuplas R(). Devuelve la versión traducida si LANG != es."""
    if LANG == "es":
        return para
    import sys

    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    from translations_en import TRANSLATIONS

    key = "".join(t for (t, *_rest) in para)
    if not key.strip():
        return para
    en = TRANSLATIONS.get(key)
    if isinstance(en, str):
        # A plain string replaces the content runs and keeps the marker runs ("▸  ", "“ ", " ”").
        out, placed = [], False
        for (t, *rest) in para:
            if not any(ch.isalnum() for ch in t):
                out.append((t, *rest))
            elif not placed:
                out.append((en, *rest))
                placed = True
            else:
                out.append(("", *rest))
        return out
    if en is None:
        # Solo interesa avisar de prosa: el código, las URLs y los nombres propios
        # pasan tal cual a propósito.
        if any(ch.isalpha() for ch in key) and len(key) > 3:
            _MISSES.append(key)
        return para
    if len(en) != len(para):
        # Los decks se re-guardaron en PowerPoint, que FUSIONA runs adyacentes con el
        # mismo formato: una línea que aquí se emite en 5 runs puede estar en el deck
        # como 1. Se conservan los runs iniciales que coinciden literalmente (marcadores
        # tipo "▸  " o "■ ", idénticos en ambos idiomas) y el resto se junta en el
        # siguiente run — así no se pierde texto y el marcador mantiene su color.
        keep = 0
        while keep < min(len(en), len(para)) and en[keep] == para[keep][0]:
            keep += 1
        merged = "".join(en[keep:])
        out = []
        for i, (t, *rest) in enumerate(para):
            if i < keep:
                out.append((en[i], *rest))
            elif i == keep:
                out.append((merged, *rest))
            else:
                out.append(("", *rest))
        _SOFT.append(f"[runs {len(para)}<-{len(en)}, merged at {keep}] {key[:70]}")
        return out
    return [(en[i], *rest) for i, (t, *rest) in enumerate(para)]


# ----------------------------------------------------------------------------- helpers
def _solid(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def _noline(shape):
    shape.line.fill.background()


def _line(shape, color, w=0.75):
    shape.line.color.rgb = color
    shape.line.width = Pt(w)


def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, rounded=False, radius=0.08):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    if rounded:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        shp.fill.background()
    else:
        _solid(shp, fill)
    if line is None:
        _noline(shp)
    else:
        _line(shp, line, lw)
    shp.shadow.inherit = False
    return shp


def text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         space_after=4, line_spacing=1.0):
    """runs: lista de párrafos; cada párrafo es lista de (txt, size, color, bold, font)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, para in enumerate(runs):
        para = _translate(para)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.space_before = Pt(0)
        p.line_spacing = line_spacing
        for (t, size, color, bold, font) in para:
            r = p.add_run()
            r.text = t
            r.font.size = Pt(size)
            r.font.color.rgb = color
            r.font.bold = bold
            r.font.name = font
    return tb


def R(t, size, color, bold=False, font=FONT):
    return (t, size, color, bold, font)


# ----------------------------------------------------------------------------- chrome
def base(slide, eyebrow=None, ttl=None, page=None):
    rect(slide, -0.1, -0.1, 13.53, 7.7, fill=BG)                     # fondo
    rect(slide, 0, 0, 0.22, 7.5, fill=CORAL)                         # barra lateral
    if eyebrow:
        text(slide, 0.7, 0.55, 11, 0.4,
             [[R(eyebrow.upper(), 12, CORAL, True)]])
    if ttl:
        text(slide, 0.68, 0.92, 12, 1.1, [[R(ttl, 30, TEXT, True)]])
        rect(slide, 0.72, 1.72, 1.1, 0.045, fill=CORAL)
    if page is not None:
        text(slide, 0.7, 7.02, 8, 0.35,
             [[R("OAG vs grafo de tickets · Investigación", 9.5, FAINT, False)]])
        text(slide, 11.8, 7.02, 1.2, 0.35,
             [[R(str(page), 9.5, FAINT, True)]], align=PP_ALIGN.RIGHT)


def takeaway(slide, phrase):
    """Franja de conclusión (🗣️) al pie."""
    y = 6.35
    rect(slide, 0.7, y, 11.95, 0.52, fill=PANEL_2, line=STROKE, rounded=True, radius=0.28)
    rect(slide, 0.7, y, 0.09, 0.52, fill=CORAL, rounded=True, radius=0.5)
    text(slide, 0.95, y + 0.03, 11.6, 0.46,
         [[R("“ ", 13, CORAL, True), R(phrase, 12.5, TEXT, False),
           R(" ”", 13, CORAL, True)]], anchor=MSO_ANCHOR.MIDDLE)


def cards(slide, items, top=2.1, cols=2, height=1.02, gap=0.28, badge=CORAL, bottom_takeaway=True,
          left=0.7, right=12.65):
    """items: lista de (num, titulo, descripcion). Rejilla de tarjetas numeradas."""
    total_w = right - left
    card_w = (total_w - gap * (cols - 1)) / cols
    for idx, (num, ttl, desc) in enumerate(items):
        r, c = divmod(idx, cols)
        x = left + c * (card_w + gap)
        y = top + r * (height + gap)
        rect(slide, x, y, card_w, height, fill=PANEL, line=STROKE, rounded=True, radius=0.09)
        # badge
        rect(slide, x + 0.22, y + 0.22, 0.5, 0.5, fill=badge, rounded=True, radius=0.32)
        text(slide, x + 0.22, y + 0.24, 0.5, 0.46,
             [[R(str(num), 15, BG, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(slide, x + 0.9, y + 0.16, card_w - 1.05, 0.4,
             [[R(ttl, 14.5, TEXT, True)]])
        text(slide, x + 0.9, y + 0.5, card_w - 1.05, height - 0.55,
             [[R(desc, 11, MUTED, False)]], line_spacing=1.02)


def code(slide, x, y, w, h, lines, title=None):
    if title:
        text(slide, x, y - 0.34, w, 0.3, [[R(title, 11, BLUE, True)]])
    rect(slide, x, y, w, h, fill=RGBColor(0x0A, 0x0E, 0x13), line=STROKE, rounded=True, radius=0.05)
    runs = [[R(ln, 11.5, TEXT if not ln.startswith("#") else MUTED, False, MONO)] for ln in lines]
    text(slide, x + 0.28, y + 0.2, w - 0.5, h - 0.35, runs, line_spacing=1.12, space_after=2)


def panel_bullets(slide, x, y, w, h, header, bullets, accent=CORAL):
    rect(slide, x, y, w, h, fill=PANEL, line=STROKE, rounded=True, radius=0.06)
    text(slide, x + 0.3, y + 0.22, w - 0.5, 0.4, [[R(header, 14, accent, True)]])
    runs = []
    for b in bullets:
        runs.append([R("▸  ", 11.5, accent, True), R(b, 11.5, TEXT, False)])
    text(slide, x + 0.3, y + 0.72, w - 0.55, h - 0.9, runs, line_spacing=1.05, space_after=6)


def divider(slide, part, ttl, subtitle, items, page=None):
    """Separador de parte: número grande + título + lista de secciones."""
    rect(slide, -0.1, -0.1, 13.53, 7.7, fill=BG)
    rect(slide, 0, 0, 13.333, 0.16, fill=CORAL)
    rect(slide, 0, 7.34, 13.333, 0.16, fill=CORAL)
    text(slide, 1.0, 1.3, 11, 0.5, [[R(f"PARTE {part}", 16, CORAL, True)]])
    text(slide, 0.95, 1.8, 11.5, 1.2, [[R(ttl, 44, TEXT, True)]])
    rect(slide, 1.02, 2.85, 1.4, 0.05, fill=CORAL)
    text(slide, 1.0, 3.05, 11.3, 0.6, [[R(subtitle, 15, MUTED, False)]], line_spacing=1.1)
    y = 3.85
    for i, it in enumerate(items):
        r, c = divmod(i, 2)
        x = 1.0 + c * 6.0
        yy = y + r * 0.62
        rect(slide, x, yy, 5.7, 0.52, fill=PANEL, line=STROKE, rounded=True, radius=0.16)
        text(slide, x + 0.25, yy + 0.05, 5.3, 0.42, [[R(it, 12.5, TEXT, False)]],
             anchor=MSO_ANCHOR.MIDDLE)
    if page is not None:
        text(slide, 11.8, 7.02, 1.2, 0.35, [[R(str(page), 9.5, FAINT, True)]],
             align=PP_ALIGN.RIGHT)




def table(slide, x, y, col_w, rows, row_h=0.5, header_color=CORAL, first_col_color=BLUE, size=10.5):
    """rows[0] = cabecera. col_w = lista de anchos."""
    for r, row in enumerate(rows):
        yy = y + r * (row_h + 0.06)
        xx = x
        for c, cell in enumerate(row):
            w = col_w[c]
            if r == 0:
                rect(slide, xx, yy, w - 0.06, row_h, fill=PANEL_2, line=STROKE, rounded=True, radius=0.12)
                col = header_color if c else MUTED
                text(slide, xx + 0.15, yy, w - 0.3, row_h, [[R(cell, size + 1, col, True)]],
                     anchor=MSO_ANCHOR.MIDDLE)
            else:
                rect(slide, xx, yy, w - 0.06, row_h, fill=PANEL, line=STROKE, rounded=True, radius=0.12)
                if c == 0:
                    text(slide, xx + 0.15, yy, w - 0.3, row_h, [[R(cell, size, first_col_color, True)]],
                         anchor=MSO_ANCHOR.MIDDLE)
                else:
                    text(slide, xx + 0.15, yy, w - 0.3, row_h, [[R(cell, size, TEXT, False)]],
                         anchor=MSO_ANCHOR.MIDDLE, line_spacing=0.98)
            xx += w


def steps(slide, items, y=2.2, h=1.9, accent=CORAL):
    """Fila de pasos con flecha: items = (titulo, desc)."""
    n = len(items)
    left, right = 0.7, 12.65
    gap = 0.3
    w = (right - left - gap * (n - 1)) / n
    for i, (t, d) in enumerate(items):
        x = left + i * (w + gap)
        hl = (i == n - 1)
        rect(slide, x, y, w, h, fill=PANEL_2 if hl else PANEL, line=accent if hl else STROKE,
             lw=1.5 if hl else 0.75, rounded=True, radius=0.08)
        text(slide, x + 0.18, y + 0.15, w - 0.3, 0.3, [[R(f"{i + 1:02d}", 11, accent, True)]])
        text(slide, x + 0.18, y + 0.45, w - 0.3, 0.6, [[R(t, 13, TEXT, True)]], line_spacing=0.95)
        text(slide, x + 0.18, y + 1.05, w - 0.3, h - 1.1, [[R(d, 10, MUTED, False)]], line_spacing=1.0)
        if i < n - 1:
            text(slide, x + w - 0.02, y + h / 2 - 0.2, gap + 0.05, 0.4, [[R("›", 20, accent, True)]],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "img")


def diagram(slide, name, page=None):
    """Slide completa con un diagrama de docs/img (el PNG ya lleva su eyebrow y título)."""
    from PIL import Image

    base(slide, page=page)
    path = os.path.join(IMG_DIR, f"{name}.{LANG}.png")
    with Image.open(path) as im:
        iw, ih = im.size
    box_x, box_y, box_w, box_h = 0.3, 0.25, 12.95, 6.65
    scale = min(box_w / iw, box_h / ih)
    w, h = iw * scale, ih * scale
    slide.shapes.add_picture(path, Inches(box_x + (box_w - w) / 2), Inches(box_y + (box_h - h) / 2),
                             Inches(w), Inches(h))


def build():
    prs = Presentation()
    prs.slide_width = EMU_W
    prs.slide_height = EMU_H
    blank = prs.slide_layouts[6]
    _pg = [0]

    def new():
        _pg[0] += 1
        return prs.slides.add_slide(blank), _pg[0]

    # ---- 1. Portada
    s, _ = new()
    rect(s, -0.1, -0.1, 13.53, 7.7, fill=BG)
    rect(s, 0, 0, 13.333, 0.16, fill=CORAL)
    rect(s, 0, 7.34, 13.333, 0.16, fill=CORAL)
    text(s, 1.0, 1.4, 11, 0.5, [[R("CHARLA Y DEMO · METODOLOGÍA DE AGENTES IA", 14, CORAL, True)]])
    text(s, 0.95, 2.0, 11.5, 2.0,
         [[R("Ontology-Augmented Generation", 50, TEXT, True)],
          [R("De Naive RAG a OAG sobre nuestro ", 26, MUTED, False), R("grafo de tickets", 26, TEXT, True)],
          [R("Charla y demo en directo: dónde gana cada técnica y si merece la pena adoptarla", 17, MUTED, False)]],
         space_after=8)
    rect(s, 1.02, 4.2, 1.4, 0.05, fill=CORAL)
    text(s, 1.0, 4.45, 11.5, 1.7,
         [[R("PARTE 1 — ", 15, CORAL, True),
           R("Qué es OAG: de RAG a ontologías · OG-RAG (Microsoft Research) · Palantir Foundry", 13.5, MUTED, False)],
          [R("PARTE 2 — ", 15, BLUE, True),
           R("Nuestro grafo de tickets frente a OAG: qué compartimos y en qué diferimos", 13.5, MUTED, False)],
          [R("PARTE 3 — ", 15, GREEN, True),
           R("Qué adoptar: ontología mínima, extracción guiada, fact blocks, gates y cómo medirlo", 13.5, MUTED, False)],
          [R("PARTE 4 — ", 15, TEXT, True),
           R("La demo: de Naive RAG a OAG con Claude Code, dos preguntas, dónde gana cada técnica y si merece la pena", 13.5, MUTED, False)]],
         space_after=8)
    text(s, 1.0, 6.7, 11, 0.4,
         [[R("Fuentes: Sharma, Kumar & Li — OG-RAG (arXiv 2412.15235, EMNLP 2025) · docs de Palantir Foundry · "
             "L. Huang, \"From RAG to OAG\" (Medium) · reference/KNOWLEDGE_GRAPH.md", 11, FAINT, False)]])

    # ---- 2. La pregunta + respuesta corta
    s, pg = new()
    base(s, "La pregunta", "¿Es OAG lo que ya hacemos?", page=pg)
    panel_bullets(s, 0.7, 2.05, 5.85, 3.95, "Respuesta corta: primos, no gemelos",
                  ["Mismo objetivo: anclar al agente en conocimiento del dominio estructurado, con fuente citable",
                   "Mismo truco de coste: la inferencia cara se paga al construir; la consulta no llama al LLM",
                   "Diferencia clave: OAG define el esquema ANTES (schema-first); nuestro grafo lo deja EMERGER",
                   "Nuestro grafo se parece más a GraphRAG que a OG-RAG",
                   "Nuestras plantillas (ticket, sharp edges, follow-ups) ya son una ontología implícita"],
                  accent=CORAL)
    panel_bullets(s, 6.8, 2.05, 5.85, 3.95, "Lo que nos llevamos",
                  ["Una ontología mínima y explícita (≈8 clases, ≈10 relaciones)",
                   "Extracción guiada por esa ontología + validación en finalize",
                   "Backbone determinista desde el frontmatter de las plantillas",
                   "/kg facts: fact blocks mínimos con atribución",
                   "Invariantes como gate antes del merge",
                   "Un set de preguntas con respuesta conocida para medir recall"],
                  accent=GREEN)
    takeaway(s, "OAG no es un reemplazo: es el siguiente paso natural de nuestra Fase 2.")

    # =========================================================================
    # PARTE 1
    # =========================================================================
    s, pg = new()
    divider(s, 1, "Qué es OAG", "De recuperar trozos de texto a recuperar hechos tipados según una ontología.",
            ["De RAG a OAG", "Tres lecturas del término", "Qué es una ontología",
             "OG-RAG: el pipeline", "OG-RAG: resultados y límites"], page=pg)

    # ---- De RAG a OAG
    s, pg = new()
    diagram(s, "rag_evolution", page=pg)

    # ---- Tres lecturas
    s, pg = new()
    base(s, "Parte 1 · Tres lecturas", "Un nombre, tres cosas distintas", page=pg)
    panel_bullets(s, 0.7, 2.05, 3.85, 3.95, "Medium (L. Huang)",
                  ["Visión conceptual, sin método ni números",
                   "Ontología = capa normativa del conocimiento",
                   "Clases, relaciones y axiomas obligatorios (OWL, SHACL)",
                   "OAG como convergencia de las generaciones de RAG"],
                  accent=CORAL)
    panel_bullets(s, 4.75, 2.05, 3.85, 3.95, "OG-RAG (Microsoft Research)",
                  ["El paper serio: arXiv 2412.15235, EMNLP 2025",
                   "Docs → fact blocks JSON-LD mapeados a la ontología",
                   "Hipergrafo + recuperación greedy de hiperaristas",
                   "Evaluado contra RAG, RAPTOR y GraphRAG"],
                  accent=BLUE)
    panel_bullets(s, 8.8, 2.05, 3.85, 3.95, "Palantir Foundry",
                  ["Ontología = capa operativa del negocio",
                   "Objetos, enlaces y acciones tipados",
                   "OAG en la práctica: chunks como objetos + búsqueda semántica/híbrida (RRF)",
                   "El LLM consulta objetos y propone acciones"],
                  accent=GREEN)
    takeaway(s, "Lo común: un esquema del dominio que el LLM respeta al recuperar, razonar y actuar.")

    # ---- Qué es una ontología
    s, pg = new()
    base(s, "Parte 1 · Conceptos", "Qué es una ontología", page=pg)
    panel_bullets(s, 0.7, 2.0, 11.95, 1.2, "Definición",
                  ["La especificación explícita y compartida de un dominio: qué tipos de cosas existen, "
                   "cómo se relacionan y qué reglas deben cumplir. Escrita para que una máquina pueda usarla y validarla."],
                  accent=BLUE)
    cards(s, [
        ("C", "Clases", "Los tipos de cosas del dominio: Ticket, Invariante, Símbolo, Test."),
        ("R", "Relaciones", "Enlaces con nombre: Ticket fixes Símbolo, Invariante guards Símbolo."),
        ("A", "Atributos", "Propiedades de cada clase: estado, causa raíz, fichero fuente."),
        ("✓", "Restricciones", "«guards» solo sale de un Invariante; todo nodo tiene fichero fuente."),
    ], top=3.4, cols=2, height=1.25, gap=0.22, left=0.7, right=7.3)
    code(s, 7.55, 3.74, 5.1, 2.38,
         ["# esquema: qué PUEDE existir",
          "Ticket    --fixes-->       Symbol",
          "Invariant --guards-->      Symbol",
          "Ticket    --originates-->  Invariant",
          "# hechos: qué ES verdad hoy",
          "TKT-104  fixes  get_letter_end"],
         title="Esquema + instancias (nuestro dominio)")
    takeaway(s, "No es una taxonomía ni una lista de etiquetas: es un contrato sobre qué es un hecho válido en el dominio.")

    # ---- Ontología: diagrama esquema + hechos
    s, pg = new()
    diagram(s, "ontology", page=pg)

    # ---- OWL y SHACL
    s, pg = new()
    base(s, "Parte 1 · Conceptos", "OWL y SHACL: los dos estándares del W3C", page=pg)
    panel_bullets(s, 0.7, 2.0, 3.85, 4.0, "OWL · Web Ontology Language",
                  ["Sirve para escribir la ontología: clases, propiedades, jerarquías y axiomas",
                   "Ejemplo: «todo invariante tiene un ticket de origen»",
                   "Un razonador deduce hechos nuevos a partir de los declarados",
                   "Mundo abierto: lo que falta no es falso, es desconocido"], accent=BLUE)
    panel_bullets(s, 4.75, 2.0, 3.85, 4.0, "SHACL · Shapes Constraint Language",
                  ["Sirve para validar los datos del grafo contra unas «formas»",
                   "Tipos de nodo, relaciones permitidas, campos obligatorios, cardinalidades",
                   "Mundo cerrado: si falta un dato obligatorio, es un error",
                   "Devuelve un informe con lo que no cumple"], accent=AMBER)
    panel_bullets(s, 8.8, 2.0, 3.85, 4.0, "En nuestra demo",
                  ["No usamos los estándares, sino su idea con herramientas ligeras",
                   "El YAML de la ontología hace el papel de OWL",
                   "La validación de oag.py build hace el de SHACL: rechaza lo que no cumple el esquema",
                   "Si el dominio crece, el YAML se traduce a OWL y SHACL"], accent=GREEN)
    takeaway(s, "OWL dice qué puede existir y qué se deduce; SHACL comprueba que los datos lo cumplen.")

    # ---- OG-RAG pipeline
    s, pg = new()
    diagram(s, "ograg_pipeline", page=pg)

    # ---- Resultados
    s, pg = new()
    base(s, "Parte 1 · OG-RAG: resultados", "Lo que dicen los números (y lo que no)", page=pg)
    table(s, 0.7, 2.0, [2.0, 1.35, 1.35, 1.35, 1.35],
          [["Context recall", "RAG", "RAPTOR", "GraphRAG", "OG-RAG"],
           ["Soja", "0.22", "0.54", "0.41", "0.84"],
           ["Trigo", "0.14", "0.85", "0.78", "0.95"],
           ["Noticias", "0.01", "0.82", "—", "0.82"]], row_h=0.5, size=11.5)
    text(s, 0.7, 4.35, 7.3, 0.6,
         [[R("Tabla 1 del paper. «—» = no terminó en un día. Modelos: GPT-4o(-mini), Llama-3.1 8B/70B, temperatura 0.",
             10, FAINT, False)]])
    panel_bullets(s, 8.3, 2.0, 4.35, 2.2, "Titulares del abstract",
                  ["+55% recall de hechos correctos", "+40% corrección de respuesta",
                   "Atribución 30% más rápida", "+27% en razonamiento sobre hechos"], accent=GREEN)
    panel_bullets(s, 0.7, 4.85, 11.95, 1.35, "Letra pequeña",
                  ["Datos propietarios, dos dominios · ontologías hechas a mano · relevancia de respuesta no siempre mejor (RAPTOR gana en trigo y noticias)"],
                  accent=CORAL)
    takeaway(s, "La ganancia está en el recall de hechos; el precio, construir y mantener la ontología.")

    # =========================================================================
    # PARTE 2
    # =========================================================================
    s, pg = new()
    divider(s, 2, "Nuestro grafo vs OAG", "El grafo de tickets construido con graphify, puesto al lado de OG-RAG y Palantir.",
            ["Recordatorio: cómo funciona", "Nuestra pipeline y lo aprendido", "Comparación lado a lado",
             "La ontología que ya tenemos sin saberlo", "Veredicto"], page=pg)

    # ---- Recordatorio
    s, pg = new()
    base(s, "Parte 2 · Recordatorio", "El grafo de tickets en una slide", page=pg)
    code(s, 0.7, 2.15, 6.3, 1.6,
         ["kg_refresh.sh prepare   # manifest → _corpus → scratch",
          "/graphify <scratch>     # subagentes extraen el grafo",
          "kg_refresh.sh finalize  # output/ + leak-check",
          "/kg <ticket-o-tema>     # explain/path/find, sin LLM"],
         title="Pipeline y consulta")
    table(s, 0.7, 4.15, [2.4, 3.9],
          [["Corpus → grafo", "Valor"],
           ["Ficheros / palabras", "453 / ~690k"],
           ["Nodos · aristas · comunidades", "3.977 · 8.076 · 213"],
           ["Aristas EXTRACTED / INFERRED", "93% / 7%"]], row_h=0.38, size=10.5)
    panel_bullets(s, 7.25, 1.82, 5.4, 4.35, "Tipos que salieron (emergentes)",
                  ["Nodos: concept 2.102 · rationale 674 · símbolo 543 · ticket 441",
                   "references 4.749 · rationale_for 821",
                   "implements 594 · calls 398",
                   "conceptually_related_to 312 · relates_to 267 · semantically_similar_to 120",
                   "~67% de las aristas son genéricas (references, relates_to y similares)",
                   "Grafo de /kg-refresh del 20-11-2026, el mismo que usa la demo"],
                  accent=BLUE)

    # ---- Nuestra pipeline
    s, pg = new()
    diagram(s, "kg_pipeline", page=pg)

    # ---- Comparación
    s, pg = new()
    base(s, "Parte 2 · Comparación", "Lado a lado", page=pg)
    table(s, 0.7, 1.95, [2.1, 3.3, 3.25, 3.3],
          [["Dimensión", "OG-RAG", "Palantir OAG", "Nuestro grafo de tickets"],
           ["Esquema", "Ontología definida antes (expertos)", "Ontología de negocio curada", "Emergente: lo decide el LLM al extraer"],
           ["Extracción", "LLM mapea docs → JSON-LD", "Pipelines + chunks como objetos", "Subagentes graphify sobre markdown"],
           ["Representación", "Hipergrafo de fact blocks", "Objetos, enlaces, acciones", "Grafo NetworkX, aristas con confianza"],
           ["Recuperación", "Set-cover greedy de hiperaristas", "Semántica / keyword / híbrida", "explain · path · find, deterministas"],
           ["Coste por consulta", "0 LLM extra", "Embeddings + LLM", "0 LLM: lee graph.json"],
           ["Salida", "Hechos dentro del prompt", "Chunks + citas en Workshop", "Lista de lectura: tickets + zona de peligro"],
           ["Acciones", "No", "Sí, tipadas", "Skills (/kg, /kg-refresh) y gates del método"]],
          row_h=0.5, size=10)

    # ---- Ontología implícita
    s, pg = new()
    base(s, "Parte 2 · Lo que ya tenemos", "Una ontología implícita en las plantillas", page=pg)
    cards(s, [
        ("T", "Ticket", "ISSUE_NOTE / <TICKET>.md: síntoma, causa raíz, fix, tests, estado."),
        ("!", "Invariante / sharp edge", "SHARP_EDGES.md: «no tocar», con ticket de origen."),
        ("→", "Follow-up", "FOLLOWUPS.md: deuda abierta enlazada a su ticket."),
        ("◆", "Componente / símbolo", "Extractores y funciones (get_letter_end…); CodeGraph los conoce."),
        ("✓", "Test / criterio QA", "TEST_MAP y QA_ACCEPTANCE: qué prueba qué."),
        ("✎", "Lección / decisión", "PLAYBOOK, memoria y handovers."),
    ], top=2.05, cols=3, height=1.2, gap=0.25)
    panel_bullets(s, 0.7, 5.0, 11.95, 1.15, "El hueco",
                  ["Las clases existen en las plantillas, pero graphify no las conoce: cada refresh las reinventa (por eso solo <1% de las etiquetas de comunidad sobrevive)."],
                  accent=CORAL)
    takeaway(s, "No hay que inventar la ontología: hay que escribir la que las plantillas ya usan.")

    # ---- Veredicto
    s, pg = new()
    base(s, "Parte 2 · Veredicto", "¿Cuánto se parece?", page=pg)
    panel_bullets(s, 0.7, 2.05, 5.85, 3.95, "Igual (≈ la mitad del camino)",
                  ["Conocimiento del dominio como grafo, no como chunks",
                   "Construcción cara una vez; consulta barata y reproducible",
                   "Atribución: cada nodo apunta a su fichero fuente",
                   "Diseñado para que el agente lo use ANTES de actuar (history-first)",
                   "Honestidad sobre la confianza (EXTRACTED vs INFERRED)"],
                  accent=GREEN)
    panel_bullets(s, 6.8, 2.05, 5.85, 3.95, "Distinto (lo que falta para ser OAG)",
                  ["Sin esquema previo: tipos de nodo y arista genéricos",
                   "Sin restricciones ni validación del grafo",
                   "Sin hechos tipados (fixes / regresses / guards / supersedes)",
                   "Devuelve qué leer, no los hechos mismos",
                   "Sin acciones ligadas a la ontología"],
                  accent=CORAL)
    takeaway(s, "Somos GraphRAG con disciplina de ingeniería; OAG añade el contrato del esquema.")

    # =========================================================================
    # PARTE 3
    # =========================================================================
    s, pg = new()
    divider(s, 3, "Qué adoptar", "Lo útil de OAG, al tamaño de un equipo pequeño y sin plataforma nueva.",
            ["Una ontología mínima", "Seis adopciones concretas",
             "Hoja de ruta y qué NO hacer", "Cómo medir si mejora"], page=pg)

    # ---- Ontología mínima
    s, pg = new()
    base(s, "Parte 3 · Ontología mínima", "Ocho clases, diez relaciones, un fichero", page=pg)
    code(s, 0.7, 2.15, 6.6, 3.95,
         ["# data/knowledge-graph/ontology.yaml",
          "classes: [Ticket, Invariant, Followup, Component,",
          "          Symbol, Test, Lesson, Decision]",
          "relations:",
          "  fixes:        Ticket -> Ticket|Symbol",
          "  regresses:    Ticket -> Ticket",
          "  supersedes:   Ticket|Decision -> Ticket|Decision",
          "  guards:       Invariant -> Symbol|Component",
          "  originates:   Ticket -> Invariant|Lesson",
          "  touches:      Ticket -> Symbol|Component",
          "  verified_by:  Ticket|Invariant -> Test",
          "  blocks / depends_on / follows_up"],
         title="Esbozo (el detalle se decide con el corpus real)")
    panel_bullets(s, 7.55, 1.82, 5.1, 4.28, "Reglas de diseño",
                  ["Sale de las plantillas que ya usamos, no de un libro de OWL",
                   "Pequeña: si una relación no responde una pregunta real, fuera",
                   "Versionada junto a los scripts del KG (va en data/, igual que el grafo)",
                   "Relaciones genéricas permitidas, pero marcadas como «pista»",
                   "Cliente → rol en la versión que se comparte fuera"],
                  accent=BLUE)

    # ---- Seis adopciones
    s, pg = new()
    base(s, "Parte 3 · Adopciones", "Seis cosas que tomar de OAG", page=pg)
    cards(s, [
        ("1", "Extracción guiada", "Pasar ontology.yaml a los subagentes de graphify: solo clases y relaciones del esquema."),
        ("2", "Validación en finalize", "Comprobación tipo SHACL: rechaza aristas fuera del esquema y nodos sin fuente."),
        ("3", "Backbone determinista", "Frontmatter YAML en las plantillas + las citas SST-NNNN → hechos sin LLM."),
        ("4", "/kg facts <tema>", "Fact blocks mínimos que cubren la consulta (set-cover de OG-RAG), con atribución."),
        ("5", "Invariantes como gate", "Antes del merge: invariantes que guardan los símbolos tocados (join con CodeGraph)."),
        ("6", "IDs estables", "Nodos con id de clase + ticket: las etiquetas de comunidad sobreviven al refresh."),
    ], top=2.0, cols=2, height=1.05, gap=0.22)
    takeaway(s, "Cada adopción es pequeña, reversible y medible: encaja con los gates del método.")

    # ---- Roadmap + no hacer
    s, pg = new()
    base(s, "Parte 3 · Hoja de ruta", "De menos a más, y qué no hacer", page=pg)
    steps(s, [
        ("Fase A · esquema", "Escribir ontology.yaml desde las plantillas. Frontmatter en ticket y sharp edges nuevos."),
        ("Fase B · backbone", "Parser determinista de frontmatter + citas. Validación en finalize."),
        ("Fase C · extracción", "graphify guiado por el esquema; INFERRED solo para lo que el parser no ve."),
        ("Fase D · consumo", "/kg facts y el gate de invariantes en el flujo de 11 etapas."),
    ], y=2.05, h=2.1, accent=GREEN)
    panel_bullets(s, 0.7, 4.4, 11.95, 1.75, "Qué NO adoptar",
                  ["Una plataforma (Foundry) ni un triplestore OWL: nuestro tamaño no lo justifica",
                   "Meter hechos en el prompt en lugar de leer la fuente: el grafo apunta, el writeup manda",
                   "Una ontología grande «por completitud»: el coste de mantenerla es el riesgo nº1 de OAG"],
                  accent=CORAL)

    # ---- Medir
    s, pg = new()
    base(s, "Parte 3 · Medir", "Validar el instrumento antes de creerle", page=pg)
    panel_bullets(s, 0.7, 2.05, 5.85, 3.95, "Set de preguntas con respuesta conocida",
                  ["15–20 preguntas reales: «¿qué tickets tocan get_letter_end?», «¿qué invariante protege X?»",
                   "Respuesta esperada = lista de tickets / invariantes, escrita a mano",
                   "Métrica: recall de contexto, como C-Rec en OG-RAG",
                   "Medir el grafo actual primero: es la línea base"],
                  accent=BLUE)
    panel_bullets(s, 6.8, 2.05, 5.85, 3.95, "Criterio de keep / revert",
                  ["Mejora de recall en zonas densas (fin de carta, títulos, numeración)",
                   "No empeora en áreas aisladas",
                   "Coste de refresh igual o menor",
                   "Composición, no total: revisar QUÉ tickets faltan, no solo cuántos",
                   "Decir qué no puede mostrar el set (sesgo de quien lo escribe)"],
                  accent=GREEN)
    takeaway(s, "Mismo principio que el método: un gate verde que no puede fallar no prueba nada.")

    # =========================================================================
    # PARTE 4
    # =========================================================================
    s, pg = new()
    divider(s, 4, "La demo", "Seis skills de Claude Code, dos preguntas reales y la misma vara de medir.",
            ["OAG en la demo", "Cómo evaluamos", "Dos preguntas, dos ganadores", "Combinar las dos",
             "De OAG v1 a v2",
             "La pregunta en castellano", "Dónde gana cada técnica", "¿Merece la pena en nuestro caso?"], page=pg)

    # ---- Cómo ejecutarla
    s, pg = new()
    base(s, "Parte 4 · Cómo ejecutarla", "La demo en Claude Code, paso a paso", page=pg)
    code(s, 0.7, 2.3, 5.55, 3.55,
         ["# una vez, en la terminal (WSL)",
          "git pull",
          "uv sync --group embed",
          "source .venv/bin/activate",
          "python demo/oag.py build --q letter-end-runin",
          "python demo/oag.py build --q comment-memo-landscape",
          "python demo/compare.py",
          "claude"], title="1 · Preparación")
    code(s, 6.5, 2.3, 6.15, 3.55,
         ["# pregunta A: reglas (gana OAG)",
          "/demo-naive-rag    /demo-agentic-rag",
          "/demo-graphrag     /demo-oag",
          "# pregunta B: exploración (gana GraphRAG)",
          "/demo-graphrag comment-memo-landscape",
          "/demo-oag comment-memo-landscape",
          "# en castellano llano (opcional)",
          "/demo-oag letter-end-runin --lang es",
          "# híbrido y cierre",
          "/demo-hybrid       /demo-compare"], title="2 · Dentro de Claude Code")
    takeaway(s, "/clear antes de cada skill y aprobar una vez «python demo/...»: cada técnica responde solo con lo suyo.")

    s, pg = new()
    diagram(s, "demo_oag_pipeline", page=pg)

    s, pg = new()
    diagram(s, "evaluation", page=pg)

    s, pg = new()
    diagram(s, "scenarios", page=pg)

    # ---- Resultados A
    s, pg = new()
    base(s, "Parte 4 · Pregunta A", "Reglas sobre un componente modelado", page=pg)
    table(s, 0.7, 1.95, [3.0, 1.3, 1.4, 1.0, 1.1, 1.85, 2.3],
          [["Técnica", "Recall", "Precisión", "F1", "IDs", "Tokens", "Con 14 ficheros (R / P)"],
           ["Naive RAG", "71%", "62%", "0,67", "8", "~1.600", "100% / 39%"],
           ["GraphRAG (/kg, 1 salto)", "71%", "50%", "0,59", "10", "~770", "43% / 43%"],
           ["GraphRAG (/kg, 2 saltos)", "100%", "13%", "0,23", "53", "~7.000", "86% / 23%"],
           ["OAG, esquema v1", "86%", "35%", "0,50", "17", "~2.000", "86% / 60%"],
           ["OAG, esquema v2", "100%", "47%", "0,64", "15", "~2.500", "-"],
           ["Agentic RAG", "en directo", "en directo", "-", "variable", "variable", "-"]], row_h=0.44, size=11.5)
    text(s, 0.7, 5.75, 11.9, 0.5,
         [[R("7 tickets esperados, escritos por quien resolvió el bug. Corpus completo: 452 ficheros. "
             "Por F1 Naive RAG queda a la par, pero se deja dos de los siete: en «qué no romper», un olvido es una regresión.",
             11, FAINT, False)]])
    takeaway(s, "OAG v2 encuentra todo en 15 tickets, no en 53, y dice por qué importa cada uno.")

    # ---- Resultados B
    s, pg = new()
    base(s, "Parte 4 · Pregunta B", "Explorar un área que la ontología no modela", page=pg)
    table(s, 0.7, 1.95, [3.0, 1.4, 1.5, 1.1, 1.2, 2.0],
          [["Técnica", "Recall", "Precisión", "F1", "IDs", "Tokens"],
           ["Naive RAG", "10%", "100%", "0,19", "3", "~1.600"],
           ["GraphRAG (/kg, 1 salto)", "21%", "67%", "0,32", "9", "~1.100"],
           ["GraphRAG (/kg, 2 saltos)", "83%", "43%", "0,56", "56", "~7.000"],
           ["OAG, esquema v1 y v2", "0%", "-", "0", "0", "0"],
           ["Agentic RAG", "en directo", "en directo", "-", "variable", "variable"]], row_h=0.44, size=11.5)
    text(s, 0.7, 5.25, 11.9, 0.9,
         [[R("29 esperados por una regla objetiva: los writeups cuyo título menciona el área. "
             "GraphRAG agrupa el resultado en temas con las comunidades del grafo; "
             "OAG no encuentra ningún componente de su ontología en la pregunta y no devuelve nada.",
             11, FAINT, False)]])
    takeaway(s, "GraphRAG descubre lo que nadie ha modelado; OAG solo ve lo que su esquema declara.")

    # ---- Híbrido
    s, pg = new()
    base(s, "Parte 4 · Combinar las dos", "Híbrido: GraphRAG propone, la ontología filtra", page=pg)
    table(s, 0.7, 2.0, [3.3, 1.6, 1.6],
          [["Técnica", "Pregunta A", "Pregunta B"],
           ["GraphRAG (/kg, 2 saltos)", "100% / 13%", "83% / 43%"],
           ["OAG, esquema v2", "100% / 47%", "0%"],
           ["Híbrido", "100% / 47%", "83% / 43%"]], row_h=0.5, size=11.5)
    text(s, 0.7, 4.2, 6.5, 1.2,
         [[R("Recall / precisión. Pregunta A: 53 candidatos del grafo; 22 se conectan al componente en la "
             "ontología; 15 cumplen sus reglas. El grafo no aportó ningún ticket que OAG no tuviera.",
             10.5, FAINT, False)]])
    panel_bullets(s, 7.55, 2.0, 5.1, 3.4, "Cómo funciona (demo/hybrid.py)",
                  ["GraphRAG a 2 saltos da la lista amplia: mucho recall, poca precisión",
                   "Si la pregunta nombra un componente de la ontología, se filtra con sus clases, relaciones y reglas",
                   "Si no nombra ninguno, se queda la lista del grafo sin tocar",
                   "Las comunidades que el grafo encuentra fuera del esquema salen como propuesta para ampliar la ontología; la revisa una persona"],
                  accent=GREEN)
    takeaway(s, "No supera a la mejor en cada pregunta: evita elegir mal y dice qué modelar después.")

    # ---- v1 -> v2
    s, pg = new()
    base(s, "Parte 4 · De OAG v1 a v2", "El esquema también se depura", page=pg)
    panel_bullets(s, 0.7, 2.0, 5.85, 2.6, "1 · Ruido: una relación sin restricción",
                  ["must_not_break traía tickets de otras áreas (numeración, PDF)",
                   "v2 añade una restricción al estilo SHACL: el ticket protegido debe compartir componente",
                   "De 17 a 11 tickets sin perder ninguno esperado"], accent=AMBER)
    panel_bullets(s, 6.8, 2.0, 5.85, 2.6, "2 · Una dependencia sin declarar",
                  ["El fin de carta usa get_titles para mirar el título siguiente",
                   "v1 trataba los componentes como islas",
                   "v2 añade la relación calls y recupera el invariante que faltaba: recall del 86 % al 100 %"],
                  accent=GREEN)
    takeaway(s, "v2 se escribió después de ver el fallo: es evolución del esquema y hay que validarla con preguntas nuevas.")

    # ---- Pregunta en castellano llano
    s, pg = new()
    base(s, "Parte 4 · La pregunta en castellano", "Corpus en inglés, pregunta sin nombres de código", page=pg)
    table(s, 0.7, 1.95, [4.4, 2.2, 2.2, 3.1],
          [["Técnica", "Pregunta A (R / P)", "Pregunta B (R / P)", "Qué compara con la pregunta"],
           ["Naive RAG, TF-IDF", "14% / 25%", "0% / 0%", "Palabras"],
           ["Naive RAG, embeddings", "43% / 38%", "10% / 50%", "Significado"],
           ["GraphRAG, semilla por nombre", "0%", "0%", "Nombre del nodo"],
           ["GraphRAG, semilla por similitud", "43% / 75%", "59% / 25%", "Significado de la etiqueta"],
           ["OAG v2, etiquetas en inglés", "0%", "0%", "Sinónimos en inglés"],
           ["OAG v3, sinónimos en castellano", "100% / 47%", "0%", "Sinónimos en castellano"],
           ["OAG v2, componentes por similitud", "100% / 47%", "0%", "Significado del componente"]],
          row_h=0.4, size=10.5)
    text(s, 0.7, 5.72, 11.9, 0.5,
         [[R("Sin capa semántica caen las tres, en silencio. GraphRAG llega a la zona correcta, no al nodo central. "
             "Modelo multilingüe pequeño en CPU; el umbral de OAG está calibrado con estas dos preguntas.",
             10.5, FAINT, False)]])
    takeaway(s, "El idioma solo afecta al primer paso: con seis sinónimos o un modelo pequeño, OAG responde igual que en inglés.")

    s, pg = new()
    diagram(s, "when_to_use", page=pg)

    # ---- Dónde gana cada una
    s, pg = new()
    base(s, "Parte 4 · Dónde gana cada técnica", "Depende de la pregunta, no de la moda", page=pg)
    table(s, 0.7, 1.95, [4.6, 2.3, 5.0],
          [["Si la pregunta es...", "Usa", "Porque"],
           ["«Qué reglas, tickets o tests protegen este componente»", "OAG", "Hechos tipados con su porqué; poco ruido; validable antes del LLM"],
           ["«Qué hay sobre esta área y cómo se organiza»", "GraphRAG (/kg)", "Descubre estructura sin esquema previo y agrupa en temas"],
           ["«Dónde se menciona este identificador»", "Naive RAG o búsqueda", "Barato e inmediato; no necesita estructura"],
           ["«Investiga este problema nuevo»", "Agentic RAG", "Planifica y vuelve a buscar; caro y variable"],
           ["Cualquiera, en castellano y sin nombres de código", "La misma + capa semántica",
            "Sinónimos en la ontología o embeddings multilingües"]],
          row_h=0.56, size=11.5)
    takeaway(s, "OAG no sustituye a GraphRAG: lo completa. Uno descubre la estructura; el otro la fija como contrato.")

    # ---- Merece la pena
    s, pg = new()
    base(s, "Parte 4 · ¿Merece la pena?", "Sí, por partes y solo para las preguntas de reglas", page=pg)
    panel_bullets(s, 0.7, 2.0, 3.85, 3.3, "Lo que ha costado",
                  ["Ontología de ~70 líneas: 4 clases, 6 relaciones, 1 restricción, 4 componentes",
                   "Sale en buena parte de las plantillas (ISSUE_NOTE, SHARP_EDGES, TEST_MAP)",
                   "Extracción determinista: 0 llamadas LLM",
                   "Preguntas en castellano: sinónimos o un modelo pequeño en CPU"], accent=GREEN)
    panel_bullets(s, 4.75, 2.0, 3.85, 3.3, "Lo que no compensa",
                  ["Modelar todo el dominio «por completitud»",
                   "Sustituir /kg: explorar lo sigue haciendo mejor el grafo",
                   "Atribuir el resultado sin un set de 15-20 preguntas"], accent=AMBER)
    panel_bullets(s, 8.8, 2.0, 3.85, 3.3, "Qué llevar a la metodología",
                  ["Paso 0: set de preguntas de reglas y de exploración",
                   "Ontología mínima con dependencias (calls)",
                   "Validar en /kg-refresh contra el esquema",
                   "/kg facts <componente> junto a /kg <tema>"], accent=CORAL)
    takeaway(s, "Poco esfuerzo, bien acotado: ontología pequeña, extracción sin LLM y dos modos en /kg.")

    # ---- Cierre
    s, pg = new()
    base(s, "Cierre", "En una frase", page=pg)
    text(s, 0.7, 2.2, 11.9, 1.4,
         [[R("Nuestro grafo ya hace la mitad de OAG. ", 26, TEXT, True),
           R("Escribir la ontología que nuestras plantillas usan, y validar el grafo contra ella, es la otra mitad.",
             26, MUTED, False)]], line_spacing=1.1)
    rect(s, 0.72, 3.95, 1.1, 0.045, fill=CORAL)
    text(s, 0.7, 4.3, 11.9, 1.9,
         [[R("Referencias", 13, CORAL, True)],
          [R("K. Sharma, P. Kumar, Y. Li — OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for LLMs. arXiv 2412.15235 (2024), EMNLP 2025.", 11, MUTED, False)],
          [R("Palantir Foundry docs — Ontology augmented generation (palantir.com/docs/foundry/ontology/ontology-augmented-generation).", 11, MUTED, False)],
          [R("L. Huang — From RAG to OAG (medium.com/@linghuang_76674).", 11, MUTED, False)],
          [R("Lewis et al. 2020 (arXiv 2005.11401) · Gao et al. 2023 (arXiv 2312.10997) · Edge et al. 2024, GraphRAG (arXiv 2404.16130) · Singh et al. 2025, Agentic RAG (arXiv 2501.09136)", 11, MUTED, False)],
          [R("Repo: docs/GUIA_DEMO.md · docs/OAG_VS_KG.md · reference/KNOWLEDGE_GRAPH.md · demo/README.md", 11, MUTED, False)]],
         space_after=6)

    name = "OAG_vs_KG_Presentacion.pptx" if LANG == "es" else "OAG_vs_KG_Presentation_EN.pptx"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    prs.save(out)
    print(f"OK  ->  {out}  ({len(prs.slides._sldIdLst)} slides)")
    if _MISSES:
        print(f"WARNING: {len(_MISSES)} lines without translation:")
        for m in _MISSES:
            print("   ", m[:100])
    return out


if __name__ == "__main__":
    import argparse

    _ap = argparse.ArgumentParser()
    _ap.add_argument("--lang", choices=["es", "en"], default="es")
    LANG = _ap.parse_args().lang
    build()
