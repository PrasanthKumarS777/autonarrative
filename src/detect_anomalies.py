import pandas as pd
import numpy as np
import sqlite3
import logging
import os
from prophet import Prophet

# Using the same log file as ingest.py so all pipeline activity is in one place
logging.basicConfig(
    filename="logs/autonarrative.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Suppressing Prophet's internal progress messages so our output stays clean
import cmdstanpy
import warnings
warnings.filterwarnings("ignore")
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

DB_PATH = "data/processed/novatech.db"

def load_from_sqlite():
    # Load the cleaned and validated data from SQLite that was stored by ingest.py
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM kpi_data", conn, parse_dates=["date"])
    conn.close()
    print("Data loaded from SQLite:", len(df), "records")
    logging.info("Data loaded from SQLite for anomaly detection")
    return df

def detect_zscore_anomalies(series, column_name, threshold=2.5):
    # Z-score method detects anomalies by measuring how far each value is
    # from the mean in terms of standard deviations
    # A threshold of 2.5 means anything beyond 2.5 standard deviations is flagged
    # This is a fast and interpretable method - easy to explain in interviews
    
    mean = series.mean()
    std = series.std()
    
    # Calculate z-score for each data point
    z_scores = (series - mean) / std
    
    # Flag as anomaly if absolute z-score exceeds threshold
    anomaly_flags = z_scores.abs() > threshold
    
    print("Z-score anomalies detected in", column_name, ":", anomaly_flags.sum())
    logging.info("Z-score detected " + str(anomaly_flags.sum()) + " anomalies in " + column_name)
    
    return anomaly_flags, z_scores

def detect_prophet_anomalies(df, column_name, interval_width=0.95):
    # Prophet is a time series forecasting model developed by Facebook/Meta
    # It models trend, weekly seasonality, and yearly seasonality automatically
    # We use it to forecast what the value SHOULD have been
    # If actual value falls outside the confidence interval, it is flagged as anomaly
    # This method is better than Z-score for catching gradual trend deviations

    # Prophet requires columns to be named ds for date and y for the value
    prophet_df = df[["date", column_name]].rename(columns={"date": "ds", column_name: "y"})

    # Initialize Prophet model with yearly seasonality on
    # We disable weekly and daily seasonality since our data is weekly
    model = Prophet(
        interval_width=interval_width,
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    # Fit the model on the full dataset
    model.fit(prophet_df)

    # Ask Prophet to forecast on the same historical dates
    # This gives us upper and lower bounds for what was expected
    forecast = model.predict(prophet_df)

    # An anomaly is when the actual value is outside the predicted confidence interval
    actual = prophet_df["y"].values
    lower = forecast["yhat_lower"].values
    upper = forecast["yhat_upper"].values

    # Flag as anomaly if actual is below lower bound or above upper bound
    anomaly_flags = (actual < lower) | (actual > upper)

    print("Prophet anomalies detected in", column_name, ":", anomaly_flags.sum())
    logging.info("Prophet detected " + str(anomaly_flags.sum()) + " anomalies in " + column_name)

    return pd.Series(anomaly_flags, index=df.index), forecast

def run_anomaly_detection():
    # Load data from database
    df = load_from_sqlite()

    # We run anomaly detection on these three KPIs as they are the most business-critical
    kpis_to_check = ["revenue", "active_users", "churn_rate"]

    # This dictionary will store all anomaly results for each KPI
    anomaly_results = {}

    for kpi in kpis_to_check:
        print("Running anomaly detection on:", kpi)

        # Run Z-score detection for this KPI
        zscore_flags, z_scores = detect_zscore_anomalies(df[kpi], kpi)

        # Run Prophet detection for this KPI
        prophet_flags, forecast = detect_prophet_anomalies(df, kpi)

        # Combine both methods using OR logic
        # If either method flags a point as anomaly we keep it
        # Using both methods together reduces false negatives (missed anomalies)
        combined_flags = zscore_flags | prophet_flags

        # Store results for this KPI
        anomaly_results[kpi] = {
            "zscore_flags": zscore_flags,
            "z_scores": z_scores,
            "prophet_flags": prophet_flags,
            "combined_flags": combined_flags,
            "forecast": forecast
        }

        print("Combined anomalies for", kpi, ":", combined_flags.sum())

    # Build a summary dataframe that shows all anomalies across all KPIs in one place
    summary_df = df[["date", "revenue", "active_users", "churn_rate"]].copy()

    for kpi in kpis_to_check:
        # Adding a column for each KPI showing True if that week was anomalous
        summary_df[kpi + "_anomaly"] = anomaly_results[kpi]["combined_flags"].values
        summary_df[kpi + "_zscore"] = anomaly_results[kpi]["z_scores"].values

    # Filter to only rows where at least one KPI was flagged as anomaly
    anomaly_weeks = summary_df[
        summary_df["revenue_anomaly"] |
        summary_df["active_users_anomaly"] |
        summary_df["churn_rate_anomaly"]
    ].copy()

    # Save anomaly summary to processed folder for use by narrative engine
    os.makedirs("data/processed", exist_ok=True)
    anomaly_weeks.to_csv("data/processed/anomaly_summary.csv", index=False)

    print("Total anomalous weeks detected:", len(anomaly_weeks))
    print("Anomaly summary saved to data/processed/anomaly_summary.csv")
    logging.info("Anomaly detection completed. Total anomalous weeks: " + str(len(anomaly_weeks)))

    return summary_df, anomaly_weeks, anomaly_results

if __name__ == "__main__":
    summary_df, anomaly_weeks, anomaly_results = run_anomaly_detection()
    print(anomaly_weeks[["date", "revenue", "revenue_anomaly", "active_users_anomaly", "churn_rate_anomaly"]])
