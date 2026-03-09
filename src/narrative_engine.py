import pandas as pd
import sqlite3
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Loading environment variables from .env file
# This is how we keep the API key secret and out of the code
load_dotenv()

# Setting up logging to track every narrative generation event
logging.basicConfig(
    filename="logs/autonarrative.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Reading the OpenAI API key from the .env file
# Never hardcode API keys directly in code - this is a critical security practice
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def load_data():
    # Load the full KPI dataset from SQLite so we have all columns
    # We use SQLite as the source of truth because anomaly_summary.csv only has a subset of columns
    conn = sqlite3.connect("data/processed/novatech.db")
    full_df = pd.read_sql("SELECT * FROM kpi_data", conn, parse_dates=["date"])
    conn.close()

    # Load the anomaly flags from the anomaly summary CSV
    anomaly_flags_df = pd.read_csv("data/processed/anomaly_summary.csv", parse_dates=["date"])

    # Merge the full dataset with anomaly flags so each row has all KPI columns plus anomaly flags
    # We merge on date so every anomalous week gets its full set of KPI values
    merged_df = pd.merge(
        anomaly_flags_df,
        full_df[["date", "cac", "conversion_rate"]],
        on="date",
        how="left"
    )

    # Filter to only the anomalous weeks for narrative generation
    anomaly_weeks = merged_df[
        merged_df["revenue_anomaly"] |
        merged_df["active_users_anomaly"] |
        merged_df["churn_rate_anomaly"]
    ].copy()

    print("Full dataset loaded:", len(full_df), "records")
    print("Anomalous weeks loaded:", len(anomaly_weeks))
    logging.info("Loaded " + str(len(anomaly_weeks)) + " anomalous weeks for narrative generation")

    return full_df, anomaly_weeks


def build_prompt(row, full_df):
    # This function builds the prompt we send to the OpenAI model
    # A well structured prompt is critical to getting a high quality business narrative
    # We give the model context about what happened and what the surrounding trend looked like

    date_str = row["date"].strftime("%B %d, %Y")

    # Get the 4 weeks before this anomaly for context
    # This helps the LLM understand what normal looked like before the anomaly
    row_index = full_df[full_df["date"] == row["date"]].index[0]
    start_index = max(0, row_index - 4)
    prior_weeks = full_df.iloc[start_index:row_index]

    # Calculate average values from prior weeks as baseline
    avg_revenue = prior_weeks["revenue"].mean() if len(prior_weeks) > 0 else row["revenue"]
    avg_users = prior_weeks["active_users"].mean() if len(prior_weeks) > 0 else row["active_users"]
    avg_churn = prior_weeks["churn_rate"].mean() if len(prior_weeks) > 0 else row["churn_rate"]

    # Build a clear description of what was anomalous this week
    anomaly_description = []

    if row["revenue_anomaly"]:
        revenue_change = ((row["revenue"] - avg_revenue) / avg_revenue) * 100
        direction = "increased" if revenue_change > 0 else "decreased"
        anomaly_description.append(
            "Revenue " + direction + " by " + str(round(abs(revenue_change), 1)) +
            "% compared to the prior 4-week average of $" + str(round(avg_revenue, 0))
        )

    if row["active_users_anomaly"]:
        users_change = ((row["active_users"] - avg_users) / avg_users) * 100
        direction = "increased" if users_change > 0 else "decreased"
        anomaly_description.append(
            "Active users " + direction + " by " + str(round(abs(users_change), 1)) +
            "% compared to the prior 4-week average of " + str(round(avg_users, 0))
        )

    if row["churn_rate_anomaly"]:
        churn_change = ((row["churn_rate"] - avg_churn) / avg_churn) * 100
        direction = "increased" if churn_change > 0 else "decreased"
        anomaly_description.append(
            "Churn rate " + direction + " by " + str(round(abs(churn_change), 1)) +
            "% compared to the prior 4-week average of " + str(round(avg_churn * 100, 2)) + "%"
        )

    anomaly_text = ". ".join(anomaly_description)

    # This is the prompt template we send to the OpenAI model
    # We are asking it to act as a senior business analyst and write a professional narrative
    prompt = """
You are a senior business analyst at NovaTech Solutions Pvt. Ltd., a B2B SaaS company headquartered in Bengaluru, India.
Write a concise executive narrative report for the week of {date}.

Observed anomalies this week:
{anomalies}

Current week metrics:
- Revenue: INR {revenue}
- Active Users: {users}
- Churn Rate: {churn}%
- CAC: INR {cac}
- Conversion Rate: {conversion}%

Instructions:
1. Write 3 to 4 sentences in plain professional English
2. State clearly what happened and how significant the change was
3. Suggest the most likely business reason for this anomaly
4. Recommend one specific action the business team should take
5. Do not use bullet points - write in paragraph format only
""".format(
        date=date_str,
        anomalies=anomaly_text,
        revenue=round(row["revenue"], 0),
        users=row["active_users"],
        churn=round(row["churn_rate"] * 100, 2),
        cac=round(row["cac"], 0),
        conversion=round(row["conversion_rate"] * 100, 2)
    )

    return prompt


def generate_narrative(prompt):
    # Initialize the OpenAI client using the API key from .env
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Calling the OpenAI chat completions API
    # We use gpt-3.5-turbo to keep costs low during development
    # In production this can be switched to gpt-4 for higher quality narratives
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a senior business analyst writing executive KPI reports. Be concise, data-driven, and actionable."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Max tokens controls the length of the response
        # 300 tokens is roughly 3 to 4 sentences which is what we want
        max_tokens=300,
        temperature=0.7
    )

    # Extract the text content from the API response
    narrative = response.choices[0].message.content.strip()
    return narrative


def run_narrative_engine():
    # Load full dataset and anomalous weeks
    full_df, anomaly_weeks = load_data()

    # This list will store all generated narratives
    narratives = []

    for index, row in anomaly_weeks.iterrows():
        print("Generating narrative for week:", row["date"].strftime("%Y-%m-%d"))

        # Build the prompt for this anomalous week using full_df for context
        prompt = build_prompt(row, full_df)

        # Check if API key is available before calling OpenAI
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            # If no API key is set we use a placeholder narrative for testing
            # This allows the rest of the pipeline to work without an API key
            narrative = (
                "Week of " + row["date"].strftime("%B %d, %Y") + ": " +
                "Significant anomaly detected in business KPIs. " +
                "Revenue and user metrics deviated substantially from the 4-week baseline. " +
                "Business team should investigate pricing, campaign, and product changes during this period."
            )
            print("No API key found - using placeholder narrative")
        else:
            # Generate narrative using OpenAI API
            narrative = generate_narrative(prompt)
            print("Narrative generated successfully")

        narratives.append({
            "date": row["date"],
            "revenue": row["revenue"],
            "active_users": row["active_users"],
            "churn_rate": row["churn_rate"],
            "revenue_anomaly": row["revenue_anomaly"],
            "active_users_anomaly": row["active_users_anomaly"],
            "churn_rate_anomaly": row["churn_rate_anomaly"],
            "narrative": narrative
        })

        logging.info("Narrative generated for week " + str(row["date"]))

    # Save all narratives to CSV
    narratives_df = pd.DataFrame(narratives)
    narratives_df.to_csv("data/processed/narratives.csv", index=False)

    print("All narratives generated and saved to data/processed/narratives.csv")
    print("Total narratives:", len(narratives_df))
    logging.info("Narrative engine completed. Total narratives: " + str(len(narratives_df)))

    return narratives_df


if __name__ == "__main__":
    narratives_df = run_narrative_engine()
    if len(narratives_df) > 0:
        print("Sample narrative:")
        print(narratives_df.iloc[0]["narrative"])
