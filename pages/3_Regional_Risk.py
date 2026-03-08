import streamlit as st
import pandas as pd
import plotly.express as px

from genai_engine import generate_genai_brief
from ml_engine import (
    detect_risk_regimes,
    forecast_with_uncertainty,
    load_annual_anomaly,
    people_impact_summary,
    pick_year_projection,
    projection_rate_per_decade,
    train_and_evaluate,
)

st.set_page_config(layout="wide")
st.title("Regional Risk and Policy")

st.write(
    """
    This page turns the archive-based climate signal into a simple regional interpretation:
    signal strength, exposure, likely pressure points, and practical actions.
    """
)


@st.cache_resource
def get_ai_context():
    anomaly = load_annual_anomaly("GlobalTemperatures.csv")
    result = train_and_evaluate(anomaly, lags=8, test_years=20)
    forecast_df = forecast_with_uncertainty(
        model=result["best_model"],
        anomaly=anomaly,
        lags=8,
        horizon=80,
        residuals=result["residuals"],
        simulations=300,
    )
    regimes = detect_risk_regimes(anomaly, clusters=3)
    return anomaly, result, forecast_df, regimes


anomaly, result, forecast_df, regimes = get_ai_context()
final_regime = str(regimes.iloc[-1]["regime"])

st.subheader("1. Archive signal setup")

c1, c2, c3 = st.columns(3)

with c1:
    horizon = st.selectbox("Illustrative horizon", ["2030s", "2050s", "2100"])

with c2:
    use_model_rate = st.checkbox("Use model-estimated rate", value=True)

with c3:
    region = st.selectbox(
        "Region",
        ["Global Average", "South Asia", "Arctic", "Europe", "Small Island States"],
    )

target_year = {"2030s": 2035, "2050s": 2050, "2100": 2100}[horizon]
model_rate = projection_rate_per_decade(anomaly, forecast_df, target_year=target_year)

if use_model_rate:
    global_rate = model_rate
else:
    global_rate = st.slider("Manual archive signal rate (C per decade)", 0.1, 0.8, 0.25, 0.01)

proj_year_value = pick_year_projection(forecast_df, target_year)

st.caption(
    f"Observed data ends at 1900. The {horizon} value is an illustrative extrapolation from the archive, not an observed climate measurement."
)

region_multipliers = {
    "Global Average": 1.0,
    "South Asia": 1.1,
    "Arctic": 2.5,
    "Europe": 1.4,
    "Small Island States": 1.0,
}

exposure_factors = {
    "Global Average": 1.0,
    "South Asia": 1.3,
    "Arctic": 0.6,
    "Europe": 1.1,
    "Small Island States": 1.5,
}

adaptive_capacity = {
    "Global Average": 0.8,
    "South Asia": 0.6,
    "Arctic": 0.7,
    "Europe": 0.9,
    "Small Island States": 0.5,
}

regional_rate = global_rate * region_multipliers[region]
vulnerability = exposure_factors[region] * (1 - adaptive_capacity[region])
regime_factor = {"Lower": 0.9, "Elevated": 1.1, "High": 1.3}
risk_score = regional_rate * vulnerability * regime_factor.get(final_regime, 1.1)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Archive rate used", f"{global_rate:.2f} C/decade")
k2.metric(f"Illustrative anomaly ({target_year})", f"{proj_year_value:.2f} C")
k3.metric("Final archive regime", final_regime)
k4.metric("Regional signal", f"{regional_rate:.2f} C/decade")

st.divider()
st.subheader("2. Regional risk score")
st.write("Simple formula: `Regional signal x Exposure x (1 - Adaptive capacity) x Regime factor`")

score_cols = st.columns(4)
score_cols[0].metric("Exposure", f"{exposure_factors[region]:.2f}")
score_cols[1].metric("Adaptive capacity", f"{adaptive_capacity[region]:.2f}")
score_cols[2].metric("Regime factor", f"{regime_factor.get(final_regime, 1.1):.2f}")
score_cols[3].metric("Composite score", f"{risk_score:.2f}")

risk_df = pd.DataFrame(
    {
        "Region": list(region_multipliers.keys()),
        "Composite score": [
            global_rate
            * region_multipliers[r]
            * exposure_factors[r]
            * (1 - adaptive_capacity[r])
            * regime_factor.get(final_regime, 1.1)
            for r in region_multipliers
        ],
    }
)

fig = px.bar(
    risk_df,
    x="Region",
    y="Composite score",
    color="Composite score",
    color_continuous_scale="Reds",
    title="Relative regional score from the archive-based signal",
)
fig.update_layout(height=400)
st.plotly_chart(fig, width="stretch")

if region == "South Asia":
    country = st.selectbox("South Asia country note", ["India", "Pakistan", "Bangladesh", "Sri Lanka"])
    country_profiles = {
        "India": "High population exposure and rising humid heat stress.",
        "Pakistan": "Water scarcity amplifies heat and livelihood stress.",
        "Bangladesh": "Flood and coastal exposure raise compounding risk.",
        "Sri Lanka": "Agriculture-sensitive systems increase seasonal vulnerability.",
    }
    st.info(country_profiles[country])

st.divider()
st.subheader("3. Human impact lens")

lens = st.radio(
    "View through",
    ["Human health", "Food systems", "Infrastructure"],
    horizontal=True,
)
st.info(people_impact_summary(final_regime, lens))

if risk_score < 0.08:
    risk_level = "Lower"
elif risk_score < 0.18:
    risk_level = "Elevated"
else:
    risk_level = "Severe"

st.write(f"Overall interpreted level: **{risk_level}**")

st.divider()
st.subheader("4. Policy actions")

planning_context = st.selectbox(
    "Action focus",
    ["Heat stress", "Flood risk", "Food security", "Urban infrastructure"],
)

if final_regime == "High" or global_rate >= 0.3:
    urgency = "High"
elif final_regime == "Elevated" or global_rate >= 0.2:
    urgency = "Elevated"
else:
    urgency = "Moderate"

st.metric("Action urgency", urgency)

if planning_context == "Heat stress":
    if urgency == "High":
        st.error("Immediate action: heat plans, worker protection, and public-health surveillance.")
    elif urgency == "Elevated":
        st.warning("Near-term action: improve early warning coverage and cooling access.")
    else:
        st.info("Maintain preparedness and targeted awareness campaigns.")
elif planning_context == "Flood risk":
    if urgency == "High":
        st.error("Prioritize drainage redesign, floodplain enforcement, and emergency logistics.")
    elif urgency == "Elevated":
        st.warning("Upgrade high-risk drainage and improve hazard communication plans.")
    else:
        st.info("Improve mapping and preparedness protocols.")
elif planning_context == "Food security":
    if urgency == "High":
        st.error("Accelerate resilient seeds, storage buffers, and irrigation efficiency.")
    elif urgency == "Elevated":
        st.warning("Diversify crop systems and improve advisories for farmers.")
    else:
        st.info("Strengthen monitoring and contingency plans.")
else:
    if urgency == "High":
        st.error("Fast-track grid hardening, retrofit critical assets, and revise design standards.")
    elif urgency == "Elevated":
        st.warning("Prioritize resilience upgrades for high-load corridors and essential services.")
    else:
        st.info("Continue phased resilience investments.")

st.caption(
    "These actions are interpretation aids built from archive-based extrapolation, not deterministic forecasts."
)

st.divider()
st.subheader("5. GenAI summary")

regional_context = {
    "region": region,
    "horizon": horizon,
    "global_rate_c_per_decade": round(float(global_rate), 3),
    "regional_rate_c_per_decade": round(float(regional_rate), 3),
    "projection_year": int(target_year),
    "projection_value_c": round(float(proj_year_value), 3),
    "risk_score": round(float(risk_score), 3),
    "final_archive_regime": final_regime,
    "risk_lens": lens,
    "risk_level": risk_level,
    "planning_context": planning_context,
    "urgency": urgency,
}

if st.button("Generate GenAI regional-policy summary"):
    brief, mode, note = generate_genai_brief(
        section_title="Regional and policy climate signal summary",
        objective="Summarize the regional signal, the main impact lens, and practical actions. Make clear that post-1900 values are illustrative extrapolations from the archive.",
        context=regional_context,
    )
    st.write(brief)
    if mode == "llm":
        st.success(note)
    else:
        st.info(f"Fallback mode: {note}")
