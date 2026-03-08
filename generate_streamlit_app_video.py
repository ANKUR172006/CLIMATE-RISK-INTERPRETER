from __future__ import annotations

import asyncio
import subprocess
import time
from pathlib import Path

import edge_tts
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
from playwright.async_api import async_playwright


APP_URL = "http://127.0.0.1:8501"
VOICE = "en-US-GuyNeural"
OUT_VIDEO = Path("streamlit_formal_demo_video_v2.mp4")
ASSET_DIR = Path("streamlit_video_assets")
ASSET_DIR.mkdir(exist_ok=True)


SCENES_BY_LABEL = {
    "app": [
        {
            "scroll_ratio": 0.0,
            "narration": (
                "Welcome to the Climate Trends, Risk Signals and Local Implications prototype. "
                "The home page introduces the decision workflow and explains why climate analytics must be interpreted for policy use."
            ),
            "wait_plot": False,
        },
        {
            "scroll_ratio": 0.55,
            "narration": (
                "This section summarizes the key outputs: long term trend detection, regional interpretation, scenario exploration, "
                "and AI assisted risk communication with uncertainty."
            ),
            "wait_plot": False,
        },
    ],
    "global trends": [
        {
            "scroll_ratio": 0.0,
            "narration": (
                "On Global Trends, the top controls let you adjust analysis period and toggle trend and uncertainty layers. "
                "The chart compares observed anomaly against a long term warming signal."
            ),
            "wait_plot": True,
        },
        {
            "scroll_ratio": 0.32,
            "narration": (
                "These metric cards compare pre industrial baseline with recent average temperature and net increase. "
                "This creates a direct before versus now climate narrative."
            ),
            "wait_plot": False,
        },
        {
            "scroll_ratio": 0.62,
            "narration": (
                "Further down, rolling warming rate shows acceleration dynamics. "
                "The decadal table then removes annual noise and highlights structural shift over time."
            ),
            "wait_plot": True,
        },
        {
            "scroll_ratio": 0.9,
            "narration": (
                "The lower section includes optional seasonal structure exploration. "
                "Overall, this page establishes global baseline change before any local risk interpretation."
            ),
            "wait_plot": False,
        },
    ],
    "regional risk": [
        {
            "scroll_ratio": 0.0,
            "narration": (
                "Regional Risk and Policy converts the archive signal into regional interpretation. "
                "You can use a model estimated rate or a manual rate, then select horizon and region."
            ),
            "wait_plot": False,
        },
        {
            "scroll_ratio": 0.4,
            "narration": (
                "The composite score combines archive signal, exposure, adaptive capacity, and final machine learning regime. "
                "This bar chart compares relative climate pressure across regions."
            ),
            "wait_plot": True,
        },
        {
            "scroll_ratio": 0.86,
            "narration": (
                "Lower on the page, the impact lens and action section translate model state into people focused insight and practical policy actions. "
                "This now combines regional interpretation and response planning in one flow."
            ),
            "wait_plot": False,
        },
    ],
    "scenario explorer": [
        {
            "scroll_ratio": 0.0,
            "narration": (
                "Scenario Explorer is an uncertainty sandbox. "
                "You set warming rate, uncertainty range, time horizon, and simulation count."
            ),
            "wait_plot": False,
        },
        {
            "scroll_ratio": 0.45,
            "narration": (
                "The histogram and percentile outputs, including P10, median, and P90, describe possible warming distribution. "
                "Threshold messages help classify impact severity."
            ),
            "wait_plot": True,
        },
    ],
    "risk pulse": [
        {
            "scroll_ratio": 0.0,
            "narration": (
                "Risk Pulse is the signal triage page. "
                "You can tune rolling window, volatility weight, and acceleration weight to shape the pulse index."
            ),
            "wait_plot": False,
        },
        {
            "scroll_ratio": 0.42,
            "narration": (
                "The timeline shows pulse dynamics, while the turning point detector identifies where the archive changed most sharply. "
                "This makes the page diagnostic, not just descriptive."
            ),
            "wait_plot": True,
        },
        {
            "scroll_ratio": 0.76,
            "narration": (
                "Lower on the page, component breakdown and era comparison explain why the pulse changed and which historical period carried stronger signal."
            ),
            "wait_plot": False,
        },
    ],
    "climate intelligence engine": [
        {
            "scroll_ratio": 0.0,
            "narration": (
                "Climate Intelligence Engine is the advanced workbench. "
                "You can configure lag features, holdout window, extrapolation horizon, and uncertainty simulations."
            ),
            "wait_plot": False,
        },
        {
            "scroll_ratio": 0.3,
            "narration": (
                "This table compares model performance on holdout metrics. "
                "The selected model is then validated against observed values in the holdout plot."
            ),
            "wait_plot": True,
        },
        {
            "scroll_ratio": 0.58,
            "narration": (
                "Feature influence improves transparency, while forecast chart provides uncertainty bands from residual bootstrapping. "
                "This avoids over confidence in a single line estimate."
            ),
            "wait_plot": True,
        },
        {
            "scroll_ratio": 0.86,
            "narration": (
                "The final section shows unsupervised risk regimes and AI narrative summary. "
                "Together, this page combines performance, explainability, and decision ready communication."
            ),
            "wait_plot": True,
        },
    ],
}


def _normalize(text: str) -> str:
    cleaned = text.strip().lower().replace("+", " ").replace("/", " ")
    return " ".join(cleaned.split())


def wait_for_streamlit(timeout_sec: int = 60) -> None:
    import urllib.request

    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            with urllib.request.urlopen(APP_URL, timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(1)
    raise TimeoutError("Streamlit server did not start in time.")


async def capture_pages() -> list[tuple[Path, str]]:
    captures: list[tuple[Path, str]] = []

    async def wait_for_page_stable(page, needs_plot: bool = False):
        # Wait for main app mount and loading spinners to settle.
        await page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=45000)
        await page.wait_for_timeout(2200)
        for _ in range(8):
            spinner_count = await page.locator('[data-testid="stSpinner"]').count()
            skeleton_count = await page.locator('[data-testid="stSkeleton"]').count()
            if spinner_count == 0 and skeleton_count == 0:
                break
            await page.wait_for_timeout(700)
        if needs_plot:
            try:
                await page.wait_for_selector(".js-plotly-plot", timeout=12000)
            except Exception:
                pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(APP_URL, wait_until="domcontentloaded")
        await wait_for_page_stable(page, needs_plot=False)

        nav_links = page.locator('[data-testid="stSidebarNav"] a')
        count = await nav_links.count()

        entries = []
        for i in range(count):
            link = nav_links.nth(i)
            label = (await link.inner_text()).strip()
            href = await link.get_attribute("href")
            if not href:
                continue
            target = href if href.startswith("http") else f"{APP_URL}{href}"
            entries.append((label, target))

        seen_urls: set[str] = set()
        scene = 1

        for label, target in entries:
            if target in seen_urls:
                continue
            seen_urls.add(target)

            await page.goto(target, wait_until="domcontentloaded")
            key = _normalize(label)
            # Align labels from Streamlit sidebar with narration map keys.
            key = key.replace("climate intelligence engine", "climate intelligence engine")
            page_scenes = SCENES_BY_LABEL.get(key, [])
            if not page_scenes:
                # fallback: single scene for unknown page labels
                page_scenes = [
                    {
                        "scroll_ratio": 0.0,
                        "narration": "This page provides additional climate analysis content.",
                        "wait_plot": False,
                    }
                ]

            for scene_cfg in page_scenes:
                await wait_for_page_stable(page, needs_plot=bool(scene_cfg["wait_plot"]))
                total_height = await page.evaluate("document.body.scrollHeight")
                viewport_height = await page.evaluate("window.innerHeight")
                max_scroll = max(0, int(total_height - viewport_height))
                scroll_y = int(max_scroll * float(scene_cfg["scroll_ratio"]))
                await page.evaluate(f"window.scrollTo(0, {scroll_y})")
                await page.wait_for_timeout(1200)

                shot = ASSET_DIR / f"scene_{scene:02d}.png"
                await page.screenshot(path=str(shot), full_page=False)
                captures.append((shot, str(scene_cfg["narration"])))
                scene += 1

        await browser.close()

    return captures


async def synthesize_audio(text: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate="-8%", pitch="-2Hz")
    await communicate.save(str(out_path))


async def build_audio_for_captures(captures: list[tuple[Path, str]]) -> list[tuple[Path, Path]]:
    triplets: list[tuple[Path, Path]] = []
    for idx, (image_path, narration) in enumerate(captures, start=1):
        audio_path = ASSET_DIR / f"scene_{idx:02d}.mp3"
        await synthesize_audio(narration, audio_path)
        triplets.append((image_path, audio_path))
    return triplets


def render_video(triplets: list[tuple[Path, Path]]) -> None:
    clips = []
    for image_path, audio_path in triplets:
        audio = AudioFileClip(str(audio_path))
        duration = max(6.5, audio.duration + 0.9)
        clip = ImageClip(str(image_path), duration=duration).with_audio(audio)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(OUT_VIDEO),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="4500k",
    )
    final.close()
    for clip in clips:
        clip.close()


def main() -> None:
    streamlit_proc = subprocess.Popen(
        ["python", "-m", "streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_streamlit(timeout_sec=70)
        captures = asyncio.run(capture_pages())
        triplets = asyncio.run(build_audio_for_captures(captures))
        render_video(triplets)
    finally:
        streamlit_proc.terminate()
        try:
            streamlit_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            streamlit_proc.kill()


if __name__ == "__main__":
    main()

