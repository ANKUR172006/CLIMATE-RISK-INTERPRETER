import streamlit as st

from genai_engine import generate_genai_brief
from ml_engine import (
    detect_risk_regimes,
    forecast_with_uncertainty,
    load_annual_anomaly,
    pick_year_projection,
    projection_rate_per_decade,
    train_and_evaluate,
)

st.set_page_config(layout="wide")
st.title("Human and Policy Implications")


@st.cache_resource
def get_policy_ai_context():
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


anomaly, result, forecast_df, regimes = get_policy_ai_context()
latest_regime = str(regimes.iloc[-1]["regime"])
rate_2050 = projection_rate_per_decade(anomaly, forecast_df, target_year=2050)
proj_2035 = pick_year_projection(forecast_df, 2035)
proj_2050 = pick_year_projection(forecast_df, 2050)

st.subheader("AI/ML policy snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Best model", result["best_model_name"])
c2.metric("Holdout RMSE", f"{result['metrics'][result['best_model_name']]['rmse']:.3f} C")
c3.metric("Projected rate to 2050", f"{rate_2050:.2f} C/decade")
c4.metric("Latest regime", latest_regime)

st.write(
    """
- Heat stress, food volatility, and infrastructure load all scale with sustained warming rates.
- AI/ML projections are used here for prioritization, not deterministic prediction.
"""
)

st.divider()
st.subheader("Scenario-aware policy prioritization")

risk_context = st.selectbox(
    "Select planning context",
    ["Heat stress", "Flood risk", "Food security", "Urban infrastructure"],
)

if latest_regime == "High" or rate_2050 >= 0.3:
    urgency = "High"
elif latest_regime == "Elevated" or rate_2050 >= 0.2:
    urgency = "Elevated"
else:
    urgency = "Moderate"

st.metric("Policy urgency", urgency)
st.caption(f"Median anomaly estimate: 2035 = {proj_2035:.2f} C, 2050 = {proj_2050:.2f} C")

if risk_context == "Heat stress":
    if urgency == "High":
        st.error("Immediate action: city heat plans, worker protections, and public-health surveillance.")
    elif urgency == "Elevated":
        st.warning("Near-term action: early warning coverage and cooling access in vulnerable districts.")
    else:
        st.info("Maintain preparedness and targeted awareness campaigns.")
elif risk_context == "Flood risk":
    if urgency == "High":
        st.error("Prioritize drainage redesign, floodplain enforcement, and emergency logistics.")
    elif urgency == "Elevated":
        st.warning("Upgrade high-risk drainage and improve hazard communication plans.")
    else:
        st.info("Improve mapping and preparedness protocols.")
elif risk_context == "Food security":
    if urgency == "High":
        st.error("Accelerate drought-resilient seed adoption, storage buffers, and irrigation efficiency.")
    elif urgency == "Elevated":
        st.warning("Diversify crop systems and improve climate advisories for farmers.")
    else:
        st.info("Strengthen monitoring and contingency plans.")
else:
    if urgency == "High":
        st.error("Fast-track grid hardening, retrofit critical assets, and revise design standards.")
    elif urgency == "Elevated":
        st.warning("Prioritize resilience upgrades for high-load corridors and essential services.")
    else:
        st.info("Continue phased resilience investments.")

st.divider()
st.subheader("Decision guidance")
st.write(
    """
Use this prototype to:
- understand direction and magnitude of climate pressure,
- compare urgency across policy domains,
- communicate risk in plain language for non-technical stakeholders.
"""
)

st.caption(
    "Responsible policy use: model outputs guide prioritization, while final decisions should include local expertise and governance context."
)

st.divider()
st.subheader("GenAI policy memo")

policy_context = {
    "planning_context": risk_context,
    "urgency": urgency,
    "latest_regime": latest_regime,
    "best_model": result["best_model_name"],
    "holdout_rmse_c": round(float(result["metrics"][result["best_model_name"]]["rmse"]), 3),
    "projected_rate_2050_c_per_decade": round(float(rate_2050), 3),
    "projection_2035_c": round(float(proj_2035), 3),
    "projection_2050_c": round(float(proj_2050), 3),
}

if st.button("Generate GenAI policy memo"):
    brief, mode, note = generate_genai_brief(
        section_title="Policy memo for climate planning",
        objective="Provide short-term and medium-term actions with uncertainty-aware language.",
        context=policy_context,
        min_words=110,
        max_words=190,
    )
    st.write(brief)
    if mode == "llm":
        st.success(note)
    else:
        st.info(f"Fallback mode: {note}")
