from __future__ import annotations

import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def load_annual_anomaly(csv_path: str = "GlobalTemperatures.csv") -> pd.Series:
    df = pd.read_csv(csv_path)
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    df = df.set_index("dt")
    annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()
    baseline = annual.loc["1850":"1900"].mean()
    anomaly = annual - baseline
    return anomaly.dropna()


def _feature_vector(history: np.ndarray, lags: int) -> np.ndarray:
    lag_values = [history[-k] for k in range(1, lags + 1)]

    win5 = history[-5:] if len(history) >= 5 else history
    win10 = history[-10:] if len(history) >= 10 else history

    rolling_mean_5 = float(np.mean(win5))
    rolling_std_5 = float(np.std(win5))
    rolling_mean_10 = float(np.mean(win10))
    rolling_std_10 = float(np.std(win10))

    if len(win10) >= 2:
        x = np.arange(len(win10))
        trend_10 = float(np.polyfit(x, win10, 1)[0])
    else:
        trend_10 = 0.0

    momentum_3 = float(history[-1] - np.mean(history[-3:])) if len(history) >= 3 else 0.0

    return np.array(
        lag_values
        + [rolling_mean_5, rolling_std_5, rolling_mean_10, rolling_std_10, trend_10, momentum_3],
        dtype=float,
    )


def build_supervised_dataset(anomaly: pd.Series, lags: int = 8):
    values = anomaly.values.astype(float)
    years = anomaly.index.year.values

    if len(values) <= lags + 10:
        raise ValueError("Not enough data to build features. Reduce lags or provide more data.")

    feature_names = [f"lag_{k}" for k in range(1, lags + 1)] + [
        "rolling_mean_5",
        "rolling_std_5",
        "rolling_mean_10",
        "rolling_std_10",
        "trend_10",
        "momentum_3",
    ]

    X_rows, y_rows, y_years = [], [], []
    for i in range(lags, len(values)):
        history = values[:i]
        X_rows.append(_feature_vector(history, lags))
        y_rows.append(values[i])
        y_years.append(years[i])

    X = pd.DataFrame(X_rows, columns=feature_names)
    y = pd.Series(y_rows, name="target_anomaly")
    y_years = np.array(y_years)

    return X, y, y_years, feature_names


def _candidate_models() -> dict:
    fast_mode = os.getenv("FAST_MODE", "1").strip().lower() in {"1", "true", "yes", "on"}
    rf_estimators = 140 if fast_mode else 300
    gb_estimators = 110 if fast_mode else 220

    return {
        "Ridge": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", Ridge(alpha=1.0)),
            ]
        ),
        "ElasticNet": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", ElasticNet(alpha=0.02, l1_ratio=0.5, random_state=42, max_iter=5000)),
            ]
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=rf_estimators,
            random_state=42,
            min_samples_leaf=2,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            random_state=42,
            n_estimators=gb_estimators,
            learning_rate=0.05,
            max_depth=3,
        ),
    }


def _walk_forward_cv_rmse(model, X_train: pd.DataFrame, y_train: pd.Series, splits: int = 5) -> float:
    usable_splits = min(splits, max(2, len(X_train) // 20))
    tscv = TimeSeriesSplit(n_splits=usable_splits)

    fold_rmses = []
    for train_idx, val_idx in tscv.split(X_train):
        x_tr, x_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        model.fit(x_tr, y_tr)
        pred = model.predict(x_val)
        fold_rmses.append(float(np.sqrt(mean_squared_error(y_val, pred))))

    return float(np.mean(fold_rmses)) if fold_rmses else np.inf


def _extract_feature_importance(model, feature_names: list[str]) -> pd.Series | None:
    estimator = model.named_steps["model"] if hasattr(model, "named_steps") else model

    if hasattr(estimator, "coef_"):
        vals = np.abs(estimator.coef_)
        return pd.Series(vals, index=feature_names).sort_values(ascending=False)

    if hasattr(estimator, "feature_importances_"):
        vals = estimator.feature_importances_
        return pd.Series(vals, index=feature_names).sort_values(ascending=False)

    return None


def train_and_evaluate(
    anomaly: pd.Series,
    lags: int = 8,
    test_years: int = 20,
    cv_splits: int = 3,
):
    X, y, y_years, feature_names = build_supervised_dataset(anomaly, lags=lags)

    if len(X) <= test_years + 20:
        raise ValueError("Not enough rows for robust train/test split. Reduce test_years or lags.")

    split = len(X) - test_years
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    years_test = y_years[split:]

    candidates = _candidate_models()
    metrics = {}
    fitted = {}

    for name, model in candidates.items():
        cv_rmse = _walk_forward_cv_rmse(model, X_train, y_train, splits=cv_splits)

        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        holdout_rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        holdout_mae = float(mean_absolute_error(y_test, pred))
        holdout_r2 = float(r2_score(y_test, pred))

        selection_score = 0.6 * cv_rmse + 0.4 * holdout_rmse

        metrics[name] = {
            "cv_rmse": cv_rmse,
            "rmse": holdout_rmse,
            "mae": holdout_mae,
            "r2": holdout_r2,
            "selection_score": selection_score,
        }
        fitted[name] = {"model": model, "pred": pred}

    best_name = min(metrics, key=lambda n: metrics[n]["selection_score"])
    best_model = candidates[best_name]
    best_model.fit(X, y)

    holdout_pred = fitted[best_name]["pred"]
    residuals = (y_test.values - holdout_pred).astype(float)

    return {
        "metrics": metrics,
        "best_model_name": best_name,
        "best_model": best_model,
        "feature_names": feature_names,
        "feature_importance": _extract_feature_importance(best_model, feature_names),
        "years_test": years_test,
        "y_test": y_test.values.astype(float),
        "holdout_pred": holdout_pred.astype(float),
        "residuals": residuals,
    }


def forecast_with_uncertainty(
    model,
    anomaly: pd.Series,
    lags: int,
    horizon: int = 30,
    residuals: np.ndarray | None = None,
    simulations: int = 400,
    seed: int = 42,
) -> pd.DataFrame:
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    history = anomaly.values.astype(float).tolist()
    last_year = int(anomaly.index.year[-1])
    future_years = np.arange(last_year + 1, last_year + horizon + 1)

    baseline_forecast = []
    for _ in range(horizon):
        x = _feature_vector(np.array(history, dtype=float), lags).reshape(1, -1)
        y_hat = float(model.predict(x)[0])
        baseline_forecast.append(y_hat)
        history.append(y_hat)

    rng = np.random.default_rng(seed)
    residuals = residuals if residuals is not None and len(residuals) > 3 else np.array([0.0])

    sims = np.zeros((simulations, horizon), dtype=float)
    for s in range(simulations):
        h = anomaly.values.astype(float).tolist()
        for t in range(horizon):
            x = _feature_vector(np.array(h, dtype=float), lags).reshape(1, -1)
            y_hat = float(model.predict(x)[0])
            y_sim = y_hat + float(rng.choice(residuals))
            sims[s, t] = y_sim
            h.append(y_sim)

    p10 = np.percentile(sims, 10, axis=0)
    p50 = np.percentile(sims, 50, axis=0)
    p90 = np.percentile(sims, 90, axis=0)

    return pd.DataFrame(
        {
            "year": future_years,
            "baseline": np.array(baseline_forecast),
            "p10": p10,
            "p50": p50,
            "p90": p90,
        }
    )


def detect_risk_regimes(anomaly: pd.Series, clusters: int = 3) -> pd.DataFrame:
    clusters = max(3, clusters)

    base = pd.DataFrame(
        {
            "year": anomaly.index.year.values,
            "anomaly": anomaly.values.astype(float),
        }
    )

    base["mean10"] = base["anomaly"].rolling(10).mean()
    base["std10"] = base["anomaly"].rolling(10).std()
    base["rate"] = np.gradient(base["mean10"])
    base["acceleration"] = np.gradient(base["rate"])
    base = base.dropna().reset_index(drop=True)

    feat_cols = ["mean10", "std10", "rate", "acceleration"]
    X = StandardScaler().fit_transform(base[feat_cols])

    kmeans = KMeans(n_clusters=clusters, random_state=42, n_init=20)
    base["cluster"] = kmeans.fit_predict(X)

    ranked = base.groupby("cluster")["mean10"].mean().sort_values().index.tolist()
    default_labels = ["Lower", "Elevated", "High"]
    extra = [f"Very High {i}" for i in range(1, max(0, clusters - 3) + 1)]
    labels = (default_labels + extra)[:clusters]

    mapping = {cluster: labels[i] for i, cluster in enumerate(ranked)}
    base["regime"] = base["cluster"].map(mapping)

    return base


def pick_year_projection(forecast_df: pd.DataFrame, year: int) -> float:
    row = forecast_df[forecast_df["year"] == year]
    if not row.empty:
        return float(row["p50"].iloc[0])
    return float(forecast_df["p50"].iloc[-1])


def projection_rate_per_decade(anomaly: pd.Series, forecast_df: pd.DataFrame, target_year: int) -> float:
    latest = float(anomaly.iloc[-1])
    latest_year = int(anomaly.index.year[-1])
    projected = pick_year_projection(forecast_df, target_year)
    years = max(1, target_year - latest_year)
    return (projected - latest) / years * 10.0


def people_impact_summary(regime: str, lens: str) -> str:
    if lens == "Human health":
        if regime.startswith("High"):
            return "Heat-risk days likely increase; prioritize workers, elderly, and low-income households."
        if regime.startswith("Elevated"):
            return "Heat exposure risk is rising; targeted early warning and local outreach are needed."
        return "Current risk is lower, but vulnerable groups still need seasonal preparedness."

    if lens == "Food systems":
        if regime.startswith("High"):
            return "Yield volatility risk is high; diversify crops and water planning immediately."
        if regime.startswith("Elevated"):
            return "Seasonal disruption risk is increasing; strengthen buffers and extension advisories."
        return "Risk remains moderate; improve monitoring and drought contingency plans."

    if regime.startswith("High"):
        return "Infrastructure stress is high; stress-test grids, transport, and cooling load capacity."
    if regime.startswith("Elevated"):
        return "Thermal stress is increasing; phase retrofits for critical assets first."
    return "Lower signal currently; maintain resilience upgrades in high-exposure zones."


def build_ai_brief(best_model_name: str, best_rmse: float, latest_regime: str, p50_2035: float) -> str:
    return (
        f"AI/ML summary: Best model = {best_model_name}; holdout RMSE = {best_rmse:.3f} C. "
        f"Latest unsupervised regime = '{latest_regime}'. "
        f"Median projected anomaly around 2035 = {p50_2035:.2f} C (vs 1850-1900 baseline)."
    )
