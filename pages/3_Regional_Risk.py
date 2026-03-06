import streamlit as st
import pandas as pd
import plotly.express as px

from genai_engine import generate_genai_brief
from ml_engine import (
    detect_risk_regimes,
    forecast_with_uncertainty,
    load_annual_anomaly,
    people_impact_summary,
    projection_rate_per_decade,
    train_and_evaluate,
)

st.set_page_config(layout="wide")
st.title("Regional and Country-Level Risk Interpretation")

st.write(
    """
    This section translates global climate signals into region-level human risk meaning,
    using AI/ML-derived warming rates plus exposure and adaptive capacity assumptions.
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
latest_regime = str(regimes.iloc[-1]["regime"])

st.subheader("Global warming context")
use_ai_rate = st.checkbox("Use AI-estimated warming rate", value=True)

horizon = st.selectbox("Select interpretation horizon", ["2030s", "2050s", "2100"])
target_year = {"2030s": 2035, "2050s": 2050, "2100": 2100}[horizon]
ai_rate = projection_rate_per_decade(anomaly, forecast_df, target_year=target_year)

if use_ai_rate:
    global_rate = ai_rate
else:
    global_rate = st.slider("Manual global warming rate (C per decade)", 0.1, 0.8, 0.25, 0.01)

c1, c2 = st.columns(2)
c1.metric("Rate used", f"{global_rate:.2f} C/decade")
c2.metric("Latest ML regime", latest_regime)

region = st.selectbox(
    "Select region",
    ["Global Average", "South Asia", "Arctic", "Europe", "Small Island States"],
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
risk_score = regional_rate * vulnerability * regime_factor.get(latest_regime, 1.1)

st.metric("Region-adjusted warming signal", f"{regional_rate:.2f} C/decade")

st.subheader("AI/ML-supported risk scoring")
st.write("Risk = Warming Signal x Exposure x (1 - Adaptive Capacity) x Regime Factor")

score_cols = st.columns(4)
score_cols[0].metric("Exposure", f"{exposure_factors[region]:.2f}")
score_cols[1].metric("Adaptive capacity", f"{adaptive_capacity[region]:.2f}")
score_cols[2].metric("Regime factor", f"{regime_factor.get(latest_regime, 1.1):.2f}")
score_cols[3].metric("Composite score", f"{risk_score:.2f}")

risk_df = pd.DataFrame(
    {
        "Region": list(region_multipliers.keys()),
        "Risk Signal": [
            global_rate
            * region_multipliers[r]
            * exposure_factors[r]
            * (1 - adaptive_capacity[r])
            * regime_factor.get(latest_regime, 1.1)
            for r in region_multipliers
        ],
    }
)

fig = px.bar(
    risk_df,
    x="Region",
    y="Risk Signal",
    color="Risk Signal",
    color_continuous_scale="Reds",
    title="AI-informed relative climate risk by region",
)
fig.update_layout(height=420)
st.plotly_chart(fig, width="stretch")

if region == "South Asia":
    st.subheader("Country context (South Asia)")
    country = st.selectbox("Select country", ["India", "Pakistan", "Bangladesh", "Sri Lanka"])

    country_profiles = {
        "India": {"note": "High population exposure and rising humid heat stress."},
        "Pakistan": {"note": "Water scarcity amplifies heat and livelihood stress."},
        "Bangladesh": {"note": "Flood and coastal exposure raise compounding risk."},
        "Sri Lanka": {"note": "Agriculture-sensitive economy increases seasonal vulnerability."},
    }

    st.write(f"Context note: {country_profiles[country]['note']}")

st.subheader("Risk lens")
lens = st.radio("View risk through:", ["Human health", "Food systems", "Infrastructure"], horizontal=True)
st.info(people_impact_summary(latest_regime, lens))

st.subheader("Overall risk signal")
if risk_score < 0.08:
    risk = "Lower"
elif risk_score < 0.18:
    risk = "Elevated"
else:
    risk = "Severe"

st.write(f"Risk level: {risk}")

if risk == "Severe":
    st.error("AI-informed signals suggest adaptive capacity may be exceeded in exposed groups.")
elif risk == "Elevated":
    st.warning("AI-informed signals indicate increasing stress on people and critical systems.")
else:
    st.success("Risk is lower relative to peers, but sustained monitoring remains necessary.")

st.caption("This page uses AI/ML rate estimation and unsupervised regime classification for clearer people-focused interpretation.")

st.divider()
st.subheader("GenAI regional brief")

regional_context = {
    "region": region,
    "horizon": horizon,
    "global_rate_c_per_decade": round(float(global_rate), 3),
    "regional_rate_c_per_decade": round(float(regional_rate), 3),
    "risk_score": round(float(risk_score), 3),
    "latest_regime": latest_regime,
    "risk_lens": lens,
    "risk_level": risk,
}

if st.button("Generate GenAI regional summary"):
    brief, mode, note = generate_genai_brief(
        section_title="Regional climate-risk summary",
        objective="Summarize regional risk and provide practical actions for local planners.",
        context=regional_context,
    )
    st.write(brief)
    if mode == "llm":
        st.success(note)
    else:
        st.info(f"Fallback mode: {note}")
