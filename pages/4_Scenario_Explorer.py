import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🧭 Scenario Explorer")

st.write(
    """
    Explore illustrative warming pathways using a simple Monte Carlo generator.
    Scenarios are **not predictions** — they help understand ranges and thresholds.
    """
)

rate = st.slider(
    "Assumed future warming rate (°C per decade)",
    0.0, 0.6, 0.25, 0.01
)

rate_uncertainty = st.slider(
    "Rate uncertainty (± °C per decade)",
    0.0, 0.2, 0.05, 0.01
)

years = st.slider(
    "Years into the future",
    10, 80, 30
)

samples = st.slider(
    "Number of simulations",
    200, 2000, 600, 100
)

np.random.seed(7)

sim_rates = np.random.normal(rate, rate_uncertainty, samples)
projected = (sim_rates / 10) * years

p10, p50, p90 = np.percentile(projected, [10, 50, 90])

m1, m2, m3 = st.columns(3)

m1.metric("10th percentile", f"{p10:.2f} °C")
m2.metric("Median", f"{p50:.2f} °C")
m3.metric("90th percentile", f"{p90:.2f} °C")

fig = go.Figure()
fig.add_trace(go.Histogram(x=projected, nbinsx=30, marker_color="#42a5f5"))
fig.update_layout(
    height=420,
    xaxis_title="Projected additional warming (°C)",
    yaxis_title="Simulation count",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

if p90 > 1.5:
    st.error("High likelihood of crossing critical climate thresholds.")
elif p50 > 1.0:
    st.warning("High-impact warming range.")
else:
    st.success("Lower-impact pathway if sustained.")

st.caption("Scenarios are illustrative, not precise forecasts.")