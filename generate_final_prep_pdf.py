from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT_PATH = Path("docs/page_explainers/09_Final_Preparation_Complete.pdf")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def add_bullets(story, items, style):
    for item in items:
        story.append(Paragraph(f"- {item}", style))
    story.append(Spacer(1, 6))


def add_table(story, rows, widths, header_bg, grid):
    table = Table(rows, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor(grid)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8))


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=1.35 * cm,
        leftMargin=1.35 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm,
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
        fontSize=12.8,
        leading=16.5,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=7,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.9,
        leading=13.5,
        textColor=colors.black,
        spaceAfter=4,
    )

    story = [
        Paragraph("Final Preparation Complete Pack", title_style),
        Paragraph(
            "Complete viva and final-demo preparation guide for the climate prototype: overview, structure, page flow, logic, ML explanation, limitations, concrete values, and mentor Q&A.",
            subtitle_style,
        ),
    ]

    story.append(Paragraph("1. Where the PDF is", heading_style))
    add_bullets(
        story,
        [
            "Previous handover PDF: docs/page_explainers/08_Team_Handover_Master.pdf",
            "This complete final-prep PDF: docs/page_explainers/09_Final_Preparation_Complete.pdf",
            "This file is the longer version meant for your final preparation.",
        ],
        body_style,
    )

    story.append(Paragraph("2. One-line prototype explanation", heading_style))
    add_bullets(
        story,
        [
            "This prototype converts a historical global temperature archive into explainable climate signals, regional risk interpretation, uncertainty-aware scenarios, and stakeholder-ready summaries.",
            "Short line to memorize: We are not just showing climate data, we are translating climate history into decision-friendly intelligence.",
        ],
        body_style,
    )

    story.append(Paragraph("3. Problem statement", heading_style))
    add_bullets(
        story,
        [
            "Climate data is available, but interpretation is hard for non-technical users.",
            "Users often see charts but cannot convert them into risk, urgency, or action.",
            "The problem is not data collection only; the real problem is readable, responsible interpretation.",
            "Our prototype addresses that by connecting signal, uncertainty, regional meaning, and action guidance.",
        ],
        body_style,
    )

    story.append(Paragraph("4. Current project structure", heading_style))
    add_table(
        story,
        [
            ["Part", "File", "Role"],
            ["Home", "app.py", "Entry page, problem framing, workflow, quick metrics"],
            ["Global Trends", "pages/1_Global_Trends.py", "Historical anomaly analysis, regression, bootstrap uncertainty, decadal view"],
            ["Regional Risk and Policy", "pages/3_Regional_Risk.py", "Regional scoring, exposure logic, impact lens, actions, GenAI summary"],
            ["Scenario Explorer", "pages/4_Scenario_Explorer.py", "Monte Carlo what-if simulation"],
            ["Climate Risk Pulse", "pages/6_Risk_pulse.py", "Turning points, pulse score, driver diagnosis, era comparison"],
            ["Climate Intelligence Engine", "pages/7_Climate_Intelligence_Engine.py", "Full ML training, holdout evaluation, uncertainty, regimes, GenAI"],
            ["ML layer", "ml_engine.py", "Data prep, feature engineering, model training, forecast, clustering"],
            ["GenAI layer", "genai_engine.py", "LLM provider routing and fallback brief generation"],
        ],
        [3.4 * cm, 5.4 * cm, 8.3 * cm],
        "#dbeafe",
        "#93c5fd",
    )

    story.append(Paragraph("5. End-to-end system flow", heading_style))
    add_bullets(
        story,
        [
            "Step 1: Load GlobalTemperatures.csv.",
            "Step 2: Parse dt column into dates and remove invalid rows.",
            "Step 3: Resample monthly values into yearly average temperature.",
            "Step 4: Compute baseline using 1850-1900 average.",
            "Step 5: Convert yearly temperatures into anomaly series.",
            "Step 6: Use anomaly series in analytics pages and ML engine.",
            "Step 7: Build features from history such as lags, rolling means, rolling standard deviations, trend, and momentum.",
            "Step 8: Train and compare multiple models.",
            "Step 9: Select best model using time-aware validation.",
            "Step 10: Build extrapolation ranges and risk regimes.",
            "Step 11: Translate model outputs into regional and policy-friendly summaries.",
        ],
        body_style,
    )

    story.append(Paragraph("6. Core dataset facts", heading_style))
    add_table(
        story,
        [
            ["Metric", "Value", "How to explain it"],
            ["Observed archive start", "1750", "The historical record used in this prototype starts in 1750."],
            ["Observed archive end", "1900", "This is the most important limitation. Observed data ends at 1900."],
            ["Years analyzed", "151", "After cleaning and yearly aggregation, 151 annual points are used."],
            ["Baseline", "1850-1900 mean", "All anomaly values are relative to this reference period."],
            ["Trend rate", "0.1856 C per decade", "This is the long-run fitted trend over the anomaly series."],
            ["Final anomaly", "-1.7924 C", "Final archive-year anomaly relative to the selected baseline."],
            ["Last 10-year mean anomaly", "-0.1478 C", "Average anomaly over the last 10 archive years."],
        ],
        [3.8 * cm, 3.6 * cm, 9.7 * cm],
        "#fef3c7",
        "#fcd34d",
    )

    story.append(Paragraph("7. Important honesty point", heading_style))
    add_bullets(
        story,
        [
            "Observed data stops at 1900.",
            "So any value beyond 1900 in the app is not observed climate data.",
            "Those values are illustrative model extrapolations from the historical archive.",
            "If a mentor asks for the main limitation, say this first.",
        ],
        body_style,
    )

    story.append(Paragraph("8. Home page explanation", heading_style))
    add_bullets(
        story,
        [
            "This page introduces the problem, defines trend, risk signal, and local implication, and gives a workflow for how to use the app.",
            "It also gives a quick data snapshot so the user immediately sees the scale of the archive.",
            "Best line: The Home page is the orientation layer. It tells users what the system does and how to navigate the analysis.",
        ],
        body_style,
    )

    story.append(Paragraph("9. Global Trends page explanation", heading_style))
    add_bullets(
        story,
        [
            "This page establishes the historical foundation.",
            "It loads the dataset, computes yearly anomaly, and shows the long-term temperature pattern.",
            "The trend line comes from linear regression using numpy polyfit.",
            "The uncertainty band comes from bootstrap resampling of the trend fit.",
            "Rolling trend shift uses windowed regression to show how the slope changes over time.",
            "Decadal climate shift reduces noise and highlights structural movement across decades.",
            "The 3D seasonal surface shows how seasonality behaves over years and months.",
            "Best line: This page proves the historical signal before we translate it into risk and action.",
        ],
        body_style,
    )

    story.append(Paragraph("10. Regional Risk and Policy page explanation", heading_style))
    add_bullets(
        story,
        [
            "This page converts the climate signal into regional meaning.",
            "The user chooses horizon, region, and whether to use a model-estimated rate or a manual rate.",
            "The app applies region multipliers, exposure factors, adaptive capacity, and final regime factor.",
            "Composite formula: Regional signal x Exposure x (1 - Adaptive capacity) x Regime factor.",
            "The page then maps that score into impact language and policy urgency.",
            "This is not a fully validated regional climate model. It is an interpretable decision-support layer built on archive-based signal logic.",
            "Best line: This page is the bridge from data signal to human and policy meaning.",
        ],
        body_style,
    )

    story.append(Paragraph("11. Scenario Explorer explanation", heading_style))
    add_bullets(
        story,
        [
            "This page is a what-if simulator, not a supervised ML page.",
            "The user sets assumed warming rate, uncertainty range, years forward, and number of simulations.",
            "The app samples many possible rates using a normal distribution and converts them into projected anomaly change.",
            "It reports P10, P50, and P90 to show a plausible range rather than one fixed number.",
            "Best line: Scenario Explorer does not predict one future; it shows a range of possible outcomes from chosen assumptions.",
        ],
        body_style,
    )

    story.append(Paragraph("12. Climate Risk Pulse explanation", heading_style))
    add_bullets(
        story,
        [
            "This page is a diagnostic or triage page.",
            "It computes rolling mean, rolling standard deviation, trend rate, and acceleration from the anomaly series.",
            "These are normalized and combined into a pulse index from 0 to 100.",
            "Turning-point detection identifies years where the pulse changed most sharply.",
            "Driver breakdown shows whether level, volatility, or acceleration contributed most.",
            "Era comparison lets us compare historical periods instead of only the final years.",
            "Best line: This page diagnoses when the climate signal changed and why, not just how high it is.",
        ],
        body_style,
    )

    story.append(Paragraph("13. Climate Intelligence Engine explanation", heading_style))
    add_bullets(
        story,
        [
            "This is the technical proof layer of the prototype.",
            "It builds the supervised dataset, trains multiple models, evaluates them on holdout years, estimates uncertainty, and detects regimes.",
            "It also generates AI-ready summaries so the outputs can be communicated to different audiences.",
            "Basic mode is for summary-level viewing. Expert mode exposes holdout performance, feature importance, and risk-regime charts.",
            "Best line: Other pages show results; this page shows the intelligence and validation behind the results.",
        ],
        body_style,
    )

    story.append(Paragraph("14. ML pipeline details", heading_style))
    add_table(
        story,
        [
            ["Step", "Implementation", "Why it matters"],
            ["Data loading", "load_annual_anomaly()", "Creates a clean annual anomaly series from the CSV"],
            ["Feature engineering", "lags, rolling_mean_5, rolling_std_5, rolling_mean_10, rolling_std_10, trend_10, momentum_3", "Transforms raw series into learnable inputs"],
            ["Train/test split", "Last test_years reserved as holdout", "Keeps final evaluation fair"],
            ["Cross-validation", "TimeSeriesSplit", "Respects time order instead of random shuffling"],
            ["Candidate models", "Ridge, ElasticNet, RandomForest, GradientBoosting", "Compares linear and non-linear approaches"],
            ["Selection logic", "0.6 x CV RMSE + 0.4 x holdout RMSE", "Systematic best-model choice"],
            ["Uncertainty", "Residual bootstrap simulations", "Produces P10/P50/P90 ranges"],
            ["Regime detection", "KMeans clustering", "Turns behavior into Lower, Elevated, High states"],
        ],
        [2.6 * cm, 7.0 * cm, 7.2 * cm],
        "#dcfce7",
        "#86efac",
    )

    story.append(Paragraph("15. Features in plain language", heading_style))
    add_table(
        story,
        [
            ["Feature", "Meaning", "Why useful"],
            ["lag_1 to lag_8", "Recent past anomaly values", "Model learns from recent history"],
            ["rolling_mean_5", "Short-term average", "Captures recent level"],
            ["rolling_std_5", "Short-term variability", "Captures recent instability"],
            ["rolling_mean_10", "Medium-term average", "Captures broader local context"],
            ["rolling_std_10", "Medium-term variability", "Shows whether the series became more unstable"],
            ["trend_10", "Slope over recent 10 values", "Captures direction and pace"],
            ["momentum_3", "Latest value against short recent average", "Captures recent push or slowdown"],
        ],
        [3.4 * cm, 5.8 * cm, 7.6 * cm],
        "#ede9fe",
        "#c4b5fd",
    )

    story.append(Paragraph("16. Actual model comparison from this project", heading_style))
    add_table(
        story,
        [
            ["Model", "CV RMSE", "Holdout RMSE", "MAE", "R2", "Interpretation"],
            ["Ridge", "Extremely unstable", "0.4479", "0.2049", "-0.2160", "Cross-validation became numerically unstable here"],
            ["ElasticNet", "0.8348", "0.4390", "0.1889", "-0.1684", "Best selection score in current run"],
            ["RandomForest", "0.8349", "0.4428", "0.1957", "-0.1888", "Very close to ElasticNet"],
            ["GradientBoosting", "0.8348", "0.4561", "0.2138", "-0.2613", "Slightly weaker holdout behavior"],
        ],
        [3.2 * cm, 2.7 * cm, 2.8 * cm, 2.1 * cm, 1.9 * cm, 4.8 * cm],
        "#fee2e2",
        "#fca5a5",
    )

    story.append(Paragraph("17. Best model and top feature influences", heading_style))
    add_bullets(
        story,
        [
            "Current best model from the code run: ElasticNet.",
            "Top feature influences observed in the run: lag_1, lag_2, rolling_mean_5, rolling_mean_10, lag_8, momentum_3, lag_3, rolling_std_5.",
            "Simple explanation: the model mostly depends on recent history plus short and medium-term trend context.",
        ],
        body_style,
    )

    story.append(Paragraph("18. Forecast and uncertainty explanation", heading_style))
    add_bullets(
        story,
        [
            "The model predicts future values step by step using its own previous outputs as new history.",
            "Residuals from the holdout period are resampled and added repeatedly to simulate uncertainty.",
            "The app reports percentiles instead of one exact future line.",
            "Example from a recent run: for 1935, the illustrative range was roughly P10 = -1.0310, P50 = -0.1808, P90 = 0.3582.",
            "Use the word illustrative extrapolation in the viva, because it is more honest than saying certain forecast.",
        ],
        body_style,
    )

    story.append(Paragraph("19. Risk regime detection explanation", heading_style))
    add_bullets(
        story,
        [
            "This is the unsupervised ML part of the app.",
            "KMeans clusters years using mean10, std10, rate, and acceleration.",
            "Clusters are then ranked by mean10 and mapped to Lower, Elevated, and High.",
            "In the current run, the final archive regime is High.",
            "Current regime counts are Lower = 89, High = 42, Elevated = 9.",
        ],
        body_style,
    )

    story.append(Paragraph("20. GenAI layer explanation", heading_style))
    add_bullets(
        story,
        [
            "The GenAI layer does not invent numbers by itself.",
            "It receives structured context from the analytics and ML layer.",
            "It can use OpenAI, Gemini, or OpenRouter, depending on keys and configuration.",
            "If no provider is available, it falls back to template-generated summaries.",
            "Best line: GenAI here is a communication layer on top of computed climate signals, not a replacement for the analytics engine.",
        ],
        body_style,
    )

    story.append(PageBreak())
    story.append(Paragraph("21. What is innovative in this prototype", heading_style))
    add_bullets(
        story,
        [
            "It connects historical climate analysis with decision-friendly interpretation.",
            "It separates signal, uncertainty, and action instead of mixing them into one chart.",
            "It uses explainable ML rather than a black-box-only approach.",
            "It includes both technical and non-technical communication layers in one prototype.",
            "It supports mentor, policymaker, and public-style outputs from the same core pipeline.",
        ],
        body_style,
    )

    story.append(Paragraph("22. What mentors may challenge", heading_style))
    add_bullets(
        story,
        [
            "Why is the dataset only until 1900?",
            "How can you justify using post-1900 outputs?",
            "Is this really regional modeling or just heuristic scoring?",
            "Which pages use real ML and which use analytics or simulation?",
            "Why are some metrics weak, especially R2?",
            "How do you prevent the AI summary from hallucinating?",
        ],
        body_style,
    )

    story.append(Paragraph("23. Strong answers to likely mentor questions", heading_style))
    add_table(
        story,
        [
            ["Question", "Strong answer"],
            ["What is your project in one sentence?", "It is an explainable climate intelligence prototype that turns a historical temperature archive into risk signals, uncertainty-aware scenarios, and stakeholder-ready interpretations."],
            ["Why did you choose this problem?", "Because climate data exists, but non-technical decision-makers still struggle to convert it into practical meaning."],
            ["What is the main objective?", "To bridge the gap between raw climate data and understandable, responsible decision support."],
            ["Why use anomaly instead of raw temperature?", "Anomaly normalizes values relative to a baseline and makes long-term shifts easier to interpret."],
            ["Why 1850-1900 baseline?", "It is used as the reference period in the prototype to compare relative deviations in the archive."],
            ["Which page is the most technical?", "Climate Intelligence Engine, because it contains model training, validation, uncertainty estimation, and regime detection."],
            ["Which page is most useful for non-technical users?", "Regional Risk and Policy, because it converts signal into region-level impact and action guidance."],
            ["Is Scenario Explorer machine learning?", "No. It is a Monte Carlo simulation page driven by user assumptions."],
            ["Is Risk Pulse supervised machine learning?", "No. It is a diagnostic analytics page that constructs a composite pulse from signal components."],
            ["What models did you compare?", "Ridge, ElasticNet, RandomForest, and GradientBoosting."],
            ["How did you choose the best model?", "Using time-series cross-validation plus holdout testing, combined into a selection score."],
            ["What does RMSE mean here?", "It is the typical scale of prediction error. Lower RMSE means the model tracked the holdout data more closely."],
            ["Why is R2 negative?", "It means the series is difficult for the model and that the current setup is still only prototype-grade, which is why we emphasize transparency and limitations."],
            ["What is your biggest limitation?", "Observed data ends at 1900, so later values are illustrative extrapolations, not observed climate records."],
            ["Then why is the prototype still useful?", "Because the value is in the workflow: explainable signal detection, uncertainty framing, regional interpretation, and communication support."],
            ["How do you avoid black-box criticism?", "We show feature influences, model comparison, holdout validation, uncertainty bands, and explicit regime logic."],
            ["How do you avoid AI hallucination?", "The AI layer is grounded on structured context from computed outputs, and it falls back to templates if no provider is safely available."],
            ["Is the regional risk score scientifically final?", "No. It is a transparent prototype scoring framework meant for interpretation support, not a fully calibrated regional climate model."],
            ["What would you improve next?", "Use a richer and more current climate dataset, calibrate regional factors with domain experts, and strengthen evaluation and governance."],
        ],
        [5.2 * cm, 10.2 * cm],
        "#dbeafe",
        "#93c5fd",
    )

    story.append(Paragraph("24. Page-by-page speaking script", heading_style))
    add_bullets(
        story,
        [
            "Home: This page introduces the problem, defines the key concepts, and tells the user how to move through the system.",
            "Global Trends: Here we establish the historical climate signal using anomaly, regression, bootstrap uncertainty, and decadal diagnostics.",
            "Regional Risk and Policy: This page translates the signal into regional exposure, vulnerability, urgency, and action guidance.",
            "Scenario Explorer: This page lets the user test assumptions and see a plausible range instead of one fixed future value.",
            "Climate Risk Pulse: This page diagnoses when the archive shifted fastest and what component drove that shift.",
            "Climate Intelligence Engine: This page proves the technical depth by showing model selection, validation, uncertainty, regime detection, and AI-ready summaries.",
        ],
        body_style,
    )

    story.append(Paragraph("25. Best 90-second final explanation", heading_style))
    add_bullets(
        story,
        [
            "Our prototype is a climate intelligence system built in Streamlit. It starts from a historical global temperature archive, converts the yearly data into anomaly relative to an 1850-1900 baseline, and then uses that signal in multiple ways.",
            "First, we explain the historical pattern through the Global Trends page using regression, bootstrap uncertainty, rolling trend shifts, and decadal summaries.",
            "Second, we translate the signal into regional meaning through exposure, adaptive capacity, and urgency logic on the Regional Risk and Policy page.",
            "Third, we let users explore uncertainty using Monte Carlo scenarios and a diagnostic pulse page that detects turning points and signal drivers.",
            "Finally, the Climate Intelligence Engine is our technical proof layer, where we build features, compare Ridge, ElasticNet, RandomForest, and GradientBoosting, choose the best model with time-aware validation, estimate uncertainty, detect regimes with KMeans, and generate stakeholder-ready summaries.",
            "The biggest limitation is that observed data ends at 1900, so later values are illustrative extrapolations. Even with that limitation, the prototype is useful because it demonstrates an explainable signal-to-decision workflow rather than just another chart dashboard.",
        ],
        body_style,
    )

    story.append(Paragraph("26. What not to say", heading_style))
    add_bullets(
        story,
        [
            "Do not say the app predicts the real future with certainty.",
            "Do not say the regional score is a fully validated scientific risk index.",
            "Do not say every page is machine learning.",
            "Do not hide that the observed archive ends at 1900.",
            "Do not let GenAI sound like the main engine; analytics and ML are the core engine.",
        ],
        body_style,
    )

    story.append(Paragraph("27. Best final closing line", heading_style))
    add_bullets(
        story,
        [
            "This prototype shows how climate data can be transformed into explainable, uncertainty-aware, decision-friendly intelligence, while still being honest about limitations and model scope.",
        ],
        body_style,
    )

    doc.build(story)
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
