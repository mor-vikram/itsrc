from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import datetime
import qrcode
import streamlit as st


def draw_page_border_and_watermark(canvas, doc):
    """Draws border and watermark."""
    width, height = A4
    canvas.saveState()

    # === Border ===
    margin = 25
    radius = 15
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(1.2)
    canvas.roundRect(margin, margin, width - 2 * margin, height - 2 * margin, radius)

    # === Watermark ===
    canvas.setFont("Helvetica-Bold", 36)
    canvas.setFillColorRGB(0.85, 0.85, 0.85, alpha=0.5)
    canvas.saveState()
    canvas.translate(width / 2, height / 2)
    canvas.rotate(30)
    canvas.drawCentredString(0, 0, "ITSRC, Vadodara Annual Sports 2025")
    canvas.restoreState()

    canvas.restoreState()


def generate_participant_pdf(participant_data, logo_path="logo.jpg", output_path="participant_form.pdf"):
    """
    Generate a styled participant form PDF (A4 portrait) with border, watermark, QR code, and clean layout.
    """

    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=50
    )
    story = []
    styles = getSampleStyleSheet()

    # === Header Styles ===
    header_style = ParagraphStyle(
        'header_style', fontSize=18, alignment=1,
        spaceAfter=12, leading=22, textColor=colors.darkblue
    )
    subheader_style = ParagraphStyle(
        'subheader_style', fontSize=11, alignment=1, textColor=colors.grey
    )

    # === Logo ===
    try:
        logo = Image(logo_path, width=65, height=65)
    except Exception:
        logo = None

    # === QR Code ===
    base_url = st.secrets.get("APP_BASE_URL", "http://itsrc2025.streamlit.app")
    verification_url = participant_data.get(
        "verification_url",
        f"{base_url}/?verify_id={participant_data.get('id','')}"
    )

    qr_img = qrcode.make(verification_url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer)
    qr_buffer.seek(0)
    qr = Image(qr_buffer, width=70, height=70)

    # === Header Layout (Logo | Title | QR) ===
    header_table_data = [[logo, Paragraph("<b>ITSRC, Vadodara Annual Sports @ 2025</b>", header_style), qr]]
    header_table = Table(header_table_data, colWidths=[80, 380, 80])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(header_table)
    story.append(Paragraph("Participant Registration Form", subheader_style))
    story.append(Spacer(1, 15))

    # === Participant Info Table ===
    info_labels = [
        ("Name", participant_data.get("name", "")),
        ("Post", participant_data.get("post", "")),
        ("House", participant_data.get("house", "")),
        ("Event(s)", participant_data.get("event", "")),
        ("Contact Number", participant_data.get("contact", "")),
        ("Posting", participant_data.get("posting", "")),
        ("Category", participant_data.get("category", "")),
        ("Gender", participant_data.get("gender", "")),
        ("Age", participant_data.get("age", "")),
        ("Fee Paid (INR)", participant_data.get("fee", "")),
        ("Date of Registration", participant_data.get("registration_date", datetime.date.today().strftime("%d-%m-%Y"))),
    ]

    table_data = [
        [Paragraph(f"<b>{label}</b>", styles["Normal"]), Paragraph(str(value), styles["Normal"])]
        for label, value in info_labels
    ]

    info_table = Table(table_data, colWidths=[160, 340])
    info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.6, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 40))

    # === Signature Section ===
    footer_table_data = [[
        Paragraph("<b>Participant Signature</b>", styles["Normal"]),
        "",
        Paragraph("<b>Event Official Signature</b>", styles["Normal"])
    ]]
    footer = Table(footer_table_data, colWidths=[180, 200, 180])
    footer.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 40),
        ('LEFTPADDING', (0,0), (-1,-1), 40),
    ]))
    story.append(footer)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Organized by ITSRC Sports Committee</i>", subheader_style))

    # === Build PDF with Border + Watermark ===
    pdf.build(story, onFirstPage=draw_page_border_and_watermark, onLaterPages=draw_page_border_and_watermark)
    buffer.seek(0)

    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())

    return output_path


