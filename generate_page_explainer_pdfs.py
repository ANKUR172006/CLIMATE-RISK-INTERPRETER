from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT_DIR = Path("docs/page_explainers")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


PAGE_GUIDES = [
    {
        "filename": "01_Home_Page_Explained.pdf",
        "title": "Home Page Explained",
        "tagline": "Intro, definitions, workflow and quick snapshot",
        "sections": [
            (
                "Simple purpose",
                [
                    "Ye page onboarding page hai. Iska kaam user ko batana hai ki app kya karta hai, kis problem ko solve karta hai, aur next kis page par jana chahiye.",
                    "Yahan actual deep analysis nahi hota. Yahan orientation milti hai.",
                ],
            ),
            (
                "Main features",
                [
                    "Hero section: app ka naam aur main objective batata hai.",
                    "Why this prototype exists: problem framing aur key definitions deta hai.",
                    "Designed for: target users batata hai jaise planners, policy analysts, public-health teams.",
                    "What this tool enables: app ke possible outputs aur use-cases batata hai.",
                    "Climate Intelligence approach: explainable ML aur transparent logic ka summary deta hai.",
                    "Quick data snapshot: final-year anomaly, last 10-year mean, aur years analyzed jaisi quick metrics dikhata hai.",
                ],
            ),
            (
                "How it works",
                [
                    "CSV se yearly anomaly nikali jati hai.",
                    "1850-1900 ko baseline maana gaya hai.",
                    "Quick metrics same processed anomaly series se aati hain.",
                    "Page user ko batata hai ki actual detailed pages sidebar me hain.",
                ],
            ),
            (
                "Best line to explain",
                [
                    "Home page app ka intro aur map hai. Ye batata hai app kya hai, kyu bana hai, aur isse kaise use karna hai.",
                ],
            ),
        ],
    },
    {
        "filename": "02_Global_Trends_Explained.pdf",
        "title": "Global Trends Explained",
        "tagline": "Historical climate pattern and anomaly behavior",
        "sections": [
            (
                "Simple purpose",
                [
                    "Ye foundation analysis page hai. Ye historical climate archive ko samjhata hai aur batata hai ki temperature anomaly time ke saath kaise change hui.",
                ],
            ),
            (
                "Main features",
                [
                    "Exploration controls: year range aur trend/uncertainty toggles.",
                    "Historical baseline vs final observations: baseline aur archive-end comparison.",
                    "Main anomaly chart: observed anomaly, trend line aur uncertainty band.",
                    "Key signals: trend rate, final-year anomaly, years analyzed.",
                    "Rolling trend shift: moving window ke basis par trend ka slope kaise badla.",
                    "Decadal climate shift: decade-wise anomaly table.",
                    "Seasonal 3D surface: monthly seasonal structure ka visual pattern.",
                ],
            ),
            (
                "How it works",
                [
                    "CSV load hoti hai aur annual mean temperature banta hai.",
                    "1850-1900 ka average baseline liya jata hai.",
                    "Anomaly formula use hota hai: yearly temperature minus baseline.",
                    "Regression se trend line banti hai.",
                    "Bootstrap resampling se uncertainty band banti hai.",
                    "Rolling regression se trend shift detect hota hai.",
                ],
            ),
            (
                "ML or analytics",
                [
                    "Ye page mostly explainable statistical analytics use karta hai, full black-box ML nahi.",
                ],
            ),
            (
                "Best line to explain",
                [
                    "Global Trends page historical climate pattern ko clear karta hai. Ye app ka foundation hai.",
                ],
            ),
        ],
    },
    {
        "filename": "03_Regional_Risk_and_Policy_Explained.pdf",
        "title": "Regional Risk and Policy Explained",
        "tagline": "Signal to impact to action",
        "sections": [
            (
                "Simple purpose",
                [
                    "Ye page archive-based climate signal ko region-level meaning aur practical action me convert karta hai.",
                ],
            ),
            (
                "Main features",
                [
                    "Archive signal setup: horizon, model/manual rate, region selection.",
                    "Regional score: region multiplier, exposure, adaptive capacity aur regime factor se composite score.",
                    "Regional comparison chart: different regions ka relative score.",
                    "Human impact lens: health, food systems, infrastructure ke perspective se explanation.",
                    "Policy actions: urgency ke hisab se action suggestions.",
                    "GenAI summary: non-technical explanation generate karna.",
                ],
            ),
            (
                "How it works",
                [
                    "Climate signal ML engine se aata hai ya manual diya ja sakta hai.",
                    "Region multiplier batata hai ki selected region signal ko kaise amplify karega.",
                    "Exposure aur adaptive capacity se vulnerability estimate hoti hai.",
                    "Composite formula use hota hai: regional signal x exposure x (1 - adaptive capacity) x regime factor.",
                    "Uske baad score ko simple impact aur action guidance me convert kiya jata hai.",
                ],
            ),
            (
                "ML usage",
                [
                    "Yahan full ML training page par nahi hoti, but ML-derived signal aur regime output use hote hain.",
                ],
            ),
            (
                "Best line to explain",
                [
                    "Ye page signal se action tak ka bridge hai.",
                ],
            ),
        ],
    },
    {
        "filename": "04_Scenario_Explorer_Explained.pdf",
        "title": "Scenario Explorer Explained",
        "tagline": "What-if analysis with uncertainty",
        "sections": [
            (
                "Simple purpose",
                [
                    "Ye page what-if tool hai. User assumptions change karke possible outcome range dekh sakta hai.",
                ],
            ),
            (
                "Main features",
                [
                    "Assumed extrapolated rate: expected rate define karna.",
                    "Rate uncertainty: variation kitni ho sakti hai.",
                    "Years beyond archive end: kitna aage illustrative dekhna hai.",
                    "Number of simulations: kitni runs karni hain.",
                    "Percentiles: P10, median, P90.",
                    "Histogram: possible outcomes ka spread.",
                    "Threshold message: lower, higher ya severe-type range ka quick reading.",
                ],
            ),
            (
                "How it works",
                [
                    "User input ke basis par multiple simulated rates banti hain.",
                    "Har simulation ek possible outcome deti hai.",
                    "Sab simulations ko combine karke distribution milta hai.",
                    "Page ek single answer nahi deta, range deta hai.",
                ],
            ),
            (
                "ML usage",
                [
                    "Ye proper ML page nahi hai. Ye simulation-based uncertainty page hai.",
                ],
            ),
            (
                "Best line to explain",
                [
                    "Scenario Explorer future ko fix karke nahi batata, possible range dikhata hai.",
                ],
            ),
        ],
    },
    {
        "filename": "05_Climate_Risk_Pulse_Explained.pdf",
        "title": "Climate Risk Pulse Explained",
        "tagline": "Signal triage: turning points, drivers and era comparison",
        "sections": [
            (
                "Simple purpose",
                [
                    "Ye page simple summary nahi hai. Ye signal triage page hai jo batata hai signal kab sharply badla, kyu badla, aur kaunsa historical era stronger tha.",
                ],
            ),
            (
                "Main features",
                [
                    "Pulse controls: rolling window, volatility weight, acceleration weight.",
                    "Pulse timeline: pulse index ka time-based chart.",
                    "Turning-point detector: top years jahan pulse sharply change hua.",
                    "Component-driver breakdown: selected turning year me mean level, volatility, aur acceleration ka role.",
                    "Era comparison: 1750-1799, 1800-1849, 1850-1900 ka comparison.",
                    "Quick read: archive-end pulse ka short interpretation.",
                ],
            ),
            (
                "How it works",
                [
                    "Anomaly series se rolling mean, rolling volatility aur acceleration nikali jati hai.",
                    "In components ko normalize karke pulse score banaya jata hai.",
                    "Pulse me strongest changes ko turning-point detector pick karta hai.",
                    "Selected year ke liye page dikha deta hai ki pulse driver kya tha.",
                    "Era comparison se alag historical periods ka pulse behavior compare hota hai.",
                ],
            ),
            (
                "Why this page is innovative",
                [
                    "Ye sirf trend repeat nahi karta.",
                    "Ye diagnostic page hai: when did the signal turn, what drove it, and how do eras compare.",
                ],
            ),
            (
                "Best line to explain",
                [
                    "Risk Pulse page climate signal ko diagnose karta hai, sirf summarize nahi.",
                ],
            ),
        ],
    },
    {
        "filename": "06_Climate_Intelligence_Engine_Explained.pdf",
        "title": "Climate Intelligence Engine Explained",
        "tagline": "Advanced ML and GenAI workbench",
        "sections": [
            (
                "Simple purpose",
                [
                    "Ye app ka advanced technical page hai. Iska kaam results ke peeche ka ML aur AI logic dikhana hai.",
                ],
            ),
            (
                "Main features",
                [
                    "Controls: lag features, holdout years, extrapolation horizon, uncertainty simulations.",
                    "Executive KPI strip: best model, RMSE, final archive regime, illustrative anomaly, confidence.",
                    "Holdout performance: observed vs predicted comparison.",
                    "Model explainability: feature importance.",
                    "Extrapolation with uncertainty: archive signal aur post-1900 illustrative band.",
                    "Risk-regime detection: lower, elevated, high categories.",
                    "AI narrative summary: readable model summary.",
                    "GenAI studio: policy brief, executive summary, public message.",
                    "Ask GenAI: analysis context se Q and A.",
                ],
            ),
            (
                "How it works",
                [
                    "Anomaly series se supervised dataset banta hai.",
                    "Lag features aur rolling features create hote hain.",
                    "Multiple models train aur compare hote hain.",
                    "Best model RMSE and other metrics ke basis par choose hota hai.",
                    "Residual bootstrap se uncertainty band banti hai.",
                    "KMeans regime detection se archive states label hote hain.",
                    "GenAI layer model outputs ko stakeholder-ready text me convert karti hai.",
                ],
            ),
            (
                "ML usage",
                [
                    "Proper ML training isi page me strongest form me hoti hai.",
                ],
            ),
            (
                "Best line to explain",
                [
                    "Baaki pages result dikhate hain, Climate Intelligence Engine result ke peeche ka intelligence dikhata hai.",
                ],
            ),
        ],
    },
]


def build_pdf(guide: dict) -> None:
    output_path = OUTPUT_DIR / guide["filename"]
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=colors.HexColor("#123c52"),
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
        spaceBefore=8,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.black,
        spaceAfter=5,
    )

    story = [
        Paragraph(guide["title"], title_style),
        Paragraph(guide["tagline"], subtitle_style),
    ]

    for heading, points in guide["sections"]:
        story.append(Paragraph(heading, heading_style))
        for point in points:
            story.append(Paragraph(f"- {point}", body_style))
        story.append(Spacer(1, 6))

    summary_table = Table(
        [
            ["Use case", "Team explanation handover"],
            ["Language style", "Desi / simple Roman Hindi"],
            ["Prototype type", "Climate interpretation prototype"],
        ],
        colWidths=[5.0 * cm, 10.5 * cm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    doc.build(story)


def main() -> None:
    for guide in PAGE_GUIDES:
        build_pdf(guide)
    print(f"Generated {len(PAGE_GUIDES)} PDFs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
