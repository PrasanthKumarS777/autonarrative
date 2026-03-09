import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Setting a fixed random seed so results are reproducible every time we run this script
np.random.seed(42)

def generate_kpi_data():
    # Define the starting date of our dataset - first Monday of 2023
    start_date = datetime(2023, 1, 2)
    
    # We are generating 104 weeks which equals exactly 2 years of weekly data
    weeks = 104
    
    # Create a list of weekly dates starting from start_date
    dates = [start_date + timedelta(weeks=i) for i in range(weeks)]

    # Initialize empty lists to store each KPI column
    revenue = []
    active_users = []
    churn_rate = []
    cac = []
    conversion_rate = []

    # These are the realistic baseline values for a mid-size SaaS company
    # Revenue starts at 500k per week
    base_revenue = 5000000
    # Active users starts at 12000
    base_users = 12000
    # Churn rate starts at 4.5 percent
    base_churn = 0.045
    # Customer Acquisition Cost starts at $120
    base_cac = 8500
    # Conversion rate starts at 3.2 percent
    base_conversion = 0.032

    for i in range(weeks):
        # Adding a 0.3 percent weekly organic growth trend to revenue to simulate business growth
        # Adding random noise with normal distribution to make data look realistic
        week_revenue = base_revenue * (1 + 0.003 * i) + np.random.normal(0, 15000)
        
        # Adding a 0.2 percent weekly growth to users with small random noise
        week_users = base_users * (1 + 0.002 * i) + np.random.normal(0, 300)
        
        # Churn rate stays roughly flat with small random weekly fluctuations
        week_churn = base_churn + np.random.normal(0, 0.002)
        
        # CAC stays roughly flat with small random weekly fluctuations
        week_cac = base_cac + np.random.normal(0, 5)
        
        # Conversion rate stays roughly flat with small random weekly fluctuations
        week_conversion = base_conversion + np.random.normal(0, 0.001)

        # ANOMALY 1 - Pricing change event at week 20
        # When the company increased prices, revenue spiked but churn and conversion were hurt
        if i == 20:
            week_revenue *= 1.45
            week_conversion *= 0.72
            week_churn *= 1.6

        # ANOMALY 2 - Marketing campaign failure at week 45
        # A failed paid campaign caused revenue drop, user decline and wasted ad spend (high CAC)
        if i == 45:
            week_revenue *= 0.68
            week_users *= 0.88
            week_cac *= 1.75

        # ANOMALY 3 - Seasonal holiday slowdown at week 72
        # Business activity dropped during end of year holiday period
        if i == 72:
            week_revenue *= 0.78
            week_users *= 0.82
            week_conversion *= 0.65

        # ANOMALY 4 - Viral product feature launch at week 88
        # A new feature went viral causing a strong positive spike across all KPIs
        if i == 88:
            week_revenue *= 1.62
            week_users *= 1.38
            week_conversion *= 1.45

        # Appending final values to lists, using max() to prevent any negative values
        revenue.append(round(max(week_revenue, 0), 2))
        active_users.append(int(max(week_users, 0)))
        churn_rate.append(round(max(week_churn, 0.001), 4))
        cac.append(round(max(week_cac, 0), 2))
        conversion_rate.append(round(max(week_conversion, 0.001), 4))

    # Combining all lists into a single pandas DataFrame
    df = pd.DataFrame({
        "date": dates,
        "revenue": revenue,
        "active_users": active_users,
        "churn_rate": churn_rate,
        "cac": cac,
        "conversion_rate": conversion_rate,
        "company": "NovaTech Solutions Pvt. Ltd."
    })

    return df

if __name__ == "__main__":
    # Create the data/raw folder if it does not already exist
    os.makedirs("data/raw", exist_ok=True)
    
    # Call the function to generate the dataset
    df = generate_kpi_data()
    
    # Save the dataset as a CSV file in the data/raw folder
    df.to_csv("data/raw/novatech_kpi.csv", index=False)
    
    # Print confirmation and summary statistics for verification
    print("Dataset created successfully")
    print("Total weekly records:", len(df))
    print("Date range:", df["date"].min(), "to", df["date"].max())
    print("Revenue range: $", df["revenue"].min(), "to $", df["revenue"].max())
    print("Anomalies injected at weeks: 20, 45, 72, 88")
    print(df.head())
