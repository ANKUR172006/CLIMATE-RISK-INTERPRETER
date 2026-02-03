import streamlit as st

st.set_page_config(layout="wide")
st.title("5. Human & Policy Implications")

st.write("""
### What the data implies

• **Heat stress** increases disproportionately in dense regions  
• **Agriculture** faces yield instability and seasonal shifts  
• **Infrastructure** must adapt to higher thermal baselines  
""")

st.subheader("Sectoral impacts")

st.write("""
**Health:** Increased heat-related illness and mortality  
**Food systems:** Greater climate sensitivity and volatility  
**Cities:** Cooling demand and infrastructure stress  
""")

st.subheader("Decision guidance")

st.write("""
This tool should be used:
- To understand **direction and magnitude**
- To support **risk-aware planning**
- Not as a precise prediction engine
""")

st.warning(
    "Delays in mitigation increase adaptation costs non-linearly."
)

st.caption(
    "Responsible climate communication prioritizes clarity over certainty."
)
