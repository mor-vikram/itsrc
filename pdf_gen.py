"""
ITSRC participant registration form PDF generator.

Drop-in replacement for the existing pdf_gen.py.
Public function signature is intentionally preserved:
    generate_participant_pdf(participant_data, logo_path, output_path="participant_form.pdf")
"""
from io import BytesIO
from pathlib import Path
from datetime import datetime, date
from html import escape
from zoneinfo import ZoneInfo

import qrcode
try:
    import streamlit as st
except ImportError:
    st = None
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
    KeepTogether
)

HOUSE_CAPTAINS = {
    "CC Challengers": "Shri Rakesh Kumar, ITO",
    "JAO Giants": "Shri Abid Ali Quadri, ITO",
    "Faceless Fighters": "Shri Bablu Meena, ITO",
    "Investigation Warriors": "Shri Rohit S B Gupta, ITI",
}

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#087E78")
MINT = colors.HexColor("#EAF5F2")
PALE = colors.HexColor("#F4F7FA")
GOLD = colors.HexColor("#D6A642")
INK = colors.HexColor("#243746")
MUTED = colors.HexColor("#667785")
LINE = colors.HexColor("#D8E2E8")
WHITE = colors.white


def _safe(value):
    """Escape user-supplied text before placing it in a ReportLab Paragraph."""
    if value is None:
        return "—"
    text = str(value).strip()
    return escape(text) if text else "—"


def _registration_datetime(value):
    """Format registration timestamp in Indian Standard Time where possible."""
    if not value:
        return date.today().strftime("%d %b %Y")
    try:
        if isinstance(value, datetime):
            dt = value
        else:
            raw = str(value).strip()
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                # Preserve an unrecognised but readable date instead of failing PDF creation.
                return _safe(raw)
        if dt.tzinfo is not None:
            dt = dt.astimezone(ZoneInfo("Asia/Kolkata"))
        return dt.strftime("%d %b %Y")
    except Exception:
        return _safe(value)


def draw_page_border_and_watermark(canvas, doc):
    """Subtle page frame, watermark and footer."""
    width, height = A4
    canvas.saveState()

    # Soft page frame
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.8)
    canvas.roundRect(11 * mm, 10 * mm, width - 22 * mm, height - 20 * mm, 9, stroke=1, fill=0)

    # Restrained diagonal watermark
    canvas.saveState()
    canvas.translate(width / 2, height / 2)
    canvas.rotate(32)
    canvas.setFillColor(colors.HexColor("#E8EFED"))
    canvas.setFont("Helvetica-Bold", 27)
    canvas.drawCentredString(0, 0, "ITSRC  •  VADODARA")
    canvas.restoreState()

    # Footer line and label
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 17 * mm, width - 18 * mm, 17 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(19 * mm, 12.5 * mm, "ITSRC  |  Annual Sports Meet 2026–27")
    canvas.drawRightString(width - 19 * mm, 12.5 * mm, "Participant Registration Form")
    canvas.restoreState()


def _make_qr(verification_url):
    qr_code = qrcode.QRCode(box_size=5, border=1)
    qr_code.add_data(verification_url)
    qr_code.make(fit=True)
    qr_image = qr_code.make_image(fill_color="#17324D", back_color="white").convert("RGB")
    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    return Image(buffer, width=21 * mm, height=21 * mm)


def generate_participant_pdf(participant_data, logo_path, output_path="participant_form.pdf"):
    """
    Generate an A4, print-friendly participant registration form cum receipt.
    Keeps the original function signature and participant_data field names.
    """
    participant_data = participant_data or {}
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=23 * mm,
        title="ITSRC Participant Registration Form - Annual Sports Meet 2026-27",
        author="Income Tax Sports & Recreation Club, Vadodara",
    )

    base = getSampleStyleSheet()
    styles = {
        "club": ParagraphStyle(
            "ClubHeading", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=14, leading=17, textColor=NAVY, alignment=TA_CENTER,
        ),
        "event": ParagraphStyle(
            "EventHeading", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=12, textColor=TEAL, alignment=TA_CENTER,
        ),
        "form": ParagraphStyle(
            "FormHeading", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, textColor=WHITE, alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "SectionHeading", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=11, textColor=NAVY,
        ),
        "label": ParagraphStyle(
            "FieldLabel", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.5, leading=11, textColor=TEAL,
        ),
        "value": ParagraphStyle(
            "FieldValue", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.2, leading=12, textColor=INK, wordWrap="CJK",
        ),
        "hero_name": ParagraphStyle(
            "HeroName", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=15, leading=18, textColor=NAVY,
        ),
        "hero_house": ParagraphStyle(
            "HeroHouse", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10, leading=13, textColor=TEAL,
        ),
        "small": ParagraphStyle(
            "SmallNote", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10, textColor=MUTED,
        ),
        "approval": ParagraphStyle(
            "ApprovalTitle", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=12, textColor=NAVY,
        ),
        "instruction": ParagraphStyle(
            "Instruction", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=12, textColor=NAVY, alignment=TA_CENTER,
        ),
        "qr_caption": ParagraphStyle(
            "QrCaption", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=6.4, leading=7.5, textColor=TEAL, alignment=TA_CENTER,
        ),
    }

    name = participant_data.get("name", "")
    post = participant_data.get("post", "")
    house = participant_data.get("house", "")
    event = participant_data.get("event", "")
    contact = participant_data.get("contact", "")
    posting = participant_data.get("posting", "")
    category = participant_data.get("category", "")
    gender = participant_data.get("gender", "")
    age = participant_data.get("age", "")
    fee = participant_data.get("fee", "")
    reg_date = _registration_datetime(participant_data.get("registration_date"))
    captain_name = HOUSE_CAPTAINS.get(str(house), "House Captain")
    registration_id = participant_data.get("id", "")

    # Base URL lookup is guarded so the module also works outside Streamlit runtime.
    try:
        base_url = st.secrets.get("APP_BASE_URL", "http://itsrcvadodara.streamlit.app") if st is not None else "http://itsrcvadodara.streamlit.app"
    except Exception:
        base_url = "http://itsrcvadodara.streamlit.app"
    verification_url = participant_data.get(
        "verification_url",
        f"{base_url}/?verify_id={registration_id}"
    )

    # Header: logo | club identity | QR
    logo = ""
    try:
        if logo_path and Path(str(logo_path)).is_file():
            logo = Image(str(logo_path), width=22 * mm, height=22 * mm, kind="proportional")
    except Exception:
        logo = ""

    qr = _make_qr(verification_url)
    heading = [
        Paragraph("INCOME TAX SPORTS &amp; RECREATION CLUB", styles["club"]),
        Paragraph("VADODARA", styles["event"]),
        Spacer(1, 2),
        Paragraph("ANNUAL SPORTS MEET 2026–27", styles["event"]),
    ]
    qr_block = [qr, Spacer(1, 1), Paragraph("Scan QR to see<br/>Approval Status", styles["qr_caption"])]
    header = Table([[logo, heading, qr_block]], colWidths=[25 * mm, 128 * mm, 25 * mm])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    story = [header, Spacer(1, 3 * mm)]
    title_bar = Table([[Paragraph("PARTICIPANT REGISTRATION FORM CUM RECEIPT", styles["form"])]],
                      colWidths=[178 * mm])
    title_bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([title_bar, Spacer(1, 5 * mm)])

    # Participant identity panel
    identity = Table([[
        [
            Paragraph(_safe(name), styles["hero_name"]),
            Paragraph(f"HOUSE  •  {_safe(house)}", styles["hero_house"]),
        ],
        [
            Paragraph(f"<b>Registration ID:</b> {_safe(registration_id)}", styles["small"]),
            Paragraph(f"<b>Registered:</b> {_safe(reg_date)}", styles["small"]),
        ],
    ]], colWidths=[112 * mm, 66 * mm])
    identity.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MINT),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#B8D8D0")),
        ("LINEBEFORE", (1, 0), (1, 0), 0.7, colors.HexColor("#B8D8D0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([identity, Spacer(1, 4 * mm)])

    story.append(Paragraph("PARTICIPANT DETAILS", styles["section"]))
    story.append(Spacer(1, 2 * mm))

    fields = [
        ("Post Held", post),
        ("Office / Posting Details", posting),
        ("Contact Number", contact),
        ("Gender", gender),
        ("Age", age),
        ("Category", category),
    ]
    rows = []
    for label, value in fields:
        rows.append([Paragraph(_safe(label), styles["label"]),
                     Paragraph(_safe(value), styles["value"])])

    details = Table(rows, colWidths=[52 * mm, 126 * mm], hAlign="LEFT")
    details.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PALE),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([details, Spacer(1, 4 * mm)])

    # Events and fee are deliberately prominent.
    story.append(Paragraph("EVENTS &amp; REGISTRATION FEE", styles["section"]))
    story.append(Spacer(1, 2 * mm))
    event_text = _safe(event).replace(" | ", "<br/>").replace("; ", "<br/>")
    event_panel = Table([
        [Paragraph("<b>Events Registered</b>", styles["label"])],
        [Paragraph(event_text, styles["value"])],
        [Paragraph(f"<b>Registration Fee:</b> Rs. {_safe(fee)}", styles["hero_house"])],
    ], colWidths=[178 * mm])
    event_panel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.45, LINE),
        ("LINEBELOW", (0, 1), (-1, 1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([event_panel, Spacer(1, 5 * mm)])

    story.append(Paragraph("VERIFICATION &amp; APPROVAL", styles["section"]))
    story.append(Spacer(1, 2 * mm))
    participant_cell = [
        Paragraph("PARTICIPANT", styles["approval"]),
        Spacer(1, 14 * mm),
        Paragraph("Signature: __________________________", styles["small"]),
        Spacer(1, 2 * mm),
        Paragraph("Date: ______________________________", styles["small"]),
    ]
    captain_cell = [
        Paragraph("HOUSE CAPTAIN", styles["approval"]),
        Spacer(1, 14 * mm),
        Paragraph(f"<b>{_safe(captain_name)}</b>", styles["value"]),
        Paragraph(f"House Captain – {_safe(house)}", styles["small"]),
        Spacer(1, 2 * mm),
        Paragraph("Signature / Date: ____________________", styles["small"]),
    ]
    approval = Table([[participant_cell, captain_cell]], colWidths=[89 * mm, 89 * mm])
    approval.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PALE),
        ("BACKGROUND", (1, 0), (1, 0), MINT),
        ("BOX", (0, 0), (-1, -1), 0.65, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.65, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([approval, Spacer(1, 4 * mm)])

    instruction_box = Table([[
        Paragraph("Please submit this form, along with the applicable registration fee, to your House Captain.",
                  styles["instruction"])
    ]], colWidths=[178 * mm])
    instruction_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E8")),
        ("BOX", (0, 0), (-1, -1), 0.7, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([
        instruction_box,
        Spacer(1, 3 * mm),
        Paragraph("Organised by ITSRC Sports Committee", ParagraphStyle(
            "CommitteeFooter", parent=styles["small"], alignment=TA_CENTER,
            fontName="Helvetica-Oblique",
        )),
    ])

    doc.build(story, onFirstPage=draw_page_border_and_watermark,
              onLaterPages=draw_page_border_and_watermark)

    buffer.seek(0)
    output_path = str(output_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as output_file:
        output_file.write(buffer.getvalue())
    return output_path
