import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🌍 Global Temperature Trends")

st.caption(
    "This section explains how Earth’s average temperature has changed over time, "
    "why the change is accelerating, and why it matters for regions and people."
)

@st.cache_data
def load_data():
    df = pd.read_csv("GlobalTemperatures.csv")
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    return df.set_index("dt")

df = load_data()

st.markdown("### 🎛️ Exploration Controls")

c1, c2, c3 = st.columns(3)

with c1:
    year_range = st.slider(
        "Select analysis period",
        int(df.index.year.min()),
        int(df.index.year.max()),
        (1950, int(df.index.year.max()))
    )

with c2:
    show_trend = st.checkbox("Show long-term trend", value=True)

with c3:
    show_uncertainty = st.checkbox("Show uncertainty band (bootstrap)", value=True)

df = df[(df.index.year >= year_range[0]) & (df.index.year <= year_range[1])]

annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()

baseline = annual.loc["1850":"1900"].mean()
anomaly = annual - baseline

years = anomaly.index.year.values
temps = anomaly.values

if len(years) > 1:
    slope, intercept = np.polyfit(years, temps, 1)
    trend = slope * years + intercept
else:
    slope, trend = 0, None

st.markdown("### ⏳ Before vs Now")

pre_industrial = annual.loc["1850":"1900"].mean()

recent_years = min(10, len(annual))
recent = annual.iloc[-recent_years:].mean()

delta = recent - pre_industrial

b1, b2, b3 = st.columns(3)

b1.metric("Pre-industrial average", f"{pre_industrial:.2f} °C")
b2.metric(f"Recent {recent_years}-year average", f"{recent:.2f} °C")
b3.metric("Net increase", f"+{delta:.2f} °C")

st.caption(
    "This comparison shows how today’s climate differs from the one modern societies developed in."
)

uncertainty_low = None
uncertainty_high = None

if show_uncertainty and len(years) > 10:
    samples = 600
    preds = []
    for _ in range(samples):
        resample_idx = np.random.choice(len(years), len(years), replace=True)
        x = years[resample_idx]
        y = temps[resample_idx]
        boot_slope, boot_intercept = np.polyfit(x, y, 1)
        preds.append(boot_slope * years + boot_intercept)
    preds = np.vstack(preds)
    uncertainty_low = np.percentile(preds, 5, axis=0)
    uncertainty_high = np.percentile(preds, 95, axis=0)

fig = go.Figure()

fig.add_vrect(x0=1850, x1=1950, fillcolor="#e3f2fd", opacity=0.3, line_width=0)
fig.add_vrect(x0=1950, x1=1980, fillcolor="#fff9c4", opacity=0.3, line_width=0)
fig.add_vrect(x0=1980, x1=years[-1], fillcolor="#ffebee", opacity=0.3, line_width=0)

fig.add_trace(go.Scatter(
    x=years,
    y=temps,
    mode="lines",
    name="Observed temperature anomaly",
    line=dict(color="#1565c0", width=2)
))

if show_trend and trend is not None:
    fig.add_trace(go.Scatter(
        x=years,
        y=trend,
        name="Long-term trend",
        line=dict(color="#c62828", dash="dash", width=2)
    ))

if show_uncertainty and uncertainty_low is not None:
    fig.add_trace(go.Scatter(
        x=np.concatenate([years, years[::-1]]),
        y=np.concatenate([uncertainty_low, uncertainty_high[::-1]]),
        fill="toself",
        fillcolor="rgba(33, 150, 243, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="Bootstrap 90% band"
    ))

fig.update_layout(
    height=500,
    hovermode="x unified",
    xaxis_title="Year",
    yaxis_title="Temperature anomaly (°C)",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📊 Key Signals")

m1, m2, m3 = st.columns(3)

m1.metric("Warming rate", f"{slope*10:.2f} °C per decade")
m2.metric("Latest anomaly", f"{temps[-1]:.2f} °C")
m3.metric("Years analyzed", f"{len(years)}")

st.caption("All values are relative to the 1850–1900 pre-industrial baseline.")

st.info(
    "🧠 **Plain-language insight:**\n\n"
    "The planet is not just warming — the **speed of warming is increasing**. "
    "Each decade adds more heat than the one before, shifting what is considered "
    "‘normal’ climate for ecosystems, cities, and agriculture."
)

st.divider()

st.markdown("### 🧭 Rolling acceleration (AI/ML signal)")

window = st.slider("Rolling window (years)", 10, 40, 20)

rolling_rates = []
rolling_years = []

if len(years) > window:
    for i in range(len(years) - window + 1):
        x = years[i : i + window]
        y = temps[i : i + window]
        roll_slope, _ = np.polyfit(x, y, 1)
        rolling_rates.append(roll_slope * 10)
        rolling_years.append(x[-1])

    roll_fig = go.Figure()
    roll_fig.add_trace(go.Scatter(
        x=rolling_years,
        y=rolling_rates,
        mode="lines",
        line=dict(color="#00897b", width=2),
        name="Rolling warming rate"
    ))
    roll_fig.update_layout(
        height=350,
        xaxis_title="Year",
        yaxis_title="Warming rate (°C/decade)",
        template="plotly_white"
    )
    st.plotly_chart(roll_fig, use_container_width=True)
else:
    st.warning("Not enough data to compute rolling rates for the selected window.")

st.caption(
    "Rolling regression acts as a transparent ML signal to reveal where warming accelerates."
)

st.divider()

st.markdown("### 🗂️ Decadal Climate Shift")

df_dec = anomaly.to_frame("Anomaly")
df_dec["Decade"] = (df_dec.index.year // 10) * 10
decadal = df_dec.groupby("Decade").mean().round(2)

st.dataframe(decadal, use_container_width=True)

st.caption(
    "Decadal averages remove year-to-year noise and reveal long-term structural change."
)

st.divider()

with st.expander("🌐 Seasonal Structure — 3D Climate Surface"):
    df_m = df.copy()
    df_m["Year"] = df_m.index.year
    df_m["Month"] = df_m.index.month

    pivot = df_m.pivot_table(
        index="Year",
        columns="Month",
        values="LandAndOceanAverageTemperature",
        aggfunc="mean"
    )

    fig3d = go.Figure(
        data=[go.Surface(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale="Viridis",
            contours=dict(z=dict(show=True, project_z=True)),
            lighting=dict(ambient=0.6, diffuse=0.8)
        )]
    )

    fig3d.update_layout(
        height=550,
        scene=dict(
            xaxis_title="Month",
            yaxis_title="Year",
            zaxis_title="Temperature (°C)",
            camera=dict(eye=dict(x=1.6, y=1.3, z=0.9))
        )
    )

    st.plotly_chart(fig3d, use_container_width=True)

st.caption(
    "Seasonal cycles remain — but they now occur on top of a higher and warmer baseline."
)

st.success(
    "➡️ **Why this matters:** Global warming sets the baseline. "
    "Next sections explore **which regions warm fastest**, "
    "**who is most exposed**, and **what risks emerge locally**."
)