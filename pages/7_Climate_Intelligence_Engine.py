import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from genai_engine import generate_genai_brief, generate_policy_brief
from ml_engine import (
    build_ai_brief,
    detect_risk_regimes,
    forecast_with_uncertainty,
    load_annual_anomaly,
    train_and_evaluate,
)

st.set_page_config(layout="wide")
st.title("Climate Intelligence Engine")

st.write(
    """
    Transparent ML + GenAI workflow for climate decision support:
    - train and compare models,
    - quantify uncertainty,
    - detect risk regimes,
    - generate stakeholder-ready briefings.
    """
)

if "genai_last_text" not in st.session_state:
    st.session_state.genai_last_text = ""
if "engine_prev_snapshot" not in st.session_state:
    st.session_state.engine_prev_snapshot = None

@st.cache_resource(show_spinner=False)
def run_training_pipeline(lags: int, test_years: int):
    anomaly_series = load_annual_anomaly("GlobalTemperatures.csv")
    result_obj = train_and_evaluate(anomaly_series, lags=lags, test_years=test_years)
    regime_obj = detect_risk_regimes(anomaly_series, clusters=3)
    return anomaly_series, result_obj, regime_obj


@st.cache_resource(show_spinner=False)
def run_forecast_pipeline(
    lags: int,
    test_years: int,
    horizon: int,
    sims: int,
):
    anomaly_series, result_obj, _ = run_training_pipeline(lags, test_years)
    forecast_obj = forecast_with_uncertainty(
        model=result_obj["best_model"],
        anomaly=anomaly_series,
        lags=lags,
        horizon=horizon,
        residuals=result_obj["residuals"],
        simulations=sims,
    )
    return forecast_obj

st.markdown("### Controls")
c0, c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1, 1])
with c0:
    view_mode = st.segmented_control("View mode", ["Basic", "Expert"], default="Basic")
with c1:
    lags = st.slider("Lag features", 4, 15, 8)
with c2:
    test_years = st.slider("Holdout years", 10, 40, 20)
with c3:
    horizon = st.slider("Forecast horizon", 10, 60, 25)
with c4:
    sims = st.slider("Uncertainty simulations", 200, 1200, 400, 100)

try:
    with st.spinner("Running ML pipeline..."):
        anomaly, result, regime_df = run_training_pipeline(lags, test_years)
        forecast_df = run_forecast_pipeline(lags, test_years, horizon, sims)
except ValueError as err:
    st.warning(str(err))
    st.stop()

metrics_df = pd.DataFrame(result["metrics"]).T.sort_values("rmse")
best_name = result["best_model_name"]
best_rmse = float(metrics_df.loc[best_name, "rmse"])

latest = regime_df.iloc[-1]

year_2035 = forecast_df[forecast_df["year"] == 2035]
year_2050 = forecast_df[forecast_df["year"] == 2050]

p50_2035 = float(year_2035["p50"].iloc[0]) if not year_2035.empty else float(forecast_df["p50"].iloc[min(len(forecast_df)-1, 10)])
p50_2050 = float(year_2050["p50"].iloc[0]) if not year_2050.empty else float(forecast_df["p50"].iloc[-1])

p10_2035 = float(year_2035["p10"].iloc[0]) if not year_2035.empty else float(forecast_df["p10"].iloc[min(len(forecast_df)-1, 10)])
p90_2035 = float(year_2035["p90"].iloc[0]) if not year_2035.empty else float(forecast_df["p90"].iloc[min(len(forecast_df)-1, 10)])
unc_width_2035 = p90_2035 - p10_2035

if best_rmse <= 0.15 and unc_width_2035 <= 0.6:
    confidence = "High"
elif best_rmse <= 0.25 and unc_width_2035 <= 1.0:
    confidence = "Medium"
else:
    confidence = "Low"

st.markdown("### Executive KPI Strip")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Best model", best_name)
k2.metric("RMSE", f"{best_rmse:.3f} C")
k3.metric("Current regime", str(latest["regime"]))
k4.metric("P50 anomaly 2035", f"{p50_2035:.2f} C")
k5.metric("Model confidence", confidence)

current_snapshot = {
    "best_model": best_name,
    "rmse": best_rmse,
    "regime": str(latest["regime"]),
    "p50_2035": p50_2035,
}

prev = st.session_state.engine_prev_snapshot
if prev is not None:
    d_rmse = best_rmse - prev["rmse"]
    d_p35 = p50_2035 - prev["p50_2035"]
    st.caption(
        f"Since last run: model {prev['best_model']} -> {best_name}, "
        f"RMSE delta {d_rmse:+.3f}, 2035 projection delta {d_p35:+.3f} C, "
        f"regime {prev['regime']} -> {current_snapshot['regime']}"
    )
st.session_state.engine_prev_snapshot = current_snapshot

context = {
    "best_model": best_name,
    "rmse": best_rmse,
    "regime": str(latest["regime"]),
    "p50_2035": p50_2035,
    "p50_2050": p50_2050,
    "horizon": int(horizon),
    "lags": int(lags),
    "confidence": confidence,
}

if view_mode == "Expert":
    st.markdown("### Holdout model performance")
    st.dataframe(
        metrics_df.style.format({"rmse": "{:.3f}", "mae": "{:.3f}", "r2": "{:.3f}"}),
        width="stretch",
    )

    fig_holdout = go.Figure()
    fig_holdout.add_trace(
        go.Scatter(
            x=result["years_test"],
            y=result["y_test"],
            mode="lines+markers",
            name="Observed",
            line=dict(color="#1565c0", width=2),
        )
    )
    fig_holdout.add_trace(
        go.Scatter(
            x=result["years_test"],
            y=result["holdout_pred"],
            mode="lines+markers",
            name="Predicted",
            line=dict(color="#ef6c00", width=2, dash="dash"),
        )
    )
    fig_holdout.update_layout(height=360, xaxis_title="Year", yaxis_title="Anomaly (C)", template="plotly_white")
    st.plotly_chart(fig_holdout, width="stretch")

    if result["feature_importance"] is not None:
        st.markdown("### Model explainability")
        imp = result["feature_importance"].head(12).sort_values(ascending=True)
        fig_imp = go.Figure(go.Bar(x=imp.values, y=imp.index, orientation="h", marker_color="#00897b"))
        fig_imp.update_layout(height=400, xaxis_title="Relative influence", yaxis_title="Feature", template="plotly_white")
        st.plotly_chart(fig_imp, width="stretch")

st.markdown("### Forecast with uncertainty")
fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(x=anomaly.index.year, y=anomaly.values, mode="lines", name="Historical anomaly", line=dict(color="#1e88e5", width=2)))
fig_fc.add_trace(go.Scatter(x=forecast_df["year"], y=forecast_df["p50"], mode="lines", name="Median forecast", line=dict(color="#d81b60", width=2)))
fig_fc.add_trace(
    go.Scatter(
        x=list(forecast_df["year"]) + list(forecast_df["year"])[::-1],
        y=list(forecast_df["p10"]) + list(forecast_df["p90"])[::-1],
        fill="toself",
        fillcolor="rgba(216,27,96,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="P10-P90 band",
    )
)
fig_fc.update_layout(height=420, xaxis_title="Year", yaxis_title="Anomaly (C)", template="plotly_white")
st.plotly_chart(fig_fc, width="stretch")

if view_mode == "Expert":
    st.markdown("### Risk-regime detection")
    color_map = {"Lower": "#2e7d32", "Elevated": "#ef6c00", "High": "#c62828"}
    fig_reg = go.Figure()
    for regime, color in color_map.items():
        chunk = regime_df[regime_df["regime"] == regime]
        fig_reg.add_trace(
            go.Scatter(x=chunk["year"], y=chunk["mean10"], mode="markers", marker=dict(color=color, size=8), name=f"{regime} regime")
        )
    fig_reg.update_layout(height=360, xaxis_title="Year", yaxis_title="10-year mean anomaly (C)", template="plotly_white")
    st.plotly_chart(fig_reg, width="stretch")

st.markdown("### AI narrative summary")
st.write(build_ai_brief(best_name, best_rmse, str(latest["regime"]), p50_2035))

st.markdown("### GenAI Studio")
length_pref = st.selectbox("Response length", ["Short", "Medium", "Detailed"], index=1)
length_range = {"Short": (70, 120), "Medium": (100, 180), "Detailed": (160, 260)}
min_w, max_w = length_range[length_pref]

cx1, cx2, cx3 = st.columns(3)
with cx1:
    if st.button("Generate Policy Brief"):
        brief, mode, note = generate_policy_brief(context)
        st.session_state.genai_last_text = brief
        (st.success if mode == "llm" else st.info)(note if mode == "llm" else f"Fallback mode: {note}")
with cx2:
    if st.button("Generate Executive 3-Block"):
        brief, mode, note = generate_genai_brief(
            section_title="Executive climate summary",
            objective="Return exactly 3 titled blocks: Current Signal, Key Risks, Priority Actions.",
            context=context,
            min_words=min_w,
            max_words=max_w,
        )
        st.session_state.genai_last_text = brief
        (st.success if mode == "llm" else st.info)(note if mode == "llm" else f"Fallback mode: {note}")
with cx3:
    if st.button("Generate Public Message"):
        brief, mode, note = generate_genai_brief(
            section_title="Public communication draft",
            objective="Explain findings for citizens in clear language and include uncertainty caution.",
            context=context,
            min_words=min_w,
            max_words=max_w,
        )
        st.session_state.genai_last_text = brief
        (st.success if mode == "llm" else st.info)(note if mode == "llm" else f"Fallback mode: {note}")

st.markdown("### Ask GenAI")
user_question = st.text_input("Ask from current analysis context", placeholder="What should city planners prioritize by 2035?")
if st.button("Ask") and user_question.strip():
    q_context = dict(context)
    q_context["question"] = user_question.strip()
    answer, mode, note = generate_genai_brief(
        section_title="Context-aware question answering",
        objective="Answer the question directly using provided model context.",
        context=q_context,
        min_words=80,
        max_words=150,
    )
    st.session_state.genai_last_text = answer
    (st.success if mode == "llm" else st.info)(note if mode == "llm" else f"Fallback mode: {note}")

if st.session_state.genai_last_text:
    st.markdown("### Latest GenAI Output")
    st.write(st.session_state.genai_last_text)
    st.download_button(
        "Download GenAI output (.txt)",
        data=st.session_state.genai_last_text,
        file_name="genai_output.txt",
        mime="text/plain",
    )

st.caption(
    "Guardrail: this output is decision-support only. Use local expertise and governance checks before policy decisions."
)
