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
from reportlab.graphics.shapes import Drawing, Rect

HOUSE_CAPTAINS = {
    "CC Challengers": "Shri Rakesh Kumar, ITO",
    "JAO Giants": "Shri Kishor Kumar, ITO",
    "Faceless Fighters": "Shri K K Vijayan, ITO",
    "Investigation Warriors": "Shri Rohit S B Gupta, ITI",
}

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


def generate_participant_pdf(participant_data,logo_path,output_path="participant_form.pdf"):
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

    # -------- Custom styles --------
    title_style = ParagraphStyle(
        "TitleBig",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=1,  # center
        textColor=colors.HexColor("#004d40"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#00695c"),
        spaceAfter=4,
    )
    form_title_style = ParagraphStyle(
        "FormTitle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        alignment=1,
        textColor=colors.black,
        spaceBefore=6,
        spaceAfter=10,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#004d40"),
    )
    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=13,
        textColor=colors.black,
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
    )
    italic_grey_style = ParagraphStyle(
        "ItalicGrey",
        parent=styles["Italic"],
        fontSize=9,
        leading=12,
        textColor=colors.grey,
        alignment=1,
    )
    approved_style = ParagraphStyle(
        "Approved",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#000000"),
        alignment=0,  # left align
        spaceAfter=6,
    )

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
    story.append(Paragraph("(Sports Events @2025-26)", subtitle_style))
    story.append(Paragraph("Participant Registration Form", form_title_style))
    story.append(Spacer(1, 15))

    

    # -------- Participant details table --------
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
    reg_date = participant_data.get(
        "registration_date",
        datetime.date.today().strftime("%d-%m-%Y"),
    )

    data_rows = [
        [Paragraph("<b>Name</b>", label_style),
         Paragraph(str(name), value_style)],
        [Paragraph("<b>House</b>", label_style),
         Paragraph(str(house), value_style)],
        [Paragraph("<b>Post Held</b>", label_style),
         Paragraph(str(post), value_style)],
        [Paragraph("<b>Posting Details</b>", label_style),
         Paragraph(str(posting), value_style)],
        [Paragraph("<b>Contact Number</b>", label_style),
         Paragraph(str(contact), value_style)],
        [Paragraph("<b>Gender</b>", label_style),
         Paragraph(str(gender), value_style)],
        [Paragraph("<b>Age</b>", label_style),
         Paragraph(str(age), value_style)],
        [Paragraph("<b>Category</b>", label_style),
         Paragraph(str(category), value_style)],
        [Paragraph("<b>Events Registered</b>", label_style),
         Paragraph(str(event), value_style)],
        [Paragraph("<b>Fee</b>", label_style),
         Paragraph(f"Rs. {fee}", value_style)],
        [Paragraph("<b>Date of Registration</b>", label_style),
         Paragraph(str(reg_date), value_style)],
    ]

    details_table = Table(data_rows, colWidths=[140, 360])
    details_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0f2f1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 16))

    # === Footer Section ===
    house_name = participant_data.get("house", "")
    captain_name = HOUSE_CAPTAINS.get(house_name, "House Captain")

    footer_table_data = [
        [
            Paragraph("<b>Signature of Participant</b>", footer_style),            
            ""
        ],
        [
            Paragraph(f"<b>Date:</b> {datetime.date.today().strftime('%d-%m-%Y')}", footer_style),
            Paragraph("", footer_style),
            
            Paragraph(f"<b>{captain_name}</b><br/><i>House Captain, {house_name}</i>", footer_style),
            ""
        ]
    ]

    footer = Table(footer_table_data, colWidths=[180, 50, 180])
    footer.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Align content in first column to the left
        ('ALIGN', (2, 0), (2, 1), 'RIGHT'), # Align content in second column to the right
        ('VALIGN', (0, 0), (1, 0), 'TOP'),  # Align both vertically to the top
        ('TOPPADDING', (0,0), (-1,-1), 40),
        ('LEFTPADDING', (0,0), (-1,-1), 40),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        
    ]))

    story.append(footer)
    story.append(Spacer(1, 20))
    story.append(Paragraph("**Submit the form, along with the fee, to your house captain.", approved_style))
    story.append(Spacer(1, 60))
    story.append(Paragraph("<i>Organized by ITSRC Sports Committee</i>", subheader_style))

    # === Build PDF with Border + Watermark ===
    pdf.build(story, onFirstPage=draw_page_border_and_watermark, onLaterPages=draw_page_border_and_watermark)
    buffer.seek(0)

    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())

    return output_path








