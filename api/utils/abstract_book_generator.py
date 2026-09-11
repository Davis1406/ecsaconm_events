"""Generates the conference Abstract Book — a paginated PDF listing accepted
oral-presentation abstracts, grouped by topic/track, with Background/Methods/
Results/Conclusion sections bolded and indented for readability. Opens with
the conference preface (cover, welcome messages, overview) so the book reads
as a standalone document rather than just a raw abstract dump.
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
    PageBreak, KeepTogether, Table, TableStyle,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
LOGO_LEFT_PATH = os.path.join(ASSETS_DIR, "logo_left.png")
LOGO_RIGHT_PATH = os.path.join(ASSETS_DIR, "logo.png")

_PINK = colors.Color(254 / 255.0, 80 / 255.0, 103 / 255.0)
_PINK_TINT = colors.Color(254 / 255.0, 80 / 255.0, 103 / 255.0, alpha=0.07)
_RED = colors.Color(220 / 255.0, 50 / 255.0, 75 / 255.0)
_GREY = colors.Color(0.45, 0.45, 0.45)
_DARK = colors.Color(0.13, 0.15, 0.18)
_TEAL = colors.Color(0.13, 0.42, 0.47)

# Static preface content (welcome messages / overview) — specific to this
# conference's printed programme, mirrored here so the Abstract Book carries
# the same front matter rather than opening cold on a list of abstracts.
_WELCOME_PRESIDENT = """
Dear Distinguished Guests, Delegates, Partners, Fellows, Nurses, Midwives, Researchers, Educators and
Friends of ECSACONM,<br/><br/>
It is my great honour and pleasure to welcome you to the 17th ECSACONM Biennial Scientific Conference
and 8th Quadrennial General Assembly in Zanzibar, United Republic of Tanzania.<br/><br/>
This year's conference is convened under the theme &ldquo;Nurses and Midwives Sustaining Quality Healthcare
in a Changing World.&rdquo; The theme reflects the essential role of nurses and midwives in responding to
evolving health needs, strengthening health systems, advancing equity, promoting research and innovation,
and sustaining quality care across our region and beyond.<br/><br/>
The scientific conference provides a regional platform for sharing evidence, exchanging best practices,
presenting research findings, strengthening professional networks and building collaboration. It brings
together nurses, midwives, educators, researchers, policymakers, regulators, health leaders and partners
who share a commitment to advancing nursing and midwifery excellence.<br/><br/>
This gathering is also a moment of celebration as we recognise ECSACONM fellows who have successfully
completed their specialist training. Their achievement reflects the College's continued commitment to
developing a competent, confident and highly skilled nursing and midwifery workforce for the region.<br/><br/>
As we proceed to the Quadrennial General Assembly, we will reflect on our collective progress, deliberate on
priorities for the College and the profession, and elect new leadership to guide ECSACONM into its next
chapter.<br/><br/>
On behalf of ECSACONM, I warmly welcome you all and wish you a productive, inspiring and memorable
conference.
""".strip()

_WELCOME_DG = """
Dear Distinguished Delegates, Colleagues and Partners,<br/><br/>
On behalf of the East, Central and Southern Africa Health Community (ECSA-HC), I am pleased to welcome
you to the 17th ECSACONM Biennial Scientific Conference.<br/><br/>
ECSACONM remains an important professional college within the ECSA-HC family, contributing to the
strengthening of nursing and midwifery education, practice, leadership, research and regulation across the
region. Nurses and midwives are central to resilient health systems, universal health coverage, quality
service delivery and effective responses to emerging and re-emerging health challenges.<br/><br/>
The conference theme, &ldquo;Nurses and Midwives Sustaining Quality Healthcare in a Changing World,&rdquo;
speaks directly to the realities facing health systems today. Workforce shortages, technological
transformation, disease outbreaks, inequities in access, climate-related pressures and changing population
needs require a well-prepared, innovative and resilient nursing and midwifery workforce.<br/><br/>
This conference is an opportunity to strengthen regional dialogue, promote evidence-based practice, build
professional networks and identify practical solutions that can improve healthcare delivery across our member
states. I commend ECSACONM for its continued leadership and congratulate the graduating fellows.<br/><br/>
I wish all delegates fruitful deliberations and a successful conference.
""".strip()

_OBJECTIVES = [
    "Provide a regional platform for dissemination of nursing and midwifery research, innovation and "
    "evidence-informed practice.",
    "Strengthen dialogue on equitable access to quality healthcare and the contribution of nurses and "
    "midwives to stronger health systems.",
    "Advance nursing and midwifery leadership, advocacy, regulation and policy engagement.",
    "Promote responsible integration of technology into nursing and midwifery education, regulation and "
    "practice.",
    "Build professional preparedness and resilience in relation to climate change, environmental "
    "sustainability and emerging health threats.",
    "Facilitate networking, mentorship, partnership development and regional knowledge exchange.",
    "Celebrate the achievements of graduating ECSACONM fellows and conduct the statutory business of the "
    "Quadrennial General Assembly.",
]

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


def _fmt_date_range(start_date, end_date):
    if not start_date:
        return ""
    if not end_date or end_date.date() == start_date.date():
        return start_date.strftime("%d %B %Y")
    if end_date.strftime("%B %Y") == start_date.strftime("%B %Y"):
        return f"{start_date.day}–{end_date.day} {start_date.strftime('%B %Y')}"
    return f"{start_date.strftime('%d %B')} – {end_date.strftime('%d %B %Y')}"


def _pill(text, W, bg, fg=colors.white):
    style = ParagraphStyle("pill", fontSize=9, fontName="Helvetica-Bold", textColor=fg, alignment=TA_CENTER)
    t = Table([[Paragraph(_esc(text), style)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), bg),
        ("TOPPADDING", (0, 0), (0, 0), 6),
        ("BOTTOMPADDING", (0, 0), (0, 0), 6),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
    ]))
    return t


def generate_abstract_book_pdf(event_name: str, abstracts: list, event_meta: dict = None) -> bytes:
    """`abstracts` is a list of dicts:
    {id, title, track, keywords, presentation_type, abstract_text,
     authors: [{name, affiliation, is_presenting}]}
    already filtered/ordered by the caller (accepted + paid + oral presenter).
    `event_meta` optionally supplies {theme, start_date, end_date, location}
    used to render the preface pages.
    """
    event_meta = event_meta or {}
    buffer = io.BytesIO()
    W = A4[0] - 4 * cm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )

    title_s = ParagraphStyle("title", fontSize=25, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=colors.white, leading=30)
    event_s = ParagraphStyle("event", fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=_DARK, leading=19, spaceAfter=10)
    theme_s = ParagraphStyle("theme", fontSize=12.5, fontName="Helvetica-Oblique", alignment=TA_CENTER, textColor=_DARK, leading=17)
    subtitle_s = ParagraphStyle("subtitle", fontSize=11, fontName="Helvetica", alignment=TA_CENTER, textColor=_GREY, spaceAfter=4)
    generated_s = ParagraphStyle("generated", fontSize=9, fontName="Helvetica-Oblique", alignment=TA_CENTER, textColor=_GREY)
    track_s = ParagraphStyle("track", fontSize=13, fontName="Helvetica-Bold", textColor=colors.white)
    abs_no_s = ParagraphStyle("absno", fontSize=9, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)
    abs_title_s = ParagraphStyle("abstitle", fontSize=12, fontName="Helvetica-Bold", textColor=_DARK, leading=15, spaceAfter=3)
    authors_s = ParagraphStyle("authors", fontSize=9.5, fontName="Helvetica-Oblique", textColor=colors.Color(0.3, 0.3, 0.3), leading=13, spaceAfter=6)
    section_s = ParagraphStyle("section", fontSize=10, fontName="Helvetica", leading=14, leftIndent=10, spaceAfter=6, alignment=TA_LEFT)
    keywords_s = ParagraphStyle("keywords", fontSize=8.5, fontName="Helvetica-Oblique", textColor=_GREY, leading=12, spaceBefore=2)
    page_head_s = ParagraphStyle("pagehead", fontSize=17, fontName="Helvetica-Bold", textColor=colors.white)
    body_s = ParagraphStyle("body", fontSize=10, fontName="Helvetica", leading=15, textColor=colors.Color(0.25, 0.25, 0.25), spaceAfter=4)
    signoff_s = ParagraphStyle("signoff", fontSize=10.5, fontName="Helvetica-Bold", textColor=_DARK, spaceBefore=10)
    signoff_role_s = ParagraphStyle("signoffrole", fontSize=9.5, fontName="Helvetica", textColor=_GREY)
    bullet_s = ParagraphStyle("bullet", fontSize=10, fontName="Helvetica", leading=14.5, leftIndent=14, bulletIndent=2, spaceAfter=6, textColor=colors.Color(0.25, 0.25, 0.25))
    divider_count_s = ParagraphStyle("dividercount", fontSize=44, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=_PINK, leading=54, spaceAfter=10)
    divider_label_s = ParagraphStyle("dividerlabel", fontSize=11, fontName="Helvetica", alignment=TA_CENTER, textColor=_GREY)

    def _banner(text_paragraph, height_pad=10, bg=_PINK):
        t = Table([[text_paragraph]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), bg),
            ("TOPPADDING", (0, 0), (0, 0), height_pad),
            ("BOTTOMPADDING", (0, 0), (0, 0), height_pad),
            ("LEFTPADDING", (0, 0), (0, 0), 14),
        ]))
        return t

    elements = []

    # ── Cover page ─────────────────────────────────────────────────────
    if os.path.exists(LOGO_LEFT_PATH) and os.path.exists(LOGO_RIGHT_PATH):
        logos = Table(
            [[Image(LOGO_LEFT_PATH, width=2.3 * cm, height=2.3 * cm),
              Image(LOGO_RIGHT_PATH, width=2.3 * cm, height=2.3 * cm)]],
            colWidths=[W / 2, W / 2],
        )
        logos.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, 0), "RIGHT"),
            ("ALIGN", (1, 0), (1, 0), "LEFT"),
            ("LEFTPADDING", (1, 0), (1, 0), 30),
            ("RIGHTPADDING", (0, 0), (0, 0), 30),
        ]))
        elements.append(Spacer(1, 1.6 * cm))
        elements.append(logos)
        elements.append(Spacer(1, 1 * cm))
    else:
        elements.append(Spacer(1, 3 * cm))

    elements.append(_banner(Paragraph("ABSTRACT BOOK", title_s), height_pad=14))
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(_esc(event_name), event_s))

    theme = event_meta.get("theme")
    if theme:
        elements.append(Paragraph(f"&ldquo;{_esc(theme)}&rdquo;", theme_s))
    elements.append(Spacer(1, 0.9 * cm))

    date_range = _fmt_date_range(event_meta.get("start_date"), event_meta.get("end_date"))
    location = event_meta.get("location")
    pills = [p for p in [date_range, location] if p]
    if pills:
        pill_w = W / len(pills)
        row = Table([[_pill(p, pill_w - 10, _TEAL if i == 0 else _DARK) for i, p in enumerate(pills)]], colWidths=[pill_w] * len(pills))
        row.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
        elements.append(row)

    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(
        f"{len(abstracts)} accepted oral presentation{'s' if len(abstracts) != 1 else ''}", subtitle_s))
    elements.append(Spacer(1, 1.2 * cm))
    elements.append(Paragraph(f"Generated {datetime.now().strftime('%d %B %Y, %H:%M')}", generated_s))
    elements.append(PageBreak())

    # ── Welcome messages ──────────────────────────────────────────────
    elements.append(_banner(Paragraph("WELCOME MESSAGE", page_head_s)))
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("From the ECSACONM President", event_s))
    elements.append(Spacer(1, 0.2 * cm))
    for para in _WELCOME_PRESIDENT.split("<br/><br/>"):
        elements.append(Paragraph(para, body_s))
    elements.append(Paragraph("Dr. Glory Msibi", signoff_s))
    elements.append(Paragraph("President, ECSACONM", signoff_role_s))
    elements.append(PageBreak())

    elements.append(_banner(Paragraph("WELCOME MESSAGE", page_head_s), bg=_TEAL))
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("From the ECSA-HC Director General", event_s))
    elements.append(Spacer(1, 0.2 * cm))
    for para in _WELCOME_DG.split("<br/><br/>"):
        elements.append(Paragraph(para, body_s))
    elements.append(Paragraph("Dr. Ntuli Angyelile Kapologwe", signoff_s))
    elements.append(Paragraph("Director General, ECSA-HC", signoff_role_s))
    elements.append(PageBreak())

    # ── Conference overview ────────────────────────────────────────────
    elements.append(_banner(Paragraph("CONFERENCE OVERVIEW", page_head_s), bg=_DARK))
    elements.append(Spacer(1, 0.4 * cm))
    overview_bits = [event_name]
    if date_range:
        overview_bits.append(f"will be held from {date_range}")
    if location:
        overview_bits.append(f"at {location}")
    elements.append(Paragraph(
        f"The {_esc(' '.join(overview_bits))}. The scientific conference combines keynote and plenary "
        "addresses, parallel oral presentations, panel discussions, poster sessions, partner-led side "
        "sessions, professional networking and the ECSACONM fellowship graduation ceremony.",
        body_s,
    ))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph("Conference Objectives", ParagraphStyle("objh", fontSize=12, fontName="Helvetica-Bold", textColor=_PINK, spaceAfter=6)))
    for obj in _OBJECTIVES:
        elements.append(Paragraph(f"&#8226;&nbsp;&nbsp;{_esc(obj)}", bullet_s))
    elements.append(PageBreak())

    # ── Section divider before the abstract listing ────────────────────
    elements.append(Spacer(1, 4 * cm))
    elements.append(Paragraph(str(len(abstracts)), divider_count_s))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("ACCEPTED ORAL PRESENTATIONS", ParagraphStyle("dividertitle", fontSize=18, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=_DARK, spaceBefore=6, spaceAfter=8)))
    elements.append(Paragraph("Consolidated index of abstracts, grouped by topic", divider_label_s))
    elements.append(PageBreak())

    # ── Group by track/topic ─────────────────────────────────────────────
    tracks = {}
    for a in abstracts:
        tracks.setdefault(a.get("track") or "General", []).append(a)

    counter = 1
    for track_idx, (track_name, items) in enumerate(sorted(tracks.items())):
        if track_idx > 0:
            elements.append(PageBreak())
        elements.append(_banner(Paragraph(_esc(track_name), track_s), height_pad=8))
        elements.append(Spacer(1, 0.4 * cm))

        for a in items:
            block = []

            head = Table(
                [[Paragraph(str(counter), abs_no_s), Paragraph(_esc(a["title"]), abs_title_s)]],
                colWidths=[1.1 * cm, W - 1.1 * cm],
            )
            head.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, 0), _PINK),
                ("BACKGROUND", (1, 0), (1, 0), _PINK_TINT),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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
            block.append(Spacer(1, 0.2 * cm))

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

            # Keep the number/title/authors header together; let long bodies
            # flow across a page break rather than force the whole abstract
            # onto one page (some run well over a page).
            elements.append(KeepTogether(block[:2]))
            elements.extend(block[2:])
            counter += 1

    doc.build(
        elements,
        onFirstPage=lambda c, d: _footer(c, d, event_name),
        onLaterPages=lambda c, d: _footer(c, d, event_name),
    )
    return buffer.getvalue()
