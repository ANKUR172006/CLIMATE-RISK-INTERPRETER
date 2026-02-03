import streamlit as st

st.set_page_config(layout="wide")
st.title("4. Scenario Explorer")

rate = st.slider(
    "Assumed future warming rate (°C per decade)",
    0.0, 0.6, 0.25, 0.01
)

years = st.slider(
    "Years into the future",
    10, 80, 30
)

projected = (rate / 10) * years

st.metric("Projected additional warming", f"{projected:.2f} °C")

if projected > 1.5:
    st.error("High likelihood of crossing critical climate thresholds.")
elif projected > 1.0:
    st.warning("High-impact warming range.")
else:
    st.success("Lower-impact pathway if sustained.")

st.caption("Scenarios are illustrative, not precise forecasts.")
