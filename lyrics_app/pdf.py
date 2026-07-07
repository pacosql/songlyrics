"""Generación del PDF listo para imprimir.

Restricción: la letra debe caber en UN solo folio A4, usando como máximo
las dos caras (2 páginas). El tamaño de fuente se reduce automáticamente
hasta que el contenido quepa; si ni con el tamaño mínimo cabe, se genera
igualmente al mínimo y se avisa al usuario.
"""

from __future__ import annotations

import os
from datetime import date

from fpdf import FPDF
from fpdf.enums import XPos, YPos

_NEXT_LINE = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}

MAX_PAGES = 2  # un folio, dos caras

# (tamaño de letra, alto de línea, tamaño título, tamaño artista, columnas)
# Primero se intenta a una columna; si no cabe, dos columnas antes de
# reducir la letra a tamaños poco legibles.
_SIZE_STEPS = (
    (12, 6.5, 22, 14, 1),
    (11, 6.0, 20, 13, 1),
    (10, 5.5, 18, 12, 1),
    (10, 5.5, 18, 12, 2),
    (9, 5.0, 16, 11, 2),
    (8, 4.5, 15, 10, 2),
    (7, 4.0, 14, 10, 2),
)

# Fuente Unicode del sistema si existe (acentos, ñ, comillas tipográficas…)
_DEJAVU_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/DejaVuSans.ttf",
)
_DEJAVU_BOLD_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/DejaVuSans-Bold.ttf",
)


def _find(paths: tuple[str, ...]) -> str | None:
    for p in paths:
        if os.path.exists(p):
            return p
    return None


class _LyricsPDF(FPDF):
    footer_text = ""

    def footer(self):
        self.set_y(-13)
        self.set_font(self.font_family, "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, self.footer_text, align="L")
        self.cell(0, 5, f"Página {self.page_no()}/{{nb}}", align="R")


def _render(
    family: str,
    fonts: tuple[str | None, str | None],
    title: str,
    artist: str,
    lyrics: str,
    footer_text: str,
    body_size: float,
    line_h: float,
    title_size: float,
    artist_size: float,
    ncols: int,
) -> _LyricsPDF:
    pdf = _LyricsPDF(format="A4")
    pdf.set_margins(18, 14, 18)
    # Los saltos de página/columna se gestionan a mano para poder fluir
    # el texto en columnas.
    pdf.set_auto_page_break(False)
    regular, bold = fonts
    if family != "Helvetica" and regular and bold:
        pdf.add_font(family, "", regular)
        pdf.add_font(family, "B", bold)
    pdf.footer_text = footer_text
    pdf.add_page()

    # Cabecera (solo en la primera cara)
    pdf.set_font(family, "B", title_size)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, title_size * 0.45, title, align="C", **_NEXT_LINE)
    pdf.set_font(family, "", artist_size)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, artist_size * 0.5, artist, align="C", **_NEXT_LINE)
    pdf.ln(1)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)

    # Letra, fluyendo por columnas y páginas
    pdf.set_font(family, "", body_size)
    pdf.set_text_color(0, 0, 0)
    gutter = 8.0
    epw = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = (epw - gutter * (ncols - 1)) / ncols
    bottom = pdf.h - 18  # deja sitio al pie de página
    blank = line_h * 0.55

    state = {"col": 0, "top": pdf.get_y(), "at_top": True}

    def col_x() -> float:
        return pdf.l_margin + state["col"] * (col_w + gutter)

    def advance_col():
        state["col"] += 1
        if state["col"] >= ncols:
            pdf.add_page()
            state["col"] = 0
            state["top"] = pdf.t_margin
        pdf.set_y(state["top"])
        state["at_top"] = True

    for line in lyrics.splitlines():
        line = line.rstrip()
        if not line:
            # separación entre estrofas, nunca al principio de una columna
            if not state["at_top"] and pdf.get_y() + blank <= bottom:
                pdf.ln(blank)
            continue
        h = pdf.multi_cell(col_w, line_h, line, align="C",
                           dry_run=True, output="HEIGHT")
        if pdf.get_y() + h > bottom:
            advance_col()
        pdf.set_x(col_x())
        pdf.multi_cell(col_w, line_h, line, align="C", **_NEXT_LINE)
        state["at_top"] = False
    return pdf


def build_pdf(
    title: str,
    artist: str,
    lyrics: str,
    verdict: dict,
    output_path: str,
) -> dict:
    """Genera el PDF. Devuelve {"path", "pages", "fits", "font_size"}."""
    regular = _find(_DEJAVU_CANDIDATES)
    bold = _find(_DEJAVU_BOLD_CANDIDATES)
    if regular and bold:
        family, fonts = "Deja", (regular, bold)
    else:
        family, fonts = "Helvetica", (None, None)
        # Los core fonts solo cubren latin-1: sustituir lo que no exista.
        lyrics = lyrics.encode("latin-1", "replace").decode("latin-1")
        title = title.encode("latin-1", "replace").decode("latin-1")
        artist = artist.encode("latin-1", "replace").decode("latin-1")

    if verdict.get("validated"):
        n = len(verdict.get("agreeing_sources", []))
        status = f"Letra validada: {n} fuentes coinciden"
    else:
        status = "Letra de una sola fuente (sin validación cruzada)"
    src = ", ".join(verdict.get("agreeing_sources", []))
    footer_text = f"{status} ({src}) — {date.today():%d/%m/%Y}"

    pdf = None
    used = _SIZE_STEPS[-1]
    for step in _SIZE_STEPS:
        pdf = _render(family, fonts, title, artist, lyrics, footer_text, *step)
        if pdf.page_no() <= MAX_PAGES:
            used = step
            break
    else:
        used = _SIZE_STEPS[-1]  # ni al mínimo cabe: se entrega igual y se avisa

    pages = pdf.page_no()
    pdf.output(output_path)
    return {
        "path": output_path,
        "pages": pages,
        "fits": pages <= MAX_PAGES,
        "font_size": used[0],
    }
