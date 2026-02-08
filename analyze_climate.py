import pandas as pd
import numpy as np


def analyze_climate_data(file_path):
    df = pd.read_csv(file_path)
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df = df.dropna(subset=["dt", "LandAndOceanAverageTemperature"])
    df = df.set_index("dt")

    annual = df["LandAndOceanAverageTemperature"].resample("YE").mean()

    baseline = annual.loc["1850":"1900"].mean()
    anomaly = annual - baseline

    recent = anomaly.tail(30)
    x = np.arange(len(recent))
    slope, _ = np.polyfit(x, recent.values, 1)

    print("Baseline (1850–1900):", round(baseline, 3))
    print("Current anomaly:", round(anomaly.iloc[-1], 3))
    print("Warming rate:", round(slope * 10, 3), "°C/decade")

    print("\nTop 5 warmest years:")
    print(anomaly.sort_values(ascending=False).head())

    years = anomaly.index.year.values
    temps = anomaly.values

    if len(years) > 10:
        samples = 300
        preds = []
        for _ in range(samples):
            resample_idx = np.random.choice(len(years), len(years), replace=True)
            x_sample = years[resample_idx]
            y_sample = temps[resample_idx]
            boot_slope, boot_intercept = np.polyfit(x_sample, y_sample, 1)
            preds.append(boot_slope * years + boot_intercept)
        preds = np.vstack(preds)
        low = np.percentile(preds, 5, axis=0)
        high = np.percentile(preds, 95, axis=0)
        print("\nBootstrap 90% band at latest year:", round(low[-1], 3), "to", round(high[-1], 3))

    candidate_years = np.arange(1910, 2010)
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

    if best_year:
        print("\nMost likely acceleration shift year:", best_year)


if __name__ == "__main__":
    analyze_climate_data("GlobalTemperatures.csv")