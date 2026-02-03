import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("1. Global Temperature Trends")

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

years = anomaly.index.year.values
temps = anomaly.values

slope, intercept = np.polyfit(years, temps, 1)
trend = slope * years + intercept

fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=temps, name="Observed anomaly"))
fig.add_trace(go.Scatter(x=years, y=trend, name="Long-term trend", line=dict(dash="dash")))

fig.update_layout(
    height=450,
    xaxis_title="Year",
    yaxis_title="Temperature anomaly (°C)"
)

st.plotly_chart(fig, use_container_width=True)

st.metric("Long-term warming rate", f"{slope*10:.2f} °C per decade")

st.divider()

with st.expander("🔍 Seasonal structure (3D view)"):
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
            colorscale="Viridis"
        )]
    )

    fig3d.update_layout(
        height=500,
        scene=dict(
            xaxis_title="Month",
            yaxis_title="Year",
            zaxis_title="Temperature (°C)"
        )
    )

    st.plotly_chart(fig3d, use_container_width=True)

st.caption("3D view highlights seasonality layered onto long-term warming.")
