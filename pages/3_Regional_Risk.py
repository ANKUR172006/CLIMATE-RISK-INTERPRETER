import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Regional & Country-Level Risk Interpretation")

st.write(
    """
    Global warming does not affect all regions equally.
    This section **translates global temperature trends into regional and population-level risk signals**,
    focusing on exposure, amplification, and vulnerability — not predictions.
    """
)

st.divider()

st.subheader("🌡️ Global warming context")

global_rate = st.slider(
    "Observed global warming rate (°C per decade)",
    0.1, 0.6, 0.25, 0.01
)

st.caption(
    "This value reflects historical global trends derived from observed temperature records."
)

st.divider()

st.subheader("⏳ Impact time horizon")

horizon = st.selectbox(
    "Select interpretation horizon",
    ["2030s", "2050s", "2100"]
)

st.caption(
    "Risk interpretation depends on time horizon, even without explicit forecasting."
)

st.divider()

st.subheader("🗺️ Regional amplification")

region = st.selectbox(
    "Select region",
    [
        "Global Average",
        "South Asia",
        "Arctic",
        "Europe",
        "Small Island States"
    ]
)

region_multipliers = {
    "Global Average": 1.0,
    "South Asia": 1.1,
    "Arctic": 2.5,
    "Europe": 1.4,
    "Small Island States": 1.0
}

exposure_factors = {
    "Global Average": 1.0,
    "South Asia": 1.3,
    "Arctic": 0.6,
    "Europe": 1.1,
    "Small Island States": 1.5
}

adaptive_capacity = {
    "Global Average": 0.8,
    "South Asia": 0.6,
    "Arctic": 0.7,
    "Europe": 0.9,
    "Small Island States": 0.5
}

regional_rate = global_rate * region_multipliers[region]

vulnerability = (exposure_factors[region] * (1 - adaptive_capacity[region]))
risk_score = regional_rate * vulnerability

st.metric(
    "Region-adjusted warming signal",
    f"{regional_rate:.2f} °C per decade"
)

st.caption(
    "Regional amplification reflects geography and climate feedbacks; exposure reflects population and system vulnerability."
)

st.divider()

st.subheader("🧠 AI/ML-style risk scoring")

st.write(
    """
    This model uses a transparent scoring equation:
    **Risk = Warming Signal × Exposure × (1 − Adaptive Capacity)**
    """
)

score_cols = st.columns(3)
score_cols[0].metric("Exposure factor", f"{exposure_factors[region]:.2f}")
score_cols[1].metric("Adaptive capacity", f"{adaptive_capacity[region]:.2f}")
score_cols[2].metric("Composite risk score", f"{risk_score:.2f}")

st.caption("All values are illustrative and intended for interpretive comparison only.")

st.divider()

st.subheader("📊 Relative regional risk comparison")

risk_df = pd.DataFrame({
    "Region": list(region_multipliers.keys()),
    "Risk Signal": [
        global_rate * region_multipliers[r] * exposure_factors[r] * (1 - adaptive_capacity[r])
        for r in region_multipliers
    ]
})

fig = px.bar(
    risk_df,
    x="Region",
    y="Risk Signal",
    color="Risk Signal",
    color_continuous_scale="Reds",
    title="Relative Climate Risk Signals by Region"
)

fig.update_layout(height=420)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "This comparison shows **relative risk signals**, not absolute temperature outcomes."
)

st.divider()

if region == "South Asia":
    st.subheader("🏳️ Country context (South Asia)")

    country = st.selectbox(
        "Select country",
        ["India", "Pakistan", "Bangladesh", "Sri Lanka"]
    )

    country_profiles = {
        "India": {
            "note": "High population exposure and increasing humid heat stress.",
            "Heat stress": "High",
            "Food systems": "High",
            "Coastal exposure": "Medium"
        },
        "Pakistan": {
            "note": "Water scarcity intensifies heat-related impacts.",
            "Heat stress": "High",
            "Food systems": "Medium",
            "Coastal exposure": "Low"
        },
        "Bangladesh": {
            "note": "Low elevation and dense population increase flood sensitivity.",
            "Heat stress": "Medium",
            "Food systems": "High",
            "Coastal exposure": "High"
        },
        "Sri Lanka": {
            "note": "Moderate warming with agriculture-sensitive impacts.",
            "Heat stress": "Medium",
            "Food systems": "Medium",
            "Coastal exposure": "Medium"
        }
    }

    profile = country_profiles[country]

    st.write(f"**Context note:** {profile['note']}")

    cols = st.columns(3)
    for col, (k, v) in zip(cols, list(profile.items())[1:]):
        col.metric(k, v)

    st.divider()

st.subheader("🔍 Risk lens")

lens = st.radio(
    "View risk through:",
    ["Human health", "Food systems", "Infrastructure"],
    horizontal=True
)

if lens == "Human health":
    st.write(
        "Focuses on heat stress, mortality risk, and vulnerable populations such as elderly and outdoor workers."
    )
elif lens == "Food systems":
    st.write(
        "Focuses on crop yield stability, rainfall variability, and seasonal disruption."
    )
else:
    st.write(
        "Focuses on urban systems, energy demand, transport stress, and infrastructure resilience."
    )

st.divider()

st.subheader("⚠️ Overall risk signal")

if risk_score < 0.08:
    risk = "Lower"
elif risk_score < 0.18:
    risk = "Elevated"
else:
    risk = "Severe"

st.write(f"**Risk level:** {risk}")

if risk == "Severe":
    st.error(
        "Observed warming signals may exceed adaptive capacity for exposed populations."
    )
elif risk == "Elevated":
    st.warning(
        "Warming trends suggest increasing stress on human and natural systems."
    )
else:
    st.success(
        "Relative risk remains lower, but long-term monitoring is essential."
    )

st.divider()

st.subheader("👥 Who is most affected?")

st.write(
    """
    • Outdoor and informal workers  
    • Elderly populations  
    • Small-scale farmers  
    • Coastal and low-lying communities  
    """
)

st.divider()

with st.expander("📌 Confidence & limitations"):
    st.write(
        """
        • Regional values are **risk translations**, not local temperature forecasts  
        • Country profiles reflect exposure and vulnerability, not precise outcomes  
        • Results indicate **direction and relative magnitude**, not certainty  
        """
    )

st.info(
    "These regional risk signals provide the analytical foundation for the **Policy & Adaptation Implications** section."
)

st.caption(
    "Responsible climate risk communication prioritizes transparency over precision."
)