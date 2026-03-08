from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Rect, String
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


OUTPUT_PATH = Path("docs/page_explainers/07_ML_Engine_Explained_and_QA.pdf")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def box(drawing, x, y, w, h, text, fill, stroke, font_size=9):
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
            strokeWidth=1.1,
        )
    )
    lines = text.split("\n")
    total_h = len(lines) * (font_size + 2)
    start_y = y + (h / 2) + (total_h / 2) - font_size
    for i, line in enumerate(lines):
        lw = stringWidth(line, "Helvetica-Bold", font_size)
        drawing.add(
            String(
                x + (w - lw) / 2,
                start_y - i * (font_size + 2),
                line,
                fontName="Helvetica-Bold",
                fontSize=font_size,
                fillColor=colors.HexColor("#0f172a"),
            )
        )


def arrow(drawing, x1, y1, x2, y2):
    drawing.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor("#475569"), strokeWidth=1.4))
    drawing.add(Line(x2, y2, x2 - 5, y2 + 3, strokeColor=colors.HexColor("#475569"), strokeWidth=1.4))
    drawing.add(Line(x2, y2, x2 - 5, y2 - 3, strokeColor=colors.HexColor("#475569"), strokeWidth=1.4))


def build_pipeline_diagram():
    d = Drawing(520, 170)
    coords = [
        (8, 95, 75, 36, "CSV\nData", "#fee2e2", "#b91c1c"),
        (95, 95, 80, 36, "Annual\nMean", "#fef3c7", "#b45309"),
        (187, 95, 86, 36, "Baseline\n1850-1900", "#fef9c3", "#a16207"),
        (285, 95, 86, 36, "Anomaly\nSeries", "#dcfce7", "#15803d"),
        (383, 95, 64, 36, "Feature\nSet", "#dbeafe", "#1d4ed8"),
        (459, 95, 54, 36, "ML", "#ede9fe", "#7c3aed"),
    ]
    for x, y, w, h, text, fill, stroke in coords:
        box(d, x, y, w, h, text, fill, stroke)
    for i in range(len(coords) - 1):
        x, y, w, h, *_ = coords[i]
        x2, y2, *_ = coords[i + 1]
        arrow(d, x + w, y + h / 2, x2, y2 + h / 2)

    box(d, 120, 20, 105, 34, "Train + Compare\nModels", "#e0f2fe", "#0369a1")
    box(d, 240, 20, 105, 34, "Holdout Test\n+ RMSE", "#e0f2fe", "#0369a1")
    box(d, 360, 20, 105, 34, "Uncertainty\n+ Regimes", "#e0f2fe", "#0369a1")
    arrow(d, 486, 95, 410, 54)
    arrow(d, 486, 95, 292, 54)
    arrow(d, 486, 95, 172, 54)
    return d


def build_model_map_diagram():
    d = Drawing(520, 155)
    box(d, 20, 95, 100, 36, "Linear\nModels", "#fee2e2", "#b91c1c")
    box(d, 145, 95, 100, 36, "Tree\nModels", "#dcfce7", "#15803d")
    box(d, 270, 95, 110, 36, "Selection\nLogic", "#dbeafe", "#1d4ed8")
    box(d, 405, 95, 95, 36, "Best\nModel", "#ede9fe", "#7c3aed")
    arrow(d, 120, 113, 145, 113)
    arrow(d, 245, 113, 270, 113)
    arrow(d, 380, 113, 405, 113)
    box(d, 20, 25, 100, 28, "Ridge\nElasticNet", "#fff7ed", "#c2410c", 8.5)
    box(d, 145, 25, 100, 28, "RandomForest\nGradientBoosting", "#f0fdf4", "#166534", 8.2)
    box(d, 270, 25, 110, 28, "CV RMSE +\nHoldout RMSE", "#eff6ff", "#1d4ed8", 8.5)
    box(d, 405, 25, 95, 28, "Chosen\nOutput", "#faf5ff", "#7c3aed", 8.5)
    return d


def add_bullets(story, bullets, style):
    for bullet in bullets:
        story.append(Paragraph(f"- {bullet}", style))
    story.append(Spacer(1, 6))


def qa_table_data():
    return [
        ["Question", "Best answer"],
        ["ML exactly kahan use hua hai?", "Proper ML training mainly Climate Intelligence Engine me hai. Regional Risk and Policy page ML-derived signal aur regime outputs use karta hai. Scenario Explorer simulation page hai, aur Risk Pulse diagnostic signal page hai."],
        ["Aapne multiple models kyu use kiye?", "Ek hi model assume karna weak engineering hota. Humne linear aur tree-based dono approaches compare ki, phir best performer choose kiya."],
        ["Best model kaise choose hua?", "Time-series cross-validation plus holdout testing. Combined selection score ke basis par best model choose hua."],
        ["RMSE simple language me kya hai?", "RMSE average prediction error ka scale hai. Lower RMSE ka matlab model actual values ke closer tha."],
        ["Observed aur predicted graph same hona chahiye?", "Pattern similar hona chahiye, exact same nahi. Exact same suspicious ho sakta hai because of leakage or overfitting."],
        ["Extrapolation kya hota hai?", "Observed data ke existing pattern ko aage extend karke estimate banana. Ye observed future nahi hota."],
        ["Scenario Explorer bhi ML hai?", "Nahi. Wo simulation-based what-if page hai. Proper trained ML workbench Climate Intelligence Engine hai."],
        ["Risk regime detection kya karta hai?", "KMeans clustering se archive ke behavior phases ko Lower, Elevated, aur High states me divide karta hai."],
        ["Model black-box hai kya?", "Nahi. Feature importance, uncertainty bands, holdout validation, aur transparent regime logic available hai."],
        ["Dataset ki sabse badi limitation kya hai?", "Observed dataset 1750 se 1900 tak hi hai. Isliye post-1900 outputs illustrative extrapolations hain."],
        ["Fir prototype useful kyu hai?", "Kyuki innovation workflow me hai: signal detection, uncertainty, regional interpretation, action guidance, and explainable ML-backed communication."],
    ]


def deep_qa_table_data():
    return [
        ["Deep technical question", "Strong answer"],
        ["Aapne anomaly series hi kyu use ki, raw temperature kyu nahi?", "Anomaly baseline-relative signal deta hai. Raw temperature me absolute seasonal level zyada dominate karta hai, jabki anomaly long-term deviation ko clearer banati hai."],
        ["Feature vector exactly kaise banta hai?", "Har prediction step par past history se lag features, rolling mean, rolling std, recent slope, aur momentum nikale jate hain. Ye recent level, variability, direction, aur short-term movement ko capture karte hain."],
        ["lag features ka intuition kya hai?", "Time-series me recent past future se related hota hai. Lag features model ko recent memory dete hain."],
        ["Rolling mean aur rolling std kyu add kiye?", "Sirf past values dene se local context weak ho sakta hai. Rolling mean signal level batata hai, rolling std local volatility batata hai."],
        ["trend_10 feature kya karta hai?", "Recent 10 observations ki slope nikalta hai. Isse model ko pata chalta hai ki series abhi upward, flat, ya downward movement me hai."],
        ["momentum_3 ka role kya hai?", "Latest value aur recent short average ka difference batata hai. Ye recent push ya slowdown capture karta hai."],
        ["Aapne random train-test split kyu nahi use kiya?", "Time-series data me random split leakage create kar sakta hai because future information indirectly train set me aa jati hai. Isliye ordered split and TimeSeriesSplit use kiya gaya."],
        ["TimeSeriesSplit kya karta hai?", "Ye forward-in-time folds banata hai. Har fold me model past par train hota hai aur later segment par validate hota hai. Isse realistic evaluation hoti hai."],
        ["Holdout set alag kyu rakha?", "Cross-validation internal robustness ke liye hai. Final unseen holdout evaluation alag rakhna zaroori tha taaki fair performance estimate mile."],
        ["Selection score me CV aur holdout dono kyu combine kiye?", "Agar sirf holdout dekhte to one-shot luck ho sakta tha, aur sirf CV dekhte to final unseen period ignore hota. Combined score more balanced choice deta hai."],
        ["Ridge, ElasticNet, RandomForest, GradientBoosting hi kyu?", "Humne linear regularized models aur tree-based non-linear models dono compare kiye. Isse simple aur complex relationships dono test hue."],
        ["ElasticNet best kyu aaya?", "Current run me isne selection score best diya. Iska advantage hai regularization plus partial feature selection, jo chhote feature set aur correlated lags me useful hota hai."],
        ["Ridge ka CV RMSE unstable kyu ho gaya?", "Prototype dataset small hai aur some folds me scaling plus linear fit numerically unstable behave kar sakte hain. Ye bhi ek reason hai ki model comparison zaroori tha, single model blind trust nahi."],
        ["Negative R2 ka matlab kya?", "Matlab current prototype setting me model simple baseline se consistently better explain nahi kar raha. Isliye hum prediction ko overclaim nahi karte aur prototype framing maintain karte hain."],
        ["Phir ML weak nahi ho gaya?", "Mentor ke perspective se ye honest answer hai: yes, forecasting strength limited hai, but the project value sirf R2 nahi; explainable pipeline, uncertainty, risk interpretation, and communication flow bhi key contributions hain."],
        ["StandardScaler linear models ke sath kyu use kiya?", "Ridge aur ElasticNet feature scale-sensitive hote hain. Standardization se coefficients stable aur comparable bante hain."],
        ["Pipeline use karne ka fayda kya?", "Scaling aur model fitting ek reusable workflow me lock ho jate hain. Isse training and prediction behavior consistent rehta hai."],
        ["Forecast iterative kaise banta hai?", "Model ek next value predict karta hai, fir us value ko history me append karke agla step predict karta hai. Isi process ko horizon tak repeat kiya jata hai."],
        ["Error accumulate nahi hota iterative forecast me?", "Hota hai, aur isi liye uncertainty bands important hain. Longer horizon par confidence naturally reduce hoti hai."],
        ["Residual bootstrap kya hai?", "Holdout residuals ko random sample karke median prediction ke around multiple simulated trajectories banayi jati hain. Isse plausible spread milta hai."],
        ["P10, P50, P90 ka exact meaning?", "P50 median estimate hai. P10 lower plausible side aur P90 upper plausible side ko show karta hai. Ye certainty nahi, range hai."],
        ["KMeans clustering kyu use ki?", "Risk regime detection unsupervised task tha. KMeans similar behavior periods ko groups me divide karne ka simple and interpretable way deta hai."],
        ["Regime labels kaise aaye?", "Clusters ko mean10 ke basis par sort karke Lower, Elevated, High labels assign kiye gaye. Labels manual ranking se map hote hain."],
        ["KMeans me kaunse features gaye?", "10-year mean, 10-year std, rate, aur acceleration. Ye state, variability, speed, aur change-of-speed capture karte hain."],
        ["KMeans ka limitation kya hai?", "Cluster shape assumptions aur small data sensitivity. Isliye regimes ko indicative behavior states kehna better hai, absolute truth nahi."],
        ["Feature importance kaise nikala?", "Linear model me absolute coefficient magnitude aur tree model me feature_importances_ use kiya. Isse relative influence explain hota hai."],
        ["Data leakage avoid kaise kiya?", "Feature generation prediction year se pehle ki history se hoti hai, random shuffling avoid kiya, aur holdout future years alag rakhe."],
        ["Overfitting kaise check kiya?", "Model comparison, time-series CV, holdout error, and observed-vs-predicted graph se. Agar train-fit strong ho but holdout weak ho to overfitting concern hota."],
        ["Agar mentor bole model production-ready nahi hai?", "Correct. Ye production forecasting engine nahi, explainable climate intelligence prototype hai. Production ke liye better data, calibration, and monitoring chahiye."],
        ["GenAI ML ka part hai kya?", "Nahi, GenAI communication layer hai. Core analytics aur ML alag engine me hota hai."],
    ]


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=1.35 * cm,
        leftMargin=1.35 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
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
    h_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=7,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=14.2,
        textColor=colors.black,
        spaceAfter=4,
    )

    story = [
        Paragraph("ML Engine Explained, Deep Notes and Judge Q&A", title_style),
        Paragraph(
            "Complete desi-language handover for how ML works in the prototype, what every technical term means, why each model is there, and how to answer difficult questions.",
            subtitle_style,
        ),
        Paragraph("1. Sabse pehle ye samjho: ML kahan-kahan use hua hai", h_style),
    ]

    add_bullets(
        story,
        [
            "Proper ML training ka strongest use Climate Intelligence Engine page me hai.",
            "Regional Risk and Policy ML-derived signal and regime use karta hai, but full training page par nahi hoti.",
            "Global Trends page statistical analytics use karta hai: regression, rolling analysis, bootstrap uncertainty.",
            "Scenario Explorer proper ML page nahi hai. Wo simulation-based what-if tool hai.",
            "Risk Pulse full supervised ML page nahi hai. Wo signal triage aur diagnostic component page hai.",
        ],
        body_style,
    )

    story.append(Paragraph("2. End-to-end ML pipeline", h_style))
    story.append(build_pipeline_diagram())
    story.append(Spacer(1, 7))
    add_bullets(
        story,
        [
            "Step 1: CSV file load hoti hai.",
            "Step 2: Date cleaning hoti hai aur annual temperature mean nikalta hai.",
            "Step 3: 1850-1900 baseline calculate hoti hai.",
            "Step 4: Anomaly series banti hai: yearly temperature minus baseline.",
            "Step 5: Isi anomaly series se ML ke liye feature set banta hai.",
            "Step 6: Multiple candidate models train aur compare hote hain.",
            "Step 7: Best model holdout and CV score ke basis par choose hota hai.",
            "Step 8: Selected model se extrapolation aur uncertainty band banti hai.",
            "Step 9: KMeans clustering se risk regimes detect hote hain.",
            "Step 10: AI/GenAI layer result ko readable summary me convert karti hai.",
        ],
        body_style,
    )

    story.append(Paragraph("3. Data and anomaly creation", h_style))
    add_bullets(
        story,
        [
            "Observed data range 1750 se 1900 tak hai.",
            "Annual mean temperature nikala jata hai.",
            "Baseline 1850-1900 mean li gayi hai.",
            "Anomaly formula: anomaly = yearly temperature - baseline average.",
            "ML ko raw temperature se zyada anomaly series useful lagti hai because it creates a relative signal.",
        ],
        body_style,
    )

    story.append(Paragraph("4. Feature engineering simple language me", h_style))
    feature_table = Table(
        [
            ["Feature", "Simple meaning", "Why useful"],
            ["lag_1, lag_2 ...", "Pichhle anomaly values", "Past pattern dekhkar next behavior estimate karna"],
            ["rolling_mean_5", "Recent 5 values ka average", "Short-term level samajhna"],
            ["rolling_std_5", "Recent 5 values ki variability", "Short-term instability samajhna"],
            ["rolling_mean_10", "Recent 10 values ka average", "Medium-term level samajhna"],
            ["rolling_std_10", "Recent 10 values ki variability", "Medium-term instability samajhna"],
            ["trend_10", "Recent 10 values ki slope", "Signal kis direction me ja raha hai"],
            ["momentum_3", "Latest vs recent short average", "Short recent movement capture karna"],
        ],
        colWidths=[3.2 * cm, 5.0 * cm, 7.4 * cm],
    )
    feature_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#93c5fd")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.7),
                ("LEADING", (0, 0), (-1, -1), 10.4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(feature_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("5. Candidate models aur unka role", h_style))
    story.append(build_model_map_diagram())
    story.append(Spacer(1, 7))
    model_table = Table(
        [
            ["Model", "Type", "Simple understanding", "Why included"],
            ["Ridge", "Linear", "Smooth regularized line-based model", "Stable baseline; trend-like data ke liye achha start"],
            ["ElasticNet", "Linear", "Feature selection + regularization", "Some features stronger hon to useful"],
            ["RandomForest", "Tree ensemble", "Non-linear patterns pakadta hai", "Simple linear relationship se aage ja sakta hai"],
            ["GradientBoosting", "Boosted trees", "Sequentially better fitting model", "Complex signal fit karne ki capacity"],
        ],
        colWidths=[2.7 * cm, 2.7 * cm, 4.8 * cm, 6.0 * cm],
    )
    model_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcfce7")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#86efac")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 10.3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(model_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("6. Best model selection ka logic", h_style))
    add_bullets(
        story,
        [
            "Time-series data me random shuffle evaluation galat ho sakti hai, isliye time-aware evaluation use hoti hai.",
            "TimeSeriesSplit based cross-validation se training data ke andar robustness check hota hai.",
            "Holdout test alag rakha jata hai taaki final evaluation fair ho.",
            "Selection score CV RMSE aur holdout RMSE dono ko combine karta hai.",
            "Ye design judges ko dikhata hai ki best model manually guess nahi kiya gaya; systematically choose hua.",
        ],
        body_style,
    )

    story.append(Paragraph("7. Metrics ka exact meaning", h_style))
    metrics_table = Table(
        [
            ["Metric", "Simple meaning", "Good sign"],
            ["RMSE", "Average prediction error ka scale", "Lower value"],
            ["MAE", "Average absolute prediction error", "Lower value"],
            ["R2", "Model data variability kitni explain kar raha hai", "Higher value"],
            ["Model confidence", "RMSE and uncertainty width ka simple combined label", "High or medium"],
        ],
        colWidths=[3.4 * cm, 8.0 * cm, 4.8 * cm],
    )
    metrics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fef3c7")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#fcd34d")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(metrics_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("8. Holdout graph kaise explain karna hai", h_style))
    add_bullets(
        story,
        [
            "Observed line actual data hai.",
            "Predicted line model estimate hai.",
            "Dono exact same nahi hone chahiye.",
            "Best case: direction similar ho, peaks and dips roughly match karein, but exact overlap na ho.",
            "Agar bilkul same hua to leakage ya overfitting ka doubt ho sakta hai.",
            "Agar bahut alag hua to model weak hai.",
        ],
        body_style,
    )

    story.append(Paragraph("9. Uncertainty ka deep explanation", h_style))
    add_bullets(
        story,
        [
            "Model median line deta hai, but uncertainty ke bina wo misleading ho sakti hai.",
            "Holdout residuals collect kiye jate hain.",
            "Residual bootstrap se multiple simulated trajectories banayi jati hain.",
            "In simulations se P10, P50, P90 nikalte hain.",
            "P50 median estimate hai; P10 aur P90 lower and upper plausible range hain.",
            "Isliye app deterministic claim nahi karta.",
        ],
        body_style,
    )

    story.append(Paragraph("10. Extrapolation aur forecast me difference", h_style))
    add_bullets(
        story,
        [
            "Observed dataset 1900 tak hi hai.",
            "Model uske baad pattern ko aage extend karta hai.",
            "Strictly honest wording me ise illustrative extrapolation kehna better hai.",
            "Forecast word use kar sakte ho, but explain karna padega ki ye observed future nahi, model-based extension hai.",
        ],
        body_style,
    )

    story.append(Paragraph("11. Risk regime detection", h_style))
    add_bullets(
        story,
        [
            "Ye unsupervised ML component hai.",
            "KMeans clustering use hoti hai.",
            "Input features: 10-year mean, 10-year std, rate, acceleration.",
            "Model similar behavior wale years ko groups me divide karta hai.",
            "Phir groups ko ranking dekar labels milte hain: Lower, Elevated, High.",
            "Iska use simple chart ko behavior-based states me convert karna hai.",
        ],
        body_style,
    )

    story.append(Paragraph("12. Explainability", h_style))
    add_bullets(
        story,
        [
            "Linear models me coefficients dikhaye ja sakte hain.",
            "Tree models me feature importance dikhayi jati hai.",
            "Engine page ka feature-importance chart judge ko proof deta hai ki model inputs matter karte hain.",
            "This is important because you can say the system is not blindly generating a number.",
        ],
        body_style,
    )

    story.append(PageBreak())
    story.append(Paragraph("13. Page-wise ML use level", h_style))
    page_table = Table(
        [
            ["Page", "ML use level", "What exactly is happening"],
            ["Home", "Low", "Processed metrics only, no direct ML training"],
            ["Global Trends", "Medium", "Regression, rolling analysis, bootstrap uncertainty"],
            ["Regional Risk and Policy", "Medium", "ML-derived signal and regime used for interpretation"],
            ["Scenario Explorer", "Low", "Simulation-based uncertainty, not proper ML training"],
            ["Climate Risk Pulse", "Medium", "Signal engineering, turning-point diagnosis, component drivers"],
            ["Climate Intelligence Engine", "High", "Full ML training, model selection, holdout testing, uncertainty, regime detection, GenAI"],
        ],
        colWidths=[4.0 * cm, 2.8 * cm, 8.5 * cm],
    )
    page_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ede9fe")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c4b5fd")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.7),
                ("LEADING", (0, 0), (-1, -1), 10.4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(page_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("14. Most important limitation", h_style))
    add_bullets(
        story,
        [
            "Observed data ends at 1900.",
            "So post-1900 model outputs actual observed climate nahi hain.",
            "They are illustrative extrapolations.",
            "This is the single most important honesty point your ML teammate must say before judges ask.",
        ],
        body_style,
    )

    story.append(Paragraph("15. Why Climate Intelligence Engine public ko directly dikhana zaroori nahi", h_style))
    add_bullets(
        story,
        [
            "Ye non-technical public-first page nahi hai.",
            "Ye transparency, validation, aur trust page hai.",
            "Judges, mentors, technical evaluators, aur team handover ke liye useful hai.",
            "Best framing: this is the proof layer, not the first-view layer.",
        ],
        body_style,
    )

    story.append(PageBreak())
    story.append(Paragraph("16. Tough judge questions and strongest answers", h_style))
    qtable = Table(qa_table_data(), colWidths=[5.4 * cm, 10.0 * cm])
    qtable.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fee2e2")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#fca5a5")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 10.1),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(qtable)
    story.append(Spacer(1, 8))

    story.append(Paragraph("17. Best lines your ML teammate should memorize", h_style))
    add_bullets(
        story,
        [
            "We did not force ML everywhere. We used ML where it adds value.",
            "Climate Intelligence Engine is the advanced proof layer of the prototype.",
            "Observed data ends at 1900, so later values are illustrative extrapolations.",
            "Our innovation is explainable signal-to-decision design, not just prediction.",
            "We combine validation, uncertainty, interpretability, and stakeholder-ready outputs in one workflow.",
        ],
        body_style,
    )

    story.append(Paragraph("18. Best 45-second ML explanation", h_style))
    story.append(
        Paragraph(
            "Prototype me proper ML ka strongest use Climate Intelligence Engine me hai. Hum anomaly series se lag, rolling mean, volatility, trend, aur momentum features banate hain. "
            "Phir Ridge, ElasticNet, RandomForest, aur GradientBoosting models compare karte hain. Time-series cross-validation aur holdout testing ke basis par best model choose hota hai. "
            "Residual bootstrap se uncertainty band banti hai, aur KMeans clustering se risk regimes detect hote hain. Isliye hum sirf ek number nahi dete, balki validated, explainable, uncertainty-aware output dete hain.",
            body_style,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("19. Deep ML Core Questions Mentors Can Ask", h_style))
    qtable2 = Table(deep_qa_table_data(), colWidths=[6.0 * cm, 9.4 * cm])
    qtable2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#93c5fd")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("LEADING", (0, 0), (-1, -1), 9.8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(qtable2)
    story.append(Spacer(1, 8))

    story.append(Paragraph("20. Fast Technical Defense Script", h_style))
    add_bullets(
        story,
        [
            "If mentor asks how ML works: start with anomaly series, then feature engineering, then model comparison, then validation, then uncertainty, then regimes.",
            "If mentor attacks low R2: say this is prototype-grade forecasting on a limited historical archive, so we emphasize transparent uncertainty and decision support rather than claiming strong production forecasting.",
            "If mentor asks what is really novel: explainable signal-to-decision workflow, not just one prediction model.",
            "If mentor asks whether GenAI is doing the analysis: say no, analytics and ML compute the outputs first, GenAI only converts them into stakeholder-friendly language.",
        ],
        body_style,
    )

    doc.build(story)
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
