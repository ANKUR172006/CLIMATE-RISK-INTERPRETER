import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Climate Trends, Risk Signals & Local Implications",
    page_icon="🌍",
    layout="wide"
)

st.markdown(
    """
    <style>
    .hero {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, #0b1f2a, #123c52);
        color: #f5f7fa;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    .hero h1 {
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .hero p {
        font-size: 1.05rem;
        margin-top: 0.5rem;
        line-height: 1.6;
    }
    .pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #1c4d69;
        border-radius: 999px;
        margin-right: 0.5rem;
        font-size: 0.85rem;
        color: #d5e7f2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <span class="pill">Climate Analytics</span>
        <span class="pill">Risk Signals</span>
        <span class="pill">Policy Insight</span>
        <h1>Climate Trends, Risk Signals & Local Implications</h1>
        <p>
            Climate data exists in abundance — understanding does not. This tool translates
            global temperature history into <strong>interpretable risk signals</strong> and
            local implications for decision-makers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.subheader("Why this prototype exists")

c1, c2 = st.columns([1.3, 1])

with c1:
    st.write(
        """
        **Problem framing**
        - Climate datasets are vast, but communities struggle to extract local meaning.
        - Trend signals are often conflated with forecasts, reducing trust.
        - Risk decisions require *direction, magnitude, and uncertainty* — not just charts.
        """
    )

    st.write(
        """
        **Key definitions**
        - **Trend:** long-term shift in the climate baseline.
        - **Risk signal:** an interpretable indicator of exposure or stress.
        - **Local implication:** how those signals translate to people, infrastructure, or systems.
        """
    )

with c2:
    st.info(
        """
        **Designed for**
        - City resilience planners
        - Public health & agriculture teams
        - Sustainability & policy analysts

        **Typical workflow**
        1. Understand global shift
        2. Detect acceleration
        3. Translate to regional exposure
        4. Explore scenarios
        5. Derive policy actions
        """
    )

st.divider()

st.subheader("What this tool enables")
st.write(
    """
    • Detection of long-term warming trends  
    • Identification of recent acceleration  
    • Regional amplification of risk  
    • Scenario-based interpretation with uncertainty  
    • Clear, responsible communication of risk signals  
    """
)

st.divider()

st.subheader("AI + ML approach (transparent, explainable)")

st.write(
    """
    This prototype integrates **explainable ML techniques** without black-box opacity:
    - **Trend regression & change-point scans** to detect acceleration
    - **Bootstrap uncertainty bands** to convey confidence
    - **Risk scoring models** that combine exposure and adaptive capacity
    """
)

st.caption("Use the sidebar to navigate through the analysis step-by-step.")

st.divider()

st.subheader("Quick data snapshot")

@st.cache_data
def load_annual_anomaly():
    df = pd.read_csv("GlobalTemperatures.csv")
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    df = df.set_index("dt")
    annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()
    baseline = annual.loc["1850":"1900"].mean()
    anomaly = annual - baseline
    return anomaly

anomaly = load_annual_anomaly()

latest_anomaly = anomaly.iloc[-1]
recent_mean = anomaly.tail(10).mean()

m1, m2, m3 = st.columns(3)

m1.metric("Latest anomaly", f"{latest_anomaly:.2f} °C")
m2.metric("Recent 10-year mean", f"{recent_mean:.2f} °C")
m3.metric("Years analyzed", f"{len(anomaly)}")

st.caption("Baseline uses 1850–1900 mean temperature.")

st.success(
    "➡️ Start with **Global Trends** to see the historical baseline, then move to **Recent Acceleration** for the AI/ML change-point analysis."
)