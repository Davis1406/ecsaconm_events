import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, HRFlowable,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

ROLE_MAP = {
    "member_state": "Member State",
    "participant": "Participant",
    "other_africa": "Other Africa",
    "world": "International",
    "student": "Student",
    "exhibitor": "Exhibitor",
    "secretariat": "Secretariat",
    "delegate": "Delegate",
    "presenter": "Presenter",
    "speaker": "Speaker",
    "sponsor": "Sponsor",
    "moderator": "Moderator",
    "moh": "Ministry of Health",
}

_RED = colors.Color(0.78, 0.08, 0.08)
_GREY = colors.Color(0.45, 0.45, 0.45)


def _p(text, style):
    return Paragraph(text, style)


def generate_receipt_pdf(
    registration_id: int,
    firstname: str,
    lastname: str,
    title_prefix: str,
    event_name: str,
    participation_role,
    amount_paid: float,
    date: datetime,
    membership_status: str = None,
    membership_arrears: float = None,
    payment_proof_url: str = None,
    photo_url: str = None,
) -> bytes:
    buffer = io.BytesIO()

    receipt_no = f"{registration_id}{date.strftime('%m%d%Y')}"

    W = A4[0] - 4 * cm   # usable page width

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # ── Styles ──────────────────────────────────────────
    normal = ParagraphStyle("n", fontSize=9, fontName="Helvetica", leading=13)
    bold9 = ParagraphStyle("b9", fontSize=9, fontName="Helvetica-Bold", leading=13)
    right9 = ParagraphStyle("r9", fontSize=9, fontName="Helvetica", leading=13, alignment=TA_RIGHT)
    right9b = ParagraphStyle("r9b", fontSize=9, fontName="Helvetica-Bold", leading=13, alignment=TA_RIGHT)
    title_s = ParagraphStyle("ts", fontSize=16, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    recno_s = ParagraphStyle("rn", fontSize=13, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=_RED, spaceAfter=10)
    note_s = ParagraphStyle("ns", fontSize=8, fontName="Helvetica-Bold", textColor=_RED, leading=12)
    small_grey = ParagraphStyle("sg", fontSize=8, fontName="Helvetica", leading=12, textColor=_GREY)
    link_s = ParagraphStyle("ls", fontSize=8, fontName="Helvetica", leading=13)
    footer_s = ParagraphStyle("fs", fontSize=8, fontName="Helvetica", alignment=TA_CENTER, textColor=_GREY)
    org_s = ParagraphStyle("os", fontSize=9, fontName="Helvetica-Bold", leading=13)
    addr_s = ParagraphStyle("as", fontSize=8, fontName="Helvetica", leading=12, alignment=TA_RIGHT)

    elements = []

    # ── Header row ───────────────────────────────────────
    logo_img = Image(LOGO_PATH, width=2.2 * cm, height=2.2 * cm) if os.path.exists(LOGO_PATH) else ""

    hdr = [[
        _p(
            "EAST, CENTRAL AND SOUTHERN<br/>AFRICA COLLEGE OF NURSING AND<br/>MIDWIFERY<br/>(ECSACONM)",
            org_s,
        ),
        logo_img,
        _p(
            "Plot No.157, Oloirien<br/>Njiro Road<br/>P.O. Box 1009<br/>Arusha, Tanzania<br/>"
            "Tel: 255-27-2549362; 2549365/6<br/>E-mail: info@ecsacon.org",
            addr_s,
        ),
    ]]
    col_l = 6 * cm
    col_m = 2.8 * cm
    col_r = W - col_l - col_m
    hdr_tbl = Table(hdr, colWidths=[col_l, col_m, col_r])
    hdr_tbl.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (1, 0), (1,  0),  "CENTER"),
        ("ALIGN",        (2, 0), (2,  0),  "RIGHT"),
        ("LINEBELOW",    (0, 0), (0,  0),  0.8, colors.black),
        ("LINEBELOW",    (2, 0), (2,  0),  0.8, colors.black),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(hdr_tbl)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Title ─────────────────────────────────────────────
    elements.append(_p("RECEIPT", title_s))
    elements.append(_p(f"No.  {receipt_no}", recno_s))

    # ── Address / Date block ──────────────────────────────
    full_name = " ".join(filter(None, [title_prefix, firstname, lastname]))
    date_str = date.strftime("%-d-%b-%Y")

    ad = [[
        _p(f"<b>Address:</b><br/>{full_name}<br/>{registration_id}", normal),
        _p(f"<b>Date:</b>  {date_str}", normal),
    ]]
    ad_tbl = Table(ad, colWidths=[W * 0.60, W * 0.40])
    ad_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.8, colors.black),
        ("LINEAFTER",     (0, 0), (0,  -1), 0.8, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(ad_tbl)

    # ── Items table ───────────────────────────────────────
    role_str = participation_role
    if hasattr(role_str, "value"):
        role_str = role_str.value
    role_label = ROLE_MAP.get(str(role_str).lower(), str(role_str) or "Participant")
    amt = float(amount_paid) if amount_paid else 0.0
    amt_str = f"{amt:,.0f}"

    col_item  = 1.2 * cm
    col_ref   = W * 0.36
    col_desc  = W * 0.30
    col_amt   = W - col_item - col_ref - col_desc

    rows = [
        [_p("<b>Item</b>", bold9), _p("<b>Ref.</b>", bold9), _p("<b>Description</b>", bold9), _p("<b>Amount<br/>(USD)</b>", bold9)],
        [_p("1", normal), _p(event_name or "Conference Registration", normal), _p(role_label, normal), _p(amt_str, right9)],
        [_p("", normal), _p("", normal), _p("<b>Total Amount</b>", bold9), _p(f"<b>{amt_str}</b>", right9b)],
    ]
    items_tbl = Table(rows, colWidths=[col_item, col_ref, col_desc, col_amt])
    items_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.8, colors.black),
        ("LINEBELOW",     (0, 0), (-1,  0), 0.8, colors.black),
        ("LINEABOVE",     (0, 2), (-1,  2), 0.8, colors.black),
        ("LINEAFTER",     (0, 0), (2,  -1), 0.5, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("SPAN",          (0, 2), (1,  2)),
    ]))
    elements.append(items_tbl)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Members section ──────────────────────────────────
    show_members = membership_status or (membership_arrears is not None and membership_arrears > 0)
    if show_members:
        elements.append(HRFlowable(width="100%", thickness=0.6, color=colors.black))
        elements.append(Spacer(1, 0.12 * cm))
        elements.append(_p("<b>For ECSACONM Members only</b>", bold9))
        elements.append(HRFlowable(width="100%", thickness=0.6, color=colors.black))
        elements.append(Spacer(1, 0.15 * cm))

        if membership_status:
            elements.append(_p(f"<b>Membership Status</b> - {membership_status}", normal))
        if membership_arrears is not None and membership_arrears > 0:
            elements.append(_p(f"<b>* Membership Arrears</b> - {membership_arrears:,.0f}", normal))
            elements.append(Spacer(1, 0.1 * cm))
            elements.append(_p(
                "* Note: Membership arrears, if applicable, must be fully settled prior to "
                "issuance of a Proof of Conference Registration Letter.",
                note_s,
            ))
        elements.append(Spacer(1, 0.35 * cm))

    # ── Proof / Photo links ───────────────────────────────
    if payment_proof_url or photo_url:
        elements.append(HRFlowable(width="100%", thickness=0.3, color=colors.lightgrey))
        elements.append(Spacer(1, 0.15 * cm))
        if payment_proof_url:
            elements.append(_p(
                f'<b>Payment Proof: </b>'
                f'<a href="{payment_proof_url}" color="#1155CC">{payment_proof_url}</a>',
                link_s,
            ))
        if photo_url:
            elements.append(_p(
                f'<b>Badge / Passport Photo: </b>'
                f'<a href="{photo_url}" color="#1155CC">{photo_url}</a>',
                link_s,
            ))
        elements.append(Spacer(1, 0.35 * cm))

    # ── Footer ────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(_p("© All Rights Reserved, ECSACONM", footer_s))

    doc.build(elements)
    return buffer.getvalue()
