from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line


OUTPUT_PATH = Path("docs/page_explainers/08_Team_Handover_Master.pdf")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def flow_box(drawing, x, y, w, h, text, fill="#e0f2fe", stroke="#0369a1", font_size=9):
    drawing.add(
        Rect(
            x,
            y,
            w,
            h,
            rx=8,
            ry=8,
            fillColor=colors.HexColor(fill),
            strokeColor=colors.HexColor(stroke),
            strokeWidth=1.2,
        )
    )
    lines = text.split("\n")
    total_h = len(lines) * (font_size + 2)
    start_y = y + (h / 2) + (total_h / 2) - font_size
    for i, line in enumerate(lines):
        line_w = stringWidth(line, "Helvetica-Bold", font_size)
        drawing.add(
            String(
                x + (w - line_w) / 2,
                start_y - i * (font_size + 2),
                line,
                fontName="Helvetica-Bold",
                fontSize=font_size,
                fillColor=colors.HexColor("#0f172a"),
            )
        )


def arrow(drawing, x1, y1, x2, y2):
    drawing.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor("#475569"), strokeWidth=1.5))
    drawing.add(Line(x2, y2, x2 - 5, y2 + 3, strokeColor=colors.HexColor("#475569"), strokeWidth=1.5))
    drawing.add(Line(x2, y2, x2 - 5, y2 - 3, strokeColor=colors.HexColor("#475569"), strokeWidth=1.5))


def add_bullets(story, items, style):
    for item in items:
        story.append(Paragraph(f"- {item}", style))
    story.append(Spacer(1, 6))


def build_flow_diagram():
    d = Drawing(520, 120)
    labels = [
        "Problem",
        "Data\n+ Baseline",
        "Analysis",
        "Regional\nMeaning",
        "Action",
        "AI/ML\nProof",
    ]
    x = 5
    boxes = []
    for label in labels:
        boxes.append((x, 35, 75, 42))
        flow_box(d, x, 35, 75, 42, label)
        x += 85
    for i in range(len(boxes) - 1):
        x1, y1, w1, h1 = boxes[i]
        x2, y2, w2, h2 = boxes[i + 1]
        arrow(d, x1 + w1, y1 + h1 / 2, x2, y2 + h2 / 2)
    return d


def build_page_map_diagram():
    d = Drawing(520, 220)
    top = [
        (25, 150, 110, 42, "Home"),
        (155, 150, 110, 42, "Global Trends"),
        (285, 150, 110, 42, "Regional Risk\nand Policy"),
        (415, 150, 90, 42, "Scenario\nExplorer"),
    ]
    bottom = [
        (115, 55, 130, 42, "Climate Risk Pulse"),
        (285, 55, 160, 42, "Climate Intelligence\nEngine"),
    ]
    for x, y, w, h, label in top:
        flow_box(d, x, y, w, h, label, fill="#ecfccb", stroke="#4d7c0f")
    for x, y, w, h, label in bottom:
        flow_box(d, x, y, w, h, label, fill="#ede9fe", stroke="#6d28d9")
    arrow(d, 80, 150, 80, 100)
    arrow(d, 210, 150, 180, 100)
    arrow(d, 340, 150, 350, 100)
    arrow(d, 455, 150, 350, 100)
    return d


def build_ml_diagram():
    d = Drawing(520, 180)
    flow_box(d, 10, 70, 90, 45, "CSV Data", fill="#fee2e2", stroke="#b91c1c")
    flow_box(d, 115, 70, 90, 45, "Annual\nAnomaly", fill="#fef3c7", stroke="#b45309")
    flow_box(d, 220, 70, 90, 45, "Features", fill="#dcfce7", stroke="#15803d")
    flow_box(d, 325, 70, 90, 45, "Models", fill="#dbeafe", stroke="#1d4ed8")
    flow_box(d, 430, 70, 80, 45, "Best\nModel", fill="#ede9fe", stroke="#7c3aed")
    arrow(d, 100, 92, 115, 92)
    arrow(d, 205, 92, 220, 92)
    arrow(d, 310, 92, 325, 92)
    arrow(d, 415, 92, 430, 92)
    flow_box(d, 145, 10, 120, 35, "Holdout Test + RMSE", fill="#f8fafc", stroke="#334155")
    flow_box(d, 285, 10, 140, 35, "Uncertainty + Regimes", fill="#f8fafc", stroke="#334155")
    arrow(d, 370, 70, 350, 45)
    arrow(d, 265, 70, 205, 45)
    return d


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#123c52"),
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.4,
        leading=14.5,
        textColor=colors.black,
        spaceAfter=4,
    )

    story = [
        Paragraph("Team Handover Master", title_style),
        Paragraph(
            "Problem statement se lekar prototype flow, page explanations, ML understanding, limitations, and team speaking support.",
            subtitle_style,
        ),
        Paragraph("1. Big Picture Flow", heading_style),
        build_flow_diagram(),
        Spacer(1, 8),
    ]

    add_bullets(
        story,
        [
            "Problem: climate data available hai but interpretation difficult hai.",
            "Data + Baseline: dataset 1750-1900, baseline 1850-1900.",
            "Analysis: anomaly, trend, uncertainty, diagnostics.",
            "Regional Meaning: region-level score and impact lens.",
            "Action: urgency and planning guidance.",
            "AI/ML Proof: advanced workbench jo modeling aur explainability dikhata hai.",
        ],
        body_style,
    )

    story.append(Paragraph("2. Problem Statement", heading_style))
    add_bullets(
        story,
        [
            "Climate data bahut available hai, but normal users usse decision-friendly meaning nahi nikal pate.",
            "Sirf charts enough nahi hote. Trend, uncertainty, impact aur action samajhna zaroori hota hai.",
            "So real problem was interpretation, not data availability.",
        ],
        body_style,
    )

    story.append(Paragraph("3. What We Had To Build", heading_style))
    add_bullets(
        story,
        [
            "Historical climate data ko understandable signals me convert karna.",
            "Trend aur uncertainty dikhani.",
            "Region-level interpretation deni.",
            "Policy-style action guidance deni.",
            "Advanced level par ML and AI-backed explanation support karna.",
        ],
        body_style,
    )

    story.append(Paragraph("4. What We Built", heading_style))
    story.append(build_page_map_diagram())
    story.append(Spacer(1, 8))
    add_bullets(
        story,
        [
            "Home: intro and orientation.",
            "Global Trends: historical climate pattern.",
            "Regional Risk and Policy: signal to impact to action.",
            "Scenario Explorer: what-if uncertainty view.",
            "Climate Risk Pulse: signal triage and turning-point diagnosis.",
            "Climate Intelligence Engine: advanced ML and GenAI workbench.",
        ],
        body_style,
    )

    story.append(Paragraph("5. Data and Baseline", heading_style))
    data_table = Table(
        [
            ["Item", "Value"],
            ["Observed dataset", "1750 to 1900"],
            ["Total years", "151"],
            ["Baseline", "1850 to 1900 mean"],
            ["Anomaly formula", "Yearly temperature minus baseline"],
            ["Important limitation", "Post-1900 values are illustrative extrapolations, not observed data"],
        ],
        colWidths=[5.0 * cm, 10.5 * cm],
    )
    data_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#93c5fd")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(data_table)

    story.append(PageBreak())
    story.append(Paragraph("6. Page Explanations", heading_style))

    page_rows = [
        ["Page", "Simple purpose", "Best one-line explanation"],
        ["Home", "Intro and definitions", "Home page app ka intro aur map hai."],
        ["Global Trends", "Historical trend foundation", "Ye page historical climate pattern ko clear karta hai."],
        ["Regional Risk and Policy", "Signal to impact to action", "Ye page signal se action tak ka bridge hai."],
        ["Scenario Explorer", "What-if range exploration", "Ye exact prediction nahi, possible range dikhata hai."],
        ["Climate Risk Pulse", "Signal triage and turning points", "Ye signal ko diagnose karta hai, sirf summarize nahi."],
        ["Climate Intelligence Engine", "Advanced modeling proof", "Baaki pages result dikhate hain, ye intelligence dikhata hai."],
    ]
    page_table = Table(page_rows, colWidths=[4.2 * cm, 5.8 * cm, 5.5 * cm])
    page_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcfce7")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#86efac")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(page_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("7. ML Flow", heading_style))
    story.append(build_ml_diagram())
    story.append(Spacer(1, 8))
    add_bullets(
        story,
        [
            "CSV data se annual anomaly banti hai.",
            "Anomaly series se lag, rolling mean, rolling std, trend aur momentum features bante hain.",
            "Multiple models train hote hain: Ridge, ElasticNet, RandomForest, GradientBoosting.",
            "Best model cross-validation plus holdout test se choose hota hai.",
            "Residual bootstrap se uncertainty aati hai.",
            "KMeans se risk regimes detect hote hain.",
        ],
        body_style,
    )

    story.append(Paragraph("8. Important ML Terms in Simple Language", heading_style))
    add_bullets(
        story,
        [
            "Lag features: past values jinko model dekhkar next pattern samajhta hai.",
            "Holdout years: testing ke liye side me rakha gaya data.",
            "RMSE: model kitni galti kar raha hai.",
            "Extrapolation: existing pattern ko aage extend karke estimate banana.",
            "Risk regime detection: data ko Lower, Elevated, High-type states me divide karna.",
            "Explainability: model ne kis basis par decision liya, uska proof.",
        ],
        body_style,
    )

    story.append(PageBreak())
    story.append(Paragraph("9. Likely Questions Team Must Handle", heading_style))
    qa_table = Table(
        [
            ["Question", "Strong answer"],
            ["Dataset 1900 tak hi kyu?", "Current prototype historical archive par based hai. Post-1900 outputs illustrative extrapolations hain."],
            ["ML kahan use hua?", "Strongest ML use Climate Intelligence Engine me hai. Other pages ML-supported ya analytics-based hain."],
            ["Scenario Explorer ML hai?", "Nahi, wo simulation-based what-if page hai."],
            ["Risk Pulse alag kya karta hai?", "Turning points, component drivers, aur era comparison dikhata hai."],
            ["Engine public ko kyu dikhana?", "Wo trust and transparency page hai, public-first page nahi."],
            ["Innovation kya hai?", "Raw climate archive ko explainable signal, regional meaning, action guidance, and AI-backed communication me convert karna."],
        ],
        colWidths=[5.0 * cm, 10.5 * cm],
    )
    qa_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fee2e2")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#fca5a5")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(qa_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("10. Best Final Summary to Speak", heading_style))
    add_bullets(
        story,
        [
            "Humara prototype raw climate data ko understandable climate intelligence me convert karta hai.",
            "Flow simple-to-advanced hai: intro, trends, regional meaning, scenarios, signal triage, and advanced ML proof.",
            "Humne explainable logic, uncertainty, regional interpretation, and AI communication ko combine kiya hai.",
            "Main limitation ye hai ki observed dataset 1900 tak hai, isliye later values illustrative extrapolations hain.",
        ],
        body_style,
    )

    doc.build(story)
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
