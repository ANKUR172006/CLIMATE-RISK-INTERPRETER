from __future__ import annotations

from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont
import pyttsx3

from moviepy import AudioFileClip, ImageClip, concatenate_videoclips


OUT_DIR = Path("video_assets")
OUT_DIR.mkdir(exist_ok=True)

VIDEO_PATH = Path("prototype_explanation_video.mp4")


SLIDES = [
    {
        "title": "Climate Prototype Overview",
        "bullets": [
            "This tool translates global temperature data into clear risk signals.",
            "It is built for non-technical stakeholders and policy planners.",
            "Goal: move from charts to actionable climate interpretation.",
        ],
        "narration": (
            "Welcome. This prototype converts raw climate history into interpretable risk signals. "
            "It helps planners understand trend direction, uncertainty, and local implications."
        ),
    },
    {
        "title": "Why This Problem Matters",
        "bullets": [
            "Climate data is large, but local decisions are still hard.",
            "Trend plots are often confused with exact predictions.",
            "Decision-makers need risk context, not just global averages.",
        ],
        "narration": (
            "We selected this problem because climate data is abundant, but decision clarity is limited. "
            "Most teams need local meaning and policy relevance, not only technical graphs."
        ),
    },
    {
        "title": "Prototype Flow",
        "bullets": [
            "Home and Global Trends establish warming baseline.",
            "Regional Risk translates signal into exposure and vulnerability.",
            "Scenario Explorer and Risk Pulse support planning alerts.",
            "Policy and AI pages convert analytics to action guidance.",
        ],
        "narration": (
            "The workflow starts with baseline understanding, then moves to regional interpretation, "
            "scenario exploration, and policy-oriented guidance."
        ),
    },
    {
        "title": "ML Integration",
        "bullets": [
            "Feature engineering: lags, rolling mean, volatility, trend, momentum.",
            "Model candidates: Ridge, ElasticNet, Random Forest, Gradient Boosting.",
            "Evaluation: time-series cross-validation plus holdout testing.",
            "Metrics: RMSE, MAE, R-squared, and combined selection score.",
        ],
        "narration": (
            "The machine learning pipeline uses engineered temporal features and benchmarks multiple supervised models. "
            "Selection is based on both cross-validation and holdout quality."
        ),
    },
    {
        "title": "Uncertainty and Explainability",
        "bullets": [
            "Forecast uncertainty is shown with P10, P50, and P90 bands.",
            "Residual bootstrapping is used for simulation ranges.",
            "Feature influence is visualized for transparent model behavior.",
            "Unsupervised clustering identifies climate risk regimes.",
        ],
        "narration": (
            "Instead of a single deterministic forecast, the prototype shows uncertainty bands. "
            "It also explains model influence and detects Lower, Elevated, and High risk regimes."
        ),
    },
    {
        "title": "GenAI Integration Status",
        "bullets": [
            "Current build uses template-based AI narrative summaries.",
            "No full external LLM orchestration in live pipeline yet.",
            "Next step: multilingual memo generation and guarded Q and A.",
        ],
        "narration": (
            "Generative AI is currently lightweight and template driven. "
            "A future release can add full language model assistance for policy briefs and multilingual communication."
        ),
    },
    {
        "title": "Ethics, Bias, and Limitations",
        "bullets": [
            "Outputs are decision support, not autonomous decisions.",
            "Regional multipliers are simplified and may hide local diversity.",
            "Data quality directly affects forecast reliability.",
            "Users must not treat scenarios as exact predictions.",
        ],
        "narration": (
            "Ethical use requires transparency and caution. "
            "This system supports human judgment and should be combined with local expertise, governance context, and uncertainty communication."
        ),
    },
    {
        "title": "Business Feasibility",
        "bullets": [
            "Target users: government, ESG teams, planners, consultants.",
            "Deployment model: B2B SaaS, white-label, or advisory analytics.",
            "Stack is lightweight and pilot-ready for cloud deployment.",
            "Production path: better data, regional calibration, governance.",
        ],
        "narration": (
            "From a business perspective, the prototype is feasible and pilot ready. "
            "It offers clear value in climate risk interpretation and stakeholder communication."
        ),
    },
    {
        "title": "Closing",
        "bullets": [
            "The prototype turns climate signals into practical insights.",
            "Its strength is interpretable analytics plus action guidance.",
            "With data and governance upgrades, it can scale to production.",
        ],
        "narration": (
            "Thank you. This prototype demonstrates a practical path from climate data to decision-ready insight."
        ),
    },
]


def _pick_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/arialbd.ttf"),
                Path("C:/Windows/Fonts/segoeuib.ttf"),
            ]
        )
    else:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/arial.ttf"),
                Path("C:/Windows/Fonts/segoeui.ttf"),
            ]
        )
    for fp in candidates:
        if fp.exists():
            return ImageFont.truetype(str(fp), size=size)
    return ImageFont.load_default()


def make_slide_image(title: str, bullets: list[str], idx: int) -> Path:
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#0b1f2a")
    draw = ImageDraw.Draw(img)

    title_font = _pick_font(64, bold=True)
    body_font = _pick_font(40, bold=False)
    small_font = _pick_font(30, bold=False)

    draw.rectangle([(0, 0), (w, 180)], fill="#123c52")
    draw.text((80, 55), title, fill="#f5f7fa", font=title_font)

    y = 250
    for bullet in bullets:
        wrapped = textwrap.wrap(bullet, width=65)
        if not wrapped:
            continue
        draw.text((110, y), f"- {wrapped[0]}", fill="#d5e7f2", font=body_font)
        y += 56
        for continuation in wrapped[1:]:
            draw.text((160, y), continuation, fill="#d5e7f2", font=body_font)
            y += 52
        y += 16

    draw.text((80, h - 70), "Climate Trends, Risk Signals & Local Implications", fill="#9fc3d9", font=small_font)

    out_path = OUT_DIR / f"slide_{idx:02d}.png"
    img.save(out_path)
    return out_path


def synthesize_audio(text: str, idx: int) -> Path:
    out_path = OUT_DIR / f"audio_{idx:02d}.wav"
    engine = pyttsx3.init()
    engine.setProperty("rate", 162)
    engine.setProperty("volume", 1.0)
    engine.save_to_file(text, str(out_path))
    engine.runAndWait()
    engine.stop()
    return out_path


def build_video() -> None:
    clips = []
    for i, slide in enumerate(SLIDES, start=1):
        img_path = make_slide_image(slide["title"], slide["bullets"], i)
        audio_path = synthesize_audio(slide["narration"], i)

        audio_clip = AudioFileClip(str(audio_path))
        duration = max(6.0, audio_clip.duration + 0.8)
        image_clip = ImageClip(str(img_path), duration=duration).with_audio(audio_clip)
        clips.append(image_clip)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(VIDEO_PATH),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="4000k",
    )

    final.close()
    for clip in clips:
        clip.close()


if __name__ == "__main__":
    build_video()
