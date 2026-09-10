"""Generates the conference Abstract Book — a paginated PDF listing accepted
abstracts, grouped by topic/track, with Background/Methods/Results/Conclusion
sections bolded and indented for readability.
"""
import os
import io
import re
from datetime import datetime
from xml.sax.saxutils import escape as _xml_escape

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable,
    PageBreak, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
LOGO_LEFT_PATH = os.path.join(ASSETS_DIR, "logo_left.png")
LOGO_RIGHT_PATH = os.path.join(ASSETS_DIR, "logo.png")

_PINK = colors.Color(254 / 255.0, 80 / 255.0, 103 / 255.0)
_RED = colors.Color(220 / 255.0, 50 / 255.0, 75 / 255.0)
_GREY = colors.Color(0.45, 0.45, 0.45)
_DARK = colors.Color(0.13, 0.15, 0.18)

# Recognised abstract structure labels — matched case-insensitively wherever
# they appear followed by a colon, not just at the start of a line, since
# submitters paste text with inconsistent line breaks.
_SECTION_LABELS = [
    "Background", "Introduction", "Aim", "Aims", "Objective", "Objectives",
    "Purpose", "Methodology", "Methods", "Method", "Results", "Findings",
    "Result", "Discussion", "Conclusion", "Conclusions", "Recommendation",
    "Recommendations", "Implications",
]
_LABEL_RE = re.compile(r"(?i)\b(" + "|".join(_SECTION_LABELS) + r")\s*:\s*")

# The standard placeholder instructions left behind by submitters who forgot
# to delete the template text before submitting — stripped as noise.
_BOILERPLATE_RE = re.compile(
    r"please read and follow the guide below.*?format provided\.\s*"
    r"(note:\s*no tables,\s*figures,\s*or references should be included in the abstract\.\s*)?",
    re.IGNORECASE | re.DOTALL,
)


def _esc(text: str) -> str:
    return _xml_escape((text or "").strip())


def parse_abstract_sections(raw_text: str):
    """Split an abstract's free-text body into (label, body) pairs — label is
    '' for any leading text found before the first recognised heading."""
    text = _BOILERPLATE_RE.sub("", raw_text or "").strip()
    if not text:
        return []
    matches = list(_LABEL_RE.finditer(text))
    if not matches:
        return [("", text)]
    sections = []
    if matches[0].start() > 0:
        lead = text[: matches[0].start()].strip()
        if lead:
            sections.append(("", lead))
    for i, m in enumerate(matches):
        label = m.group(1).strip().title()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = re.sub(r"\s+", " ", text[start:end]).strip()
        if body:
            sections.append((label, body))
    return sections


def _footer(canvas, doc, event_name):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_GREY)
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm, f"{event_name} — Abstract Book   |   Page {doc.page}")
    canvas.restoreState()


def generate_abstract_book_pdf(event_name: str, abstracts: list) -> bytes:
    """`abstracts` is a list of dicts:
    {id, title, track, keywords, presentation_type, abstract_text,
     authors: [{name, affiliation, is_presenting}]}
    already filtered/ordered by the caller (accepted + paid presenter).
    """
    buffer = io.BytesIO()
    W = A4[0] - 4 * cm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )

    title_s = ParagraphStyle("title", fontSize=26, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=_DARK, leading=32, spaceAfter=16)
    subtitle_s = ParagraphStyle("subtitle", fontSize=13, fontName="Helvetica", alignment=TA_CENTER, textColor=_GREY, spaceAfter=4)
    generated_s = ParagraphStyle("generated", fontSize=9, fontName="Helvetica-Oblique", alignment=TA_CENTER, textColor=_GREY)
    track_s = ParagraphStyle("track", fontSize=15, fontName="Helvetica-Bold", textColor=_RED, spaceBefore=6, spaceAfter=10)
    abs_no_s = ParagraphStyle("absno", fontSize=9, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)
    abs_title_s = ParagraphStyle("abstitle", fontSize=12, fontName="Helvetica-Bold", textColor=_DARK, leading=15, spaceAfter=3)
    authors_s = ParagraphStyle("authors", fontSize=9.5, fontName="Helvetica-Oblique", textColor=colors.Color(0.3, 0.3, 0.3), leading=13, spaceAfter=6)
    section_s = ParagraphStyle("section", fontSize=10, fontName="Helvetica", leading=14, leftIndent=10, spaceAfter=6, alignment=TA_LEFT)
    keywords_s = ParagraphStyle("keywords", fontSize=8.5, fontName="Helvetica-Oblique", textColor=_GREY, leading=12, spaceBefore=2)
    badge_s = ParagraphStyle("badge", fontSize=8, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)

    elements = []

    # ── Cover page ─────────────────────────────────────────────────────
    if os.path.exists(LOGO_LEFT_PATH) and os.path.exists(LOGO_RIGHT_PATH):
        from reportlab.platypus import Table, TableStyle
        logos = Table(
            [[Image(LOGO_LEFT_PATH, width=2.4 * cm, height=2.4 * cm),
              Image(LOGO_RIGHT_PATH, width=2.4 * cm, height=2.4 * cm)]],
            colWidths=[W / 2, W / 2],
        )
        logos.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, 0), "RIGHT"),
            ("ALIGN", (1, 0), (1, 0), "LEFT"),
            ("LEFTPADDING", (1, 0), (1, 0), 30),
            ("RIGHTPADDING", (0, 0), (0, 0), 30),
        ]))
        elements.append(Spacer(1, 3 * cm))
        elements.append(logos)
        elements.append(Spacer(1, 1.2 * cm))
    else:
        elements.append(Spacer(1, 5 * cm))

    elements.append(Paragraph("Abstract Book", title_s))
    elements.append(Paragraph(_esc(event_name), subtitle_s))
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph(f"{len(abstracts)} accepted abstract{'s' if len(abstracts) != 1 else ''}", subtitle_s))
    elements.append(Spacer(1, 1.5 * cm))
    elements.append(Paragraph(f"Generated {datetime.now().strftime('%d %B %Y, %H:%M')}", generated_s))
    elements.append(PageBreak())

    # ── Group by track/topic ─────────────────────────────────────────────
    tracks = {}
    for a in abstracts:
        tracks.setdefault(a.get("track") or "General", []).append(a)

    counter = 1
    for track_idx, (track_name, items) in enumerate(sorted(tracks.items())):
        if track_idx > 0:
            elements.append(PageBreak())
        elements.append(Paragraph(_esc(track_name), track_s))
        elements.append(HRFlowable(width="100%", thickness=1, color=_RED))
        elements.append(Spacer(1, 0.3 * cm))

        for a in items:
            block = []
            from reportlab.platypus import Table, TableStyle

            ptype = (a.get("presentation_type") or "oral").title()
            badge_color = _PINK if ptype.lower() == "oral" else colors.Color(0.15, 0.55, 0.45)
            head = Table(
                [[Paragraph(str(counter), abs_no_s), Paragraph(_esc(a["title"]), abs_title_s)]],
                colWidths=[1.1 * cm, W - 1.1 * cm],
            )
            head.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, 0), _PINK),
                ("TOPPADDING", (0, 0), (0, 0), 4),
                ("BOTTOMPADDING", (0, 0), (0, 0), 4),
                ("LEFTPADDING", (1, 0), (1, 0), 10),
            ]))
            block.append(head)

            authors = a.get("authors") or []
            author_bits = []
            for au in authors:
                name = au["name"] + (" *" if au.get("is_presenting") else "")
                author_bits.append(f"{_esc(name)}" + (f" ({_esc(au['affiliation'])})" if au.get("affiliation") else ""))
            if author_bits:
                block.append(Paragraph("; ".join(author_bits) + "&nbsp;&nbsp; <i>(* presenting author)</i>", authors_s))

            badge = Table([[Paragraph(ptype + " Presentation", badge_s)]], colWidths=[4.2 * cm])
            badge.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), badge_color),
                ("TOPPADDING", (0, 0), (0, 0), 3),
                ("BOTTOMPADDING", (0, 0), (0, 0), 3),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ]))
            block.append(badge)
            block.append(Spacer(1, 0.25 * cm))

            for label, body in parse_abstract_sections(a.get("abstract_text")):
                if label:
                    block.append(Paragraph(f"<b>{_esc(label)}:</b> {_esc(body)}", section_s))
                else:
                    block.append(Paragraph(_esc(body), section_s))

            if a.get("keywords"):
                block.append(Paragraph(f"<b>Keywords:</b> {_esc(a['keywords'])}", keywords_s))

            block.append(Spacer(1, 0.15 * cm))
            block.append(HRFlowable(width="100%", thickness=0.4, color=colors.lightgrey))
            block.append(Spacer(1, 0.35 * cm))

            # Keep the number/title/authors/badge header together; let long
            # bodies flow across a page break rather than force the whole
            # abstract onto one page (some run well over a page).
            elements.append(KeepTogether(block[:3]))
            elements.extend(block[3:])
            counter += 1

    doc.build(
        elements,
        onFirstPage=lambda c, d: _footer(c, d, event_name),
        onLaterPages=lambda c, d: _footer(c, d, event_name),
    )
    return buffer.getvalue()
