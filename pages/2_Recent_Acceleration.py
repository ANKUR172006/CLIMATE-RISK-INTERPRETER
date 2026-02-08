import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Recent Acceleration in Global Warming")

st.caption(
    "This page examines whether warming has accelerated in recent decades "
    "by comparing observed temperature trends across historical periods."
)

@st.cache_data
def load_data():
    df = pd.read_csv("GlobalTemperatures.csv")
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    return df.set_index("dt")

df = load_data()

annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()
baseline = annual.loc["1850":"1900"].mean()
anomaly = annual - baseline

def compute_rate(series):
    """
    Safely compute warming rate (°C/decade).
    Returns None if data is insufficient.
    """
    if series is None or len(series) < 5:
        return None
    x = series.index.year.values
    y = series.values
    slope, _ = np.polyfit(x, y, 1)
    return slope * 10

early = anomaly.loc["1850":"1900"]
mid = anomaly.loc["1900":"1980"]
recent = anomaly.loc["1980":]

early_rate = compute_rate(early)
mid_rate = compute_rate(mid)
recent_rate = compute_rate(recent)

st.markdown("### 🧪 Change-point scan (explainable ML)")

scan_start = st.slider("Scan start year", 1910, 1970, 1950)
scan_end = st.slider("Scan end year", 1975, 2010, 1995)

candidate_years = np.arange(scan_start, scan_end)

best_year = None
best_score = np.inf

for year in candidate_years:
    left = anomaly.loc[:f"{year}"]
    right = anomaly.loc[f"{year+1}":]
    if len(left) < 10 or len(right) < 10:
        continue
    x_left = left.index.year.values
    y_left = left.values
    x_right = right.index.year.values
    y_right = right.values
    left_slope, left_intercept = np.polyfit(x_left, y_left, 1)
    right_slope, right_intercept = np.polyfit(x_right, y_right, 1)
    left_pred = left_slope * x_left + left_intercept
    right_pred = right_slope * x_right + right_intercept
    score = np.sum((y_left - left_pred) ** 2) + np.sum((y_right - right_pred) ** 2)
    if score < best_score:
        best_score = score
        best_year = year

st.write(
    "This scan looks for a year that minimizes the error of two separate trend lines. "
    "It is a transparent alternative to black-box ML for detecting structural shifts."
)

if best_year:
    st.success(f"Most likely acceleration shift: **{best_year}**")
else:
    st.warning("Unable to detect a reliable change-point for the selected range.")
