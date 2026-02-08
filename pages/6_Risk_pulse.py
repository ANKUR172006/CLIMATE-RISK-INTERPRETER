import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🧭 Climate Risk Pulse")

st.write(
    """
    The **Risk Pulse** is a novel diagnostic that fuses warming trends, volatility, and acceleration
    into a single interpretable signal. It is not a forecast — it is an **early-warning composite**
    to help teams spot emerging risk regimes and prioritize local action.
    """
)

@st.cache_data
def load_anomaly():
    df = pd.read_csv("GlobalTemperatures.csv")
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    df = df.set_index("dt")
    annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()
    baseline = annual.loc["1850":"1900"].mean()
    anomaly = annual - baseline
    return anomaly

anomaly = load_anomaly()

years = anomaly.index.year.values
values = anomaly.values

st.markdown("### ⚙️ Pulse configuration")

c1, c2, c3 = st.columns(3)

with c1:
    window = st.slider("Rolling window (years)", 10, 40, 20)

with c2:
    volatility_weight = st.slider("Volatility weight", 0.0, 1.0, 0.4, 0.05)

with c3:
    acceleration_weight = st.slider("Acceleration weight", 0.0, 1.0, 0.6, 0.05)

if len(values) <= window:
    st.warning("Not enough data for the selected window.")
    st.stop()

rolling_mean = pd.Series(values).rolling(window=window).mean().to_numpy()
rolling_std = pd.Series(values).rolling(window=window).std().to_numpy()

trend_rate = np.gradient(rolling_mean)
acceleration = np.gradient(trend_rate)

valid_mask = ~np.isnan(rolling_mean)

roll_years = years[valid_mask]
roll_mean = rolling_mean[valid_mask]
roll_std = rolling_std[valid_mask]
roll_acc = acceleration[valid_mask]

z_score = (roll_mean - np.mean(roll_mean)) / np.std(roll_mean)
vol_score = (roll_std - np.mean(roll_std)) / np.std(roll_std)
acc_score = (roll_acc - np.mean(roll_acc)) / np.std(roll_acc)

pulse_raw = z_score + (volatility_weight * vol_score) + (acceleration_weight * acc_score)

pulse_min = np.percentile(pulse_raw, 5)
pulse_max = np.percentile(pulse_raw, 95)
pulse_index = 100 * (pulse_raw - pulse_min) / (pulse_max - pulse_min)

pulse_index = np.clip(pulse_index, 0, 100)

latest_pulse = pulse_index[-1]

m1, m2, m3 = st.columns(3)

m1.metric("Latest pulse index", f"{latest_pulse:.0f}")
m2.metric("Rolling mean anomaly", f"{roll_mean[-1]:.2f} °C")
m3.metric("Rolling volatility", f"{roll_std[-1]:.2f} °C")

st.caption("Pulse index scales to 0–100 using recent distribution percentiles.")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=roll_years,
    y=pulse_index,
    mode="lines",
    line=dict(color="#7b1fa2", width=2),
    name="Risk Pulse"
))

fig.update_layout(
    height=420,
    xaxis_title="Year",
    yaxis_title="Risk Pulse Index",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🚨 Emerging risk alerts")

alert_threshold = st.slider("Alert threshold", 60, 95, 80)

recent_pulse = pd.Series(pulse_index, index=roll_years)
alerts = recent_pulse[recent_pulse >= alert_threshold]

if alerts.empty:
    st.success("No alert thresholds crossed in the selected configuration.")
else:
    st.warning(
        f"Alert threshold crossed in **{len(alerts)}** years. Latest high-pulse year: **{alerts.index[-1]}**."
    )

st.divider()

st.markdown("### 🗺️ Local implication mapper")

region = st.selectbox(
    "Select a region",
    ["Global", "South Asia", "Europe", "Arctic", "Small Island States"]
)

sector = st.selectbox(
    "Select a sector",
    ["Public health", "Food systems", "Infrastructure", "Water security"]
)

if latest_pulse >= 80:
    risk_state = "High"
elif latest_pulse >= 60:
    risk_state = "Elevated"
else:
    risk_state = "Moderate"

st.write(
    f"**Current pulse state:** {risk_state} risk signal for **{region}** in **{sector}**."
)

recommendations = {
    "Public health": [
        "Activate heat early-warning systems and public alerts.",
        "Expand cooling centers and occupational heat protections.",
        "Track heat-related morbidity in near-real time."
    ],
    "Food systems": [
        "Prioritize drought-resilient crop portfolios.",
        "Increase strategic food storage buffers.",
        "Accelerate irrigation efficiency upgrades."
    ],
    "Infrastructure": [
        "Stress-test energy and transport systems for peak heat.",
        "Fast-track retrofit plans for critical assets.",
        "Review design standards for extreme temperature exposure."
    ],
    "Water security": [
        "Enhance monitoring of reservoirs and groundwater drawdown.",
        "Plan demand-management programs for heat peaks.",
        "Assess transboundary water risk coordination."
    ]
}

st.write("**Recommended actions:**")

for item in recommendations[sector]:
    st.write(f"• {item}")

st.caption(
    "These recommendations are generated from pulse intensity and sector context — not deterministic forecasts."
)