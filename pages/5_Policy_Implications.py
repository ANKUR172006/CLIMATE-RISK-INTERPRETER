import streamlit as st

st.set_page_config(layout="wide")
st.title("🏛️ Human & Policy Implications")

st.write(
    """

    • **Heat stress** increases disproportionately in dense regions  
    • **Agriculture** faces yield instability and seasonal shifts  
    • **Infrastructure** must adapt to higher thermal baselines  
    """
)

st.divider()

st.subheader("Sectoral impacts")

st.write(
    """
    **Health:** Increased heat-related illness and mortality  
    **Food systems:** Greater climate sensitivity and volatility  
    **Cities:** Cooling demand and infrastructure stress  
    """
)

st.divider()

st.subheader("AI-assisted policy prioritization")

risk_context = st.selectbox(
    "Select a planning context",
    ["Heat stress", "Flood risk", "Food security", "Urban infrastructure"]
)

if risk_context == "Heat stress":
    st.info(
        "Focus on early warning systems, cooling centers, and worker protections."
    )
elif risk_context == "Flood risk":
    st.info(
        "Prioritize resilient drainage, floodplain zoning, and emergency response capacity."
    )
elif risk_context == "Food security":
    st.info(
        "Invest in climate-resilient crops, storage, and diversified supply chains."
    )
else:
    st.info(
        "Accelerate retrofits, grid resilience, and heat-ready materials."
    )

st.caption(
    "Policy recommendations are rule-based to ensure transparency and auditability."
)

st.divider()

st.subheader("Decision guidance")

st.write(
    """
    This tool should be used:
    - To understand **direction and magnitude**
    - To support **risk-aware planning**
    - Not as a precise prediction engine
    """
)

st.warning(
    "Delays in mitigation increase adaptation costs non-linearly."
)

st.caption(
    "Responsible climate communication prioritizes clarity over certainty."
)