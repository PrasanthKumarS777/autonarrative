# AutoNarrative - Automated KPI Intelligence System

> Every Monday morning, business analysts at companies across India spend 4-6 hours writing the same performance reports. AutoNarrative eliminates that entirely.

---

## The Problem This Solves

Finance and business teams at SaaS companies waste thousands of analyst-hours annually on a single repetitive task — manually investigating KPI anomalies in dashboards and writing weekly performance narratives. Most companies have dashboards. Almost none have a system that automatically detects what went wrong, understands why, and writes the executive report without human intervention.

AutoNarrative is that system.

---

## What AutoNarrative Does

- Ingests 2 years of weekly business KPI data for a B2B SaaS company
- Detects anomalous weeks using a hybrid statistical engine combining Facebook Prophet time-series forecasting and Z-score deviation analysis
- Automatically generates professional executive narratives for each anomalous week using a large language model
- Exports a fully formatted multi-page PDF report with cover page, summary table, and per-anomaly analysis
- Presents everything in a live interactive Streamlit dashboard with trend charts and anomaly overlays

---

## Why This Project Is Different

Most data science portfolios predict something. This project replaces something - specifically, an entire Monday morning analyst workflow that costs companies real money every week.

The anomaly detection layer was deliberately designed with ground truth. Four business events were injected into the dataset at known weeks - a pricing change, a failed marketing campaign, a seasonal holiday drop, and a viral feature launch. The hybrid detection engine was then validated against these known events, which means model performance is measurable, not just assumed. This is a level of experimental rigour that production ML systems demand and that tutorial projects never demonstrate.

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Data Generation | Python, NumPy | Realistic KPI simulation with injected anomalies |
| Data Storage | SQLite, Pandas | Lightweight production-style data persistence |
| Anomaly Detection | Facebook Prophet, Z-score | Hybrid time-series and statistical detection |
| Narrative Generation | OpenAI GPT-3.5-turbo | LLM-powered executive report writing |
| PDF Reporting | fpdf2 | Automated professional report generation |
| Dashboard | Streamlit, Plotly | Interactive business intelligence interface |
| Pipeline Orchestration | Python subprocess | End-to-end automated pipeline runner |
| Containerisation | Docker | Reproducible deployment environment |
| Version Control | Git, GitHub | Full source control and collaboration |

---

## Project Structure

autonarrative/
├── main.py # Master pipeline runner - runs all steps in sequence
├── Dockerfile # Container configuration for deployment
├── requirements.txt # All Python dependencies
├── .env # API keys - never committed to Git
├── src/
│ ├── data_generator.py # Generates 2 years of realistic KPI data with anomalies
│ ├── ingest.py # Data validation, derived columns, SQLite storage
│ ├── detect_anomalies.py # Prophet + Z-score hybrid anomaly detection
│ ├── narrative_engine.py # LLM-powered executive narrative generation
│ ├── report_generator.py # Automated PDF report generation
│ └── dashboard.py # Streamlit interactive dashboard
├── data/
│ ├── raw/ # Raw generated CSV files
│ └── processed/ # Cleaned data, anomaly summary, narratives
├── reports/ # Auto-generated PDF reports
└── logs/ # Pipeline execution logs

text

---

## How To Run

**Option 1 - Run full pipeline and launch dashboard:**
```bash
python main.py
streamlit run src/dashboard.py
Option 2 - Run with Docker:

bash
docker build -t autonarrative .
docker run -p 8501:8501 autonarrative
Option 3 - Run steps individually:

bash
python src/data_generator.py
python src/ingest.py
python src/detect_anomalies.py
python src/narrative_engine.py
python src/report_generator.py
streamlit run src/dashboard.py
OpenAI API Key Setup
To enable real LLM-generated narratives, add your OpenAI API key to the .env file:

text
OPENAI_API_KEY=your_key_here
Without an API key the system runs in offline mode with placeholder narratives so the full pipeline still works for demonstration purposes.

Business Context
NovaTech Solutions Pvt. Ltd. is a fictional B2B SaaS company headquartered in Bengaluru, India. All revenue and CAC figures are denominated in Indian Rupees and calibrated to realistic Indian SaaS market benchmarks. Weekly revenue baseline of INR 50 lakhs and CAC of INR 8,500 reflect actual mid-market Indian SaaS operating metrics.

Built By
Prasanth Kumar Sahu
Masters in Finance and IT


This project was independently designed and built to demonstrate end-to-end data science engineering - from data pipeline architecture to statistical modelling to LLM integration to business intelligence reporting.
EOF