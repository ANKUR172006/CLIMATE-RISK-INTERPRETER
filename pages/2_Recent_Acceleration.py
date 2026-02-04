import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------- Page Setup ----------------
st.set_page_config(layout="wide")
st.title("📈 Recent Acceleration in Global Warming")

st.caption(
    "This page examines whether warming has accelerated in recent decades "
    "by comparing observed temperature trends across historical periods."
)

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("GlobalTemperatures.csv")
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    return df.set_index("dt")

df = load_data()

annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()
baseline = annual.loc["1850":"1900"].mean()
anomaly = annual - baseline

# ---------------- Helper Function ----------------
def compute_rate(series):
    """
    Safely compute warming rate (°C/decade).
    Returns None if data is insufficient.
    """
    if series is None or len(series) < 5:
        return None
    x = series.index.year.values
    y = series.values
    slope, _ = np.polyfit(x, y, 1)
    return slope * 10

# ---------------- Period Definitions ----------------
early = anomaly.loc["1850":"1900"]
mid = anomaly.loc["1900":"1980"]
recent = anomaly.loc["1980":]

early_rate = compute_rate(early)
mid_rate = compute_rate(mid)
recent_rate = compute_rate(recent)

# ---------------- Metrics ----------------
st.markdown("### 📊 Acceleration Signals")

c1, c2, c3 = st.columns(3)

c1.metric(
    "1850–1900 rate",
    f"{early_rate:.2f} °C / decade" if early_rate is not None else "Insufficient data"
)

c2.metric(
    "1900–1980 rate",
    f"{mid_rate:.2f} °C / decade" if mid_rate is not None else "Insufficient data"
)

c3.metric(
    "Post-1980 rate",
    f"{recent_rate:.2f} °C / decade" if recent_rate is not None else "Insufficient data"
)

st.caption("Rates are calculated using linear regression on observed data only.")

st.divider()

# ---------------- Visual Comparison ----------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=anomaly.index.year,
    y=anomaly.values,
    name="Temperature anomaly",
    line=dict(color="#1565c0")
))

fig.update_layout(
    height=460,
    xaxis_title="Year",
    yaxis_title="Temperature anomaly (°C)",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- Interpretation ----------------
st.markdown("### 🧠 What this tells us")

if recent_rate and mid_rate and recent_rate > mid_rate:
    st.success(
        "Warming has **accelerated in recent decades**. "
        "The post-1980 warming rate is significantly higher than earlier periods."
    )
elif recent_rate and mid_rate:
    st.info(
        "Warming continues, but acceleration relative to earlier periods is modest."
    )
else:
    st.warning(
        "Not enough data to confidently assess acceleration for all periods."
    )

st.caption(
    "This analysis uses historical observations only. "
    "It does not forecast future temperatures."
)
