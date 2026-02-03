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

if __name__ == "__main__":
    analyze_climate_data("GlobalTemperatures.csv")
