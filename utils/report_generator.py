"""
PDF report generator using ReportLab.
"""

import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Colour palette ─────────────────────────────────────────────────────────────
DARK_BG     = colors.HexColor("#0f172a")
ACCENT      = colors.HexColor("#6366f1")
ACCENT_LITE = colors.HexColor("#818cf8")
CARD_BG     = colors.HexColor("#1e293b")
TEXT_MAIN   = colors.HexColor("#f1f5f9")
TEXT_MUTED  = colors.HexColor("#94a3b8")
SUCCESS     = colors.HexColor("#22c55e")
WARNING     = colors.HexColor("#f59e0b")
DANGER      = colors.HexColor("#ef4444")


def _score_color(score: float):
    if score >= 80:
        return SUCCESS
    if score >= 60:
        return WARNING
    return DANGER


def generate_report(analysis: dict, output_path: str) -> str:
    """
    Build a multi-page PDF report and save to output_path.
    Returns output_path on success.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles  = getSampleStyleSheet()
    W, H    = A4
    usable  = W - 4*cm

    # ── Custom styles ──────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title2", parent=styles["Title"],
        fontSize=26, textColor=TEXT_MAIN, backColor=DARK_BG,
        spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold",
    )
    h1 = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=14, textColor=ACCENT_LITE, spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body = ParagraphStyle(
        "Body2", parent=styles["BodyText"],
        fontSize=10, textColor=TEXT_MAIN, leading=14, spaceAfter=4,
    )
    muted = ParagraphStyle(
        "Muted", parent=body, textColor=TEXT_MUTED, fontSize=9,
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=body, leftIndent=12, bulletIndent=0,
        spaceBefore=2, spaceAfter=2,
    )

    story = []

    # ── Header ─────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("AI Resume Analyzer", title_style),
    ]]
    header_table = Table(header_data, colWidths=[usable])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
        ("TOPPADDING",  (0,0), (-1,-1), 16),
        ("BOTTOMPADDING", (0,0), (-1,-1), 16),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # Candidate info
    parsed     = analysis.get("parsed", {})
    ats        = analysis.get("ats", {})
    pred       = analysis.get("prediction", {})
    summary    = analysis.get("summary", "")
    feedback   = analysis.get("feedback", [])
    int_tips   = analysis.get("interview_tips", [])
    generated  = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

    info_rows = [
        ["Candidate", parsed.get("name", "—")],
        ["Email",     parsed.get("email", "—")],
        ["Phone",     parsed.get("phone", "—")],
        ["Generated", generated],
    ]
    info_table = Table(info_rows, colWidths=[3*cm, usable-3*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), CARD_BG),
        ("TEXTCOLOR",    (0,0), (0,-1), TEXT_MUTED),
        ("TEXTCOLOR",    (1,0), (1,-1), TEXT_MAIN),
        ("FONTNAME",     (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [CARD_BG, colors.HexColor("#263245")]),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.6*cm))

    # ── ATS Score card ─────────────────────────────────────────────────────────
    score      = ats.get("total_score", 0)
    rating     = ats.get("rating", "—")
    role       = pred.get("predicted_role", "—")
    confidence = pred.get("confidence", 0)
    sc_color   = _score_color(score)

    story.append(Paragraph("ATS Analysis", h1))
    story.append(HRFlowable(width=usable, color=ACCENT, thickness=1))
    story.append(Spacer(1, 0.3*cm))

    score_rows = [
        ["ATS Score",       f"{score} / 100"],
        ["Rating",          rating],
        ["Predicted Role",  role],
        ["Confidence",      f"{confidence}%"],
    ]
    score_table = Table(score_rows, colWidths=[usable*0.45, usable*0.55])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), CARD_BG),
        ("TEXTCOLOR",    (0,0), (0,-1), TEXT_MUTED),
        ("TEXTCOLOR",    (1,0), (1,-1), TEXT_MAIN),
        ("FONTNAME",     (1,0), (1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (1,0), (1,0),  18),
        ("TEXTCOLOR",    (1,0), (1,0),  sc_color),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[CARD_BG, colors.HexColor("#263245")]),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.4*cm))

    # Score components
    comps = ats.get("components", {})
    comp_rows = [["Component", "Score"]] + [
        [k.title(), f"{v} / 100"] for k, v in comps.items()
    ]
    comp_table = Table(comp_rows, colWidths=[usable*0.6, usable*0.4])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), ACCENT),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND",   (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR",    (0,1), (-1,-1), TEXT_MAIN),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[CARD_BG, colors.HexColor("#263245")]),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#334155")),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Skills ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("Detected Skills", h1))
    story.append(HRFlowable(width=usable, color=ACCENT, thickness=1))
    story.append(Spacer(1, 0.3*cm))

    skills_by_cat = parsed.get("skills_by_category", {})
    if skills_by_cat:
        for cat, skills in skills_by_cat.items():
            story.append(Paragraph(f"<b>{cat}</b>", ParagraphStyle(
                "CatTitle", parent=muted, textColor=ACCENT_LITE, fontSize=9,
            )))
            story.append(Paragraph(", ".join(skills), body))
            story.append(Spacer(1, 0.1*cm))
    else:
        story.append(Paragraph("No structured skills detected.", muted))

    story.append(Spacer(1, 0.4*cm))

    # ── Missing Skills ─────────────────────────────────────────────────────────
    missing = ats.get("missing_skills", [])
    if missing:
        story.append(Paragraph("Missing Skills", h1))
        story.append(HRFlowable(width=usable, color=DANGER, thickness=1))
        story.append(Spacer(1, 0.3*cm))
        for s in missing:
            story.append(Paragraph(f"• {s}", bullet_style))
        story.append(Spacer(1, 0.4*cm))

    # ── Summary ────────────────────────────────────────────────────────────────
    if summary:
        story.append(Paragraph("Professional Summary", h1))
        story.append(HRFlowable(width=usable, color=ACCENT, thickness=1))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(summary, body))
        story.append(Spacer(1, 0.4*cm))

    # ── AI Feedback ────────────────────────────────────────────────────────────
    if feedback:
        story.append(Paragraph("AI Improvement Suggestions", h1))
        story.append(HRFlowable(width=usable, color=ACCENT, thickness=1))
        story.append(Spacer(1, 0.3*cm))
        for i, tip in enumerate(feedback, 1):
            story.append(Paragraph(f"{i}. {tip}", bullet_style))
        story.append(Spacer(1, 0.4*cm))

    # ── Interview Tips ─────────────────────────────────────────────────────────
    if int_tips:
        story.append(Paragraph("Interview Preparation Tips", h1))
        story.append(HRFlowable(width=usable, color=SUCCESS, thickness=1))
        story.append(Spacer(1, 0.3*cm))
        for i, tip in enumerate(int_tips, 1):
            story.append(Paragraph(f"{i}. {tip}", bullet_style))

    doc.build(story)
    return output_path
