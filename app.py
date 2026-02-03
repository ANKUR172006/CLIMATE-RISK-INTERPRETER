import streamlit as st

st.set_page_config(
    page_title="Climate Trends, Risk Signals & Local Implications",
    layout="wide"
)

st.title("Climate Trends, Risk Signals & Local Implications")

st.write("""
Climate data exists in abundance — understanding does not.

This prototype analyzes **historical global temperature records**
and transforms them into **interpretable climate risk signals**
to support public understanding and policy reasoning.
""")

st.divider()

st.subheader("What this tool enables")
st.write("""
• Detection of long-term warming trends  
• Identification of recent acceleration  
• Regional amplification of risk  
• Scenario-based interpretation  
• Responsible communication of uncertainty  
""")

st.info("""
📊 Data: Historical global temperature observations  
🧠 Model: Transparent NumPy regression (no black-box ML)  
🎯 Purpose: Decision-relevant climate understanding
""")

st.caption("Use the sidebar to navigate through the analysis step-by-step.")
