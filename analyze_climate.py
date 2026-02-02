import pandas as pd
import numpy as np

def analyze_climate_data(file_path):
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Parse dates
    df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
    
    # Check for missing dates and fill them if they are sequential
    if df['dt'].isnull().any():
        print("Found missing dates. Attempting to infer them...")
        # Find the last valid date index
        last_valid_idx = df['dt'].last_valid_index()
        if last_valid_idx is not None:
            last_valid_date = df.loc[last_valid_idx, 'dt']
            print(f"Last valid date: {last_valid_date}")
            
            # Generate new dates starting from the next month
            missing_count = len(df) - (last_valid_idx + 1)
            if missing_count > 0:
                new_dates = pd.date_range(start=last_valid_date + pd.DateOffset(months=1), periods=missing_count, freq='MS')
                df.loc[last_valid_idx+1:, 'dt'] = new_dates
                print(f"Filled {missing_count} missing dates up to {new_dates[-1]}")
    
    # Drop rows with invalid dates (if any remain)
    df = df.dropna(subset=['dt'])
    
    # Set index
    df = df.set_index('dt')
    
    # Focus on LandAndOceanAverageTemperature
    target_col = 'LandAndOceanAverageTemperature'
    if target_col not in df.columns:
        print(f"Column {target_col} not found.")
        return

    # Filter out missing values for the target column
    df_clean = df.dropna(subset=[target_col])
    
    print(f"Data range: {df_clean.index.min()} to {df_clean.index.max()}")
    print(f"Total valid months: {len(df_clean)}")

    # Resample to annual frequency, but count observations first
    df_counts = df_clean[[target_col]].resample('YE').count()
    df_annual = df_clean[[target_col]].resample('YE').mean()
    
    # Filter out years with incomplete data (< 12 months)
    valid_years = df_counts[df_counts[target_col] >= 12].index
    print(f"Dropping incomplete years: {len(df_annual) - len(valid_years)} years dropped.")
    df_annual = df_annual.loc[valid_years]
    
    # Calculate baseline (1850-1900)
    baseline_start = '1850-01-01'
    baseline_end = '1900-12-31'
    
    baseline_mask = (df_annual.index >= baseline_start) & (df_annual.index <= baseline_end)
    baseline_mean = df_annual.loc[baseline_mask, target_col].mean()
    
    print(f"Baseline ({baseline_start[:4]}-{baseline_end[:4]}) mean: {baseline_mean:.4f}")
    
    # Calculate anomalies
    df_annual['anomaly'] = df_annual[target_col] - baseline_mean
    
    # Recent trend (last 30 years)
    last_year = df_annual.index.max().year
    start_trend_year = last_year - 30
    
    recent_data = df_annual[df_annual.index.year > start_trend_year]
    
    # Linear regression for trend
    if len(recent_data) > 1:
        x = np.arange(len(recent_data))
        y = recent_data['anomaly'].values
        slope, intercept = np.polyfit(x, y, 1)
        print(f"Trend over last 30 years ({start_trend_year+1}-{last_year}): {slope*10:.4f} °C/decade")
    
    # Top 5 warmest years
    print("\nTop 5 warmest years (anomaly vs 1850-1900):")
    top_5 = df_annual.sort_values('anomaly', ascending=False).head(5)
    for date, row in top_5.iterrows():
        print(f"{date.year}: {row['anomaly']:.4f} °C")

    # Decadal averages
    print("\nDecadal Averages (Anomaly):")
    df_annual['decade'] = (df_annual.index.year // 10) * 10
    decadal = df_annual.groupby('decade')['anomaly'].mean()
    print(decadal.tail(5))

    # Check uncertainty if available
    uncertainty_col = 'LandAndOceanAverageTemperatureUncertainty'
    if uncertainty_col in df.columns:
        recent_uncertainty = df[df.index.year >= 2000][uncertainty_col].mean()
        print(f"\nAverage uncertainty since 2000: {recent_uncertainty:.4f} °C")

if __name__ == "__main__":
    analyze_climate_data('GlobalTemperatures.csv')
