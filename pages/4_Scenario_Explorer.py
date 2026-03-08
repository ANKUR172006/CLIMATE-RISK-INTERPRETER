import streamlit as st
import numpy as np
import plotly.graph_objects as go

from genai_engine import generate_genai_brief

st.set_page_config(layout="wide")
st.title("Scenario Explorer")

st.write(
    """
    Explore illustrative temperature pathways using a simple Monte Carlo generator.
    Scenarios are **not predictions** - they help understand ranges and thresholds beyond the 1750-1900 archive.
    """
)

rate = st.slider(
    "Assumed extrapolated rate (C per decade)",
    0.0,
    0.6,
    0.25,
    0.01,
)

rate_uncertainty = st.slider(
    "Rate uncertainty (+/- C per decade)",
    0.0,
    0.2,
    0.05,
    0.01,
)

years = st.slider("Years beyond the archive end", 10, 80, 30)

samples = st.slider("Number of simulations", 200, 2000, 600, 100)

np.random.seed(7)

sim_rates = np.random.normal(rate, rate_uncertainty, samples)
projected = (sim_rates / 10) * years

p10, p50, p90 = np.percentile(projected, [10, 50, 90])

m1, m2, m3 = st.columns(3)

m1.metric("10th percentile", f"{p10:.2f} C")
m2.metric("Median", f"{p50:.2f} C")
m3.metric("90th percentile", f"{p90:.2f} C")

fig = go.Figure()
fig.add_trace(go.Histogram(x=projected, nbinsx=30, marker_color="#42a5f5"))
fig.update_layout(
    height=420,
    xaxis_title="Projected additional anomaly (C)",
    yaxis_title="Simulation count",
    template="plotly_white",
)

st.plotly_chart(fig, width="stretch")

if p90 > 1.5:
    st.error("High likelihood of crossing the selected illustrative threshold range.")
elif p50 > 1.0:
    st.warning("High-impact extrapolated range.")
else:
    st.success("Lower-impact illustrative pathway if sustained.")

st.caption("Scenarios are illustrative extrapolations, not precise forecasts.")

st.divider()
st.subheader("GenAI scenario interpretation")

scenario_context = {
    "assumed_rate_c_per_decade": round(float(rate), 3),
    "rate_uncertainty_c_per_decade": round(float(rate_uncertainty), 3),
    "years_forward": int(years),
    "simulations": int(samples),
    "p10_c": round(float(p10), 3),
    "p50_c": round(float(p50), 3),
    "p90_c": round(float(p90), 3),
}

if st.button("Generate GenAI scenario summary"):
    brief, mode, note = generate_genai_brief(
        section_title="Scenario interpretation note",
        objective="Explain scenario spread, threshold risk, and no-regret actions while noting that the inputs are illustrative extrapolations.",
        context=scenario_context,
    )
    st.write(brief)
    if mode == "llm":
        st.success(note)
    else:
        st.info(f"Fallback mode: {note}")
