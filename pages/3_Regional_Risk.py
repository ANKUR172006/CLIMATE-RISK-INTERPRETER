import streamlit as st

st.set_page_config(layout="wide")
st.title("3. Regional & Country-Level Risk Interpretation")

st.write("""
Global warming does not affect all regions equally.
This section translates **global trends** into **regional and country-level risk contexts**.
""")

st.markdown("---")

# -------------------------------
# GLOBAL INPUT
# -------------------------------
st.subheader("Global warming context")

global_rate = st.slider(
    "Observed global warming rate (°C per decade)",
    0.1, 0.6, 0.25, 0.01
)

st.caption("Based on historical trend analysis.")

st.markdown("---")

# -------------------------------
# REGION SELECTION
# -------------------------------
st.subheader("Regional amplification")

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

regional_rate = global_rate * region_multipliers[region]

st.metric(
    "Region-adjusted warming rate",
    f"{regional_rate:.2f} °C per decade"
)

st.caption(
    "Regional amplification reflects geography and climate feedbacks."
)

st.markdown("---")

# -------------------------------
# COUNTRY CONTEXT (SAFE & HONEST)
# -------------------------------
if region == "South Asia":
    st.subheader("Country context")

    country = st.selectbox(
        "Select country",
        ["India", "Pakistan", "Bangladesh", "Sri Lanka"]
    )

    country_profiles = {
        "India": {
            "note": "High population exposure and humid heat stress.",
            "heat": "High",
            "food": "High",
            "coastal": "Medium"
        },
        "Pakistan": {
            "note": "Water stress amplifies heat impacts.",
            "heat": "High",
            "food": "Medium",
            "coastal": "Low"
        },
        "Bangladesh": {
            "note": "Low elevation increases flood vulnerability.",
            "heat": "Medium",
            "food": "High",
            "coastal": "High"
        },
        "Sri Lanka": {
            "note": "Moderate warming but high agricultural sensitivity.",
            "heat": "Medium",
            "food": "Medium",
            "coastal": "Medium"
        }
    }

    profile = country_profiles[country]

    st.write(f"**Context note:** {profile['note']}")

    st.markdown("---")

# -------------------------------
# RISK LENS (INNOVATION)
# -------------------------------
st.subheader("Risk lens")

lens = st.radio(
    "View risk through:",
    ["Human health", "Food systems", "Infrastructure"],
    horizontal=True
)

if lens == "Human health":
    st.write("Focus on heat stress, mortality risk, and vulnerable populations.")
elif lens == "Food systems":
    st.write("Focus on crop yield stability and seasonal disruption.")
else:
    st.write("Focus on urban systems, energy demand, and infrastructure stress.")

st.markdown("---")

# -------------------------------
# RISK CLASSIFICATION
# -------------------------------
st.subheader("Risk classification")

if regional_rate < 0.2:
    risk = "Low"
elif regional_rate < 0.4:
    risk = "High"
else:
    risk = "Critical"

st.write(f"**Overall risk level:** {risk}")

if risk == "Critical":
    st.error("Rapid warming likely to overwhelm adaptation capacity.")
elif risk == "High":
    st.warning("Significant adaptation required to reduce impacts.")
else:
    st.success("Lower risk, but monitoring remains essential.")

st.markdown("---")

# -------------------------------
# WHO IS MOST AFFECTED
# -------------------------------
st.subheader("Who is most affected?")

st.write("""
• Outdoor workers  
• Elderly populations  
• Small-scale farmers  
• Coastal communities  
""")

st.markdown("---")

# -------------------------------
# CONFIDENCE & LIMITS
# -------------------------------
with st.expander("📌 Confidence & limitations"):
    st.write("""
    • Regional values are **risk translations**, not local temperature forecasts  
    • Country impacts reflect exposure and vulnerability, not exact outcomes  
    • Results indicate **direction and relative magnitude**, not certainty
    """)

st.caption(
    "Responsible climate risk communication prioritizes transparency over precision."
)
