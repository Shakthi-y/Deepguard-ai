"""Report Agent — generates a downloadable PDF report of the analysis."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.config import settings

VERDICT_COLORS = {
    "LIKELY REAL": colors.HexColor("#22c55e"),
    "LIKELY FAKE": colors.HexColor("#ef4444"),
    "UNCERTAIN": colors.HexColor("#eab308"),
}


def generate_pdf(analysis: dict) -> str:
    out_path = settings.REPORT_DIR / f"{analysis['id']}.pdf"
    doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                             topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#0ea5e9"))
    h2 = ParagraphStyle("H2X", parent=styles["Heading2"], spaceBefore=12)
    body = styles["BodyText"]

    verdict = analysis["verdict"]
    v_color = VERDICT_COLORS.get(verdict, colors.grey)

    story = []
    story.append(Paragraph("DeepGuard AI — Analysis Report", title_style))
    story.append(Paragraph("An Agentic AI System for Intelligent Image Authenticity Verification", body))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#334155")))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Report ID: {analysis['id']}", body))
    story.append(Paragraph(f"File: {analysis['filename']}", body))
    story.append(Paragraph(f"Timestamp: {analysis['timestamp']}", body))
    story.append(Spacer(1, 10))

    verdict_style = ParagraphStyle("Verdict", parent=styles["Heading1"], textColor=v_color)
    story.append(Paragraph(f"VERDICT: {verdict}", verdict_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Detection Agent (model2_skincare.h5)", h2))
    det = analysis["detection"]
    det_table = Table([
        ["Real probability", f"{det['real_probability']*100:.1f}%"],
        ["Fake probability", f"{det['fake_probability']*100:.1f}%"],
        ["Predicted label", det["predicted_label"]],
        ["Model confidence", f"{det['model_confidence']*100:.1f}%"],
        ["Decision threshold", str(det["threshold_used"])],
    ], colWidths=[180, 250])
    det_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(det_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Forensic Analysis Agent", h2))
    for_ = analysis["forensic"]
    for_table = Table([
        ["MIME type", for_["mime_type"]],
        ["Dimensions", for_["dimensions"]],
        ["Format", for_["format"]],
        ["File size", f"{for_['file_size_kb']} KB"],
        ["EXIF present", "Yes" if for_["has_exif"] else "No"],
        ["Compression estimate", for_["estimated_compression"]],
    ], colWidths=[180, 250])
    for_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(for_table)
    if for_["flags"]:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Flags: " + "; ".join(for_["flags"]), body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Verification & Confidence", h2))
    ver = analysis["verification"]
    conf = analysis["confidence"]
    story.append(Paragraph(f"Reasoning: {ver['reasoning']}", body))
    story.append(Paragraph(
        f"Model confidence: {conf['model_confidence']*100:.1f}% | "
        f"System confidence: {conf['system_confidence']*100:.1f}% ({conf['confidence_band']})", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("AI Explanation", h2))
    story.append(Paragraph(analysis["explanation"], body))
    story.append(Spacer(1, 14))

    story.append(HRFlowable(width="100%", color=colors.HexColor("#334155")))
    disc_style = ParagraphStyle("Disc", parent=styles["Italic"], fontSize=8, textColor=colors.HexColor("#64748b"))
    story.append(Paragraph(analysis["disclaimer"], disc_style))

    doc.build(story)
    return str(out_path)
