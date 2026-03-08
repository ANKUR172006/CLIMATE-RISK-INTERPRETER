import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Climate Risk Pulse")

st.write(
    """
    This page is a signal triage lab. Instead of repeating the main trend view, it answers
    three different questions: when the archive changed fastest, which component drove the
    pulse, and how one historical era compares with another.
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


def _safe_zscore(values: np.ndarray) -> np.ndarray:
    std = float(np.std(values))
    if std == 0:
        return np.zeros_like(values, dtype=float)
    return (values - float(np.mean(values))) / std


anomaly = load_anomaly()
years = anomaly.index.year.values
values = anomaly.values

st.markdown("### Pulse controls")

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
roll_rate = trend_rate[valid_mask]
roll_acc = acceleration[valid_mask]

mean_score = _safe_zscore(roll_mean)
vol_score = _safe_zscore(roll_std)
acc_score = _safe_zscore(roll_acc)

pulse_raw = mean_score + (volatility_weight * vol_score) + (acceleration_weight * acc_score)
pulse_min = np.percentile(pulse_raw, 5)
pulse_max = np.percentile(pulse_raw, 95)

if pulse_max == pulse_min:
    pulse_index = np.full_like(pulse_raw, 50.0, dtype=float)
else:
    pulse_index = 100 * (pulse_raw - pulse_min) / (pulse_max - pulse_min)
    pulse_index = np.clip(pulse_index, 0, 100)

turning_strength = np.abs(np.gradient(pulse_index))

final_pulse = float(pulse_index[-1])
peak_idx = int(np.argmax(pulse_index))
peak_year = int(roll_years[peak_idx])
peak_pulse = float(pulse_index[peak_idx])

k1, k2, k3, k4 = st.columns(4)
k1.metric(f"Final pulse ({roll_years[-1]})", f"{final_pulse:.0f}")
k2.metric("Peak pulse", f"{peak_pulse:.0f}")
k3.metric("Peak year", f"{peak_year}")
k4.metric("Strongest shift count", f"{min(3, len(roll_years))}")

st.caption("Pulse combines level, volatility, and acceleration into a 0-100 triage score.")

st.markdown("### 1. Pulse timeline")

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=roll_years,
        y=pulse_index,
        mode="lines",
        line=dict(color="#7b1fa2", width=3),
        name="Pulse index",
    )
)
fig.add_trace(
    go.Scatter(
        x=[peak_year],
        y=[peak_pulse],
        mode="markers",
        marker=dict(size=11, color="#d81b60"),
        name="Peak pulse",
    )
)
fig.update_layout(
    height=380,
    xaxis_title="Year",
    yaxis_title="Pulse index",
    template="plotly_white",
    hovermode="x unified",
)
st.plotly_chart(fig, width="stretch")

st.divider()
st.markdown("### 2. Turning-point detector")

turn_df = pd.DataFrame(
    {
        "Year": roll_years,
        "Pulse index": pulse_index,
        "Turning strength": turning_strength,
        "Mean contribution": mean_score,
        "Volatility contribution": volatility_weight * vol_score,
        "Acceleration contribution": acceleration_weight * acc_score,
    }
)

top_turns = (
    turn_df.sort_values("Turning strength", ascending=False)
    .drop_duplicates(subset=["Year"])
    .head(3)
    .sort_values("Year")
    .reset_index(drop=True)
)

st.write("Top years where the archive pulse changed most sharply:")
st.dataframe(
    top_turns.round(2),
    width="stretch",
    hide_index=True,
)

selected_turn_year = st.selectbox(
    "Inspect a turning-point year",
    top_turns["Year"].tolist(),
    index=max(0, len(top_turns) - 1),
)

selected_row = turn_df[turn_df["Year"] == selected_turn_year].iloc[0]
component_df = pd.DataFrame(
    {
        "Component": ["Mean level", "Volatility", "Acceleration"],
        "Contribution": [
            float(selected_row["Mean contribution"]),
            float(selected_row["Volatility contribution"]),
            float(selected_row["Acceleration contribution"]),
        ],
    }
)

comp_fig = px.bar(
    component_df,
    x="Component",
    y="Contribution",
    color="Contribution",
    color_continuous_scale="Tealgrn",
    title=f"Pulse driver breakdown for {selected_turn_year}",
)
comp_fig.update_layout(height=360, coloraxis_showscale=False)
st.plotly_chart(comp_fig, width="stretch")

driver = component_df.iloc[component_df["Contribution"].abs().argmax()]["Component"]
st.info(
    f"In {selected_turn_year}, the pulse shifted most because of **{driver}**. "
    "This makes the page useful for diagnosing why a climate signal changed, not just where it was high."
)

st.divider()
st.markdown("### 3. Era comparison")

era_options = {
    "1750-1799": (1750, 1799),
    "1800-1849": (1800, 1849),
    "1850-1900": (1850, 1900),
}

e1, e2 = st.columns(2)
with e1:
    left_era = st.selectbox("First era", list(era_options.keys()), index=0)
with e2:
    right_era = st.selectbox("Second era", list(era_options.keys()), index=2)


def era_metrics(label: str) -> dict[str, float]:
    start, end = era_options[label]
    mask = (turn_df["Year"] >= start) & (turn_df["Year"] <= end)
    era = turn_df.loc[mask]
    return {
        "Mean pulse": float(era["Pulse index"].mean()),
        "Peak pulse": float(era["Pulse index"].max()),
        "Mean volatility contribution": float(era["Volatility contribution"].mean()),
        "Mean acceleration contribution": float(era["Acceleration contribution"].mean()),
    }


left_metrics = era_metrics(left_era)
right_metrics = era_metrics(right_era)

compare_df = pd.DataFrame(
    {
        "Metric": list(left_metrics.keys()),
        left_era: list(left_metrics.values()),
        right_era: list(right_metrics.values()),
    }
)
st.dataframe(compare_df.round(2), width="stretch", hide_index=True)

delta_pulse = right_metrics["Mean pulse"] - left_metrics["Mean pulse"]
if delta_pulse > 10:
    era_note = f"{right_era} shows a clearly stronger average pulse than {left_era}."
elif delta_pulse < -10:
    era_note = f"{left_era} shows a clearly stronger average pulse than {right_era}."
else:
    era_note = f"{left_era} and {right_era} sit in a fairly similar pulse range."

st.success(era_note)

st.divider()
st.markdown("### 4. Quick read")

if final_pulse >= 80:
    summary = "The final archive years sit in a high pulse range."
elif final_pulse >= 60:
    summary = "The final archive years sit in an elevated pulse range."
else:
    summary = "The final archive years sit in a moderate pulse range."

st.info(
    f"{summary} This page is now meant for triage: detect turning points, inspect pulse drivers, "
    f"and compare eras. For full ML benchmarking and extrapolation, open **Climate Intelligence Engine**."
)
