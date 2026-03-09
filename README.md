# AutoNarrative — Automated KPI Intelligence System

> Every Monday morning, business analysts at SaaS companies across India spend 4–6 hours writing the same performance reports. **AutoNarrative eliminates that entirely** — automatically detecting anomalies, understanding context, and writing the executive report with zero human intervention.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red?logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-412991?logo=openai&logoColor=white)
![Prophet](https://img.shields.io/badge/Prophet-1.1.5-0078D4)
![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

- [The Problem](#the-problem)
- [What AutoNarrative Does](#what-autonarrative-does)
- [System Architecture](#system-architecture)
- [Anomaly Detection Engine](#anomaly-detection-engine)
- [Narrative Generation](#narrative-generation)
- [PDF Report](#pdf-report)
- [Interactive Dashboard](#interactive-dashboard)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Data Validation](#data-validation)
- [Business Context](#business-context)

---

## The Problem

Finance and BI teams at growing SaaS companies face a silent productivity crisis. Every week, skilled analysts are pulled away from strategic work to perform a mechanical task — opening dashboards, scanning KPI movements, investigating what changed, and writing narrative summaries for leadership.

| Pain Point | Impact |
|---|---|
| ⏱️ Time-consuming | 4–6 hours per analyst, every single week |
| 📉 Inconsistent quality | Depends on who writes it and how much time they have |
| 🚨 Reactive alerting | Anomalies only caught after a stakeholder escalates |
| 📈 Unscalable | Manual burden grows as KPI count increases |

Most companies have dashboards. Almost none have a system that **automatically detects what went wrong, understands the surrounding business context, and writes a professional executive report** ready for leadership consumption.

**AutoNarrative is that system.**

---

## What AutoNarrative Does

AutoNarrative is a fully automated, end-to-end data pipeline that:

- 📊 **Monitors** weekly business KPIs for a B2B SaaS company
- 🔍 **Detects** statistical anomalies using a hybrid Prophet + Z-score engine
- 🤖 **Generates** professional executive narratives using GPT-3.5-turbo
- 📄 **Exports** a formatted, multi-page PDF report
- 🖥️ **Presents** everything in an interactive Streamlit dashboard

All of this runs with **zero manual intervention**.

The system is built around **NovaTech Solutions Pvt. Ltd.**, a fictional B2B SaaS company headquartered in Bengaluru, India, with metrics calibrated to real Indian SaaS market benchmarks — including revenue in Indian Rupees and CAC benchmarks reflecting actual Indian digital marketing costs.

---

## System Architecture

```
Raw KPI Data
     │
     ▼
data_generator.py        — Generates 2 years of realistic weekly KPI data
                           with deliberately injected business anomalies
     │
     ▼
ingest.py                — Validates data quality across 6 checks,
                           adds derived columns, stores to SQLite
     │
     ▼
detect_anomalies.py      — Hybrid Prophet + Z-score anomaly detection
                           across Revenue, Active Users, and Churn Rate
     │
     ▼
narrative_engine.py      — Builds context-aware prompts, calls GPT-3.5-turbo,
                           generates executive narratives per anomaly
     │
     ▼
report_generator.py      — Generates multi-page professional PDF report
                           with cover page, summary table, and narrative pages
     │
     ▼
dashboard.py             — Streamlit interactive dashboard with KPI trend charts,
                           anomaly overlays, and narrative viewer
```

### Injected Business Events

Rather than using opaque real-world data, four business events were **deliberately injected** at known weeks — giving the detection system a measurable ground truth to validate against.

| Week | Event | KPIs Affected |
|---|---|---|
| Week 20 | Pricing change | Revenue ▲45%, Churn ▲60%, Conversion ▼28% |
| Week 45 | Marketing campaign failure | Revenue ▼32%, Users ▼12%, CAC ▲75% |
| Week 72 | Seasonal holiday slowdown | Revenue ▼22%, Users ▼18%, Conversion ▼35% |
| Week 88 | Viral feature launch | Revenue ▲62%, Users ▲38%, Conversion ▲45% |

This design means detection accuracy is **verifiable**, not assumed — every missed detection or false positive can be analysed and explained. This is the level of experimental rigour that production ML systems demand.

---

## Anomaly Detection Engine

Two complementary statistical methods are combined using **OR logic**, so neither missed anomalies nor false positives dominate.

### Facebook Prophet
A time series forecasting model that captures trend, yearly seasonality, and structural breaks. It forecasts what each KPI *should* have been in a given week based on historical patterns. Any week where the actual value falls outside the **95% confidence interval** is flagged. Particularly effective at catching gradual trend deviations.

### Z-Score Analysis
Measures how many standard deviations a data point is from the historical mean. A threshold of **2.5 standard deviations** is used to flag only extreme deviations. Fast, interpretable, and effective at catching sharp sudden spikes or drops.

### Combined Logic
```
Anomaly = Prophet_flag OR ZScore_flag
```
This hybrid approach **reduces false negatives** without significantly increasing false positives — the correct trade-off for a business alerting system where missing a real event is more costly than investigating a false alarm.

---

## Narrative Generation

For each anomalous week, the narrative engine:

1. Calculates the **4-week rolling baseline** before the anomaly to define what "normal" looked like
2. Computes **percentage deviation** from baseline for each affected KPI
3. Constructs a **structured prompt** with anomaly description, current metrics, and business context
4. Sends the prompt to **GPT-3.5-turbo** with a system role instructing it to act as a senior business analyst
5. Returns a **3–4 sentence professional narrative** with a specific recommended action

**Example output — Week 20 (Pricing Change):**

> During the week of May 22, 2023, NovaTech Solutions recorded a 45% revenue spike against the prior 4-week average, accompanied by a simultaneous 60% increase in churn rate and a 28% decline in conversion rate — a pattern strongly consistent with a recent pricing adjustment. While the short-term revenue uplift appears positive, the deterioration in churn and conversion signals that a segment of the customer base is responding negatively to the new pricing structure. It is recommended that the customer success team immediately review churned accounts from this period to identify pricing sensitivity patterns and determine whether a tiered pricing option or grandfathering policy is warranted for at-risk segments.

---

## PDF Report

The automated PDF report contains:

| Section | Contents |
|---|---|
| **Cover Page** | Company name, report title, generation date, anomaly count, system description |
| **Executive Summary Table** | One row per anomaly — date, revenue, users, churn, and anomaly flags at a glance |
| **Individual Anomaly Pages** | One full page per anomalous week with KPI metrics, flags, and the full executive narrative |

Reports are saved with a timestamp in the filename so each pipeline run produces a unique **archived report**. In production, this report would be automatically emailed to the leadership team every Monday morning.

---

## Interactive Dashboard

The Streamlit dashboard provides:

- **Live KPI metric cards** with the latest week values and week-over-week delta indicators
- **Four interactive Plotly trend charts** for Revenue, Active Users, Churn Rate, and CAC with anomaly markers overlaid as red circles
- **4-week rolling average reference lines** on each chart to show trend context
- **Expandable narrative sections** — one per anomalous week with anomaly flags, executive narrative, and week metrics
- **Full dataset table** with professional column formatting

---

## Tech Stack

| Layer | Tool | Version | Purpose |
|---|---|---|---|
| Data Engineering | Python, Pandas, NumPy | 3.11 / 2.2.2 / 1.26.4 | Data generation, transformation, validation |
| Data Storage | SQLite, SQLAlchemy | — | Lightweight production-style persistence |
| Time Series Detection | Facebook Prophet | 1.1.5 | Trend-aware anomaly detection |
| Statistical Detection | Z-Score, Scikit-learn | 1.5.0 | Deviation-based anomaly detection |
| LLM Integration | OpenAI API, GPT-3.5-turbo | openai 1.30.1 | Executive narrative generation |
| PDF Generation | fpdf2 | 2.7.9 | Automated report creation |
| Dashboard | Streamlit, Plotly | 1.35.0 / 5.22.0 | Interactive BI interface |
| Pipeline Runner | Python subprocess | — | Orchestrated end-to-end automation |
| Containerisation | Docker | — | Reproducible deployment |
| Version Control | Git, GitHub | — | Source control and collaboration |
| Environment Management | python-dotenv | 1.0.1 | Secure API key management |

---

## Project Structure

```
autonarrative/
├── main.py                          # Master pipeline runner
├── Dockerfile                       # Container configuration
├── requirements.txt                 # Python dependencies
├── .env                             # API keys — not committed to Git
├── .gitignore                       # Git exclusion rules
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py            # 2-year KPI dataset with anomaly injection
│   ├── ingest.py                    # Data validation, derived columns, SQLite ingestion
│   ├── detect_anomalies.py          # Prophet + Z-score hybrid detection engine
│   ├── narrative_engine.py          # LLM prompt construction and narrative generation
│   ├── report_generator.py          # Automated multi-page PDF report generation
│   └── dashboard.py                 # Streamlit interactive dashboard
│
├── data/
│   ├── raw/
│   │   └── novatech_kpi.csv         # Raw 2-year weekly KPI dataset
│   └── processed/
│       ├── novatech.db              # SQLite database with validated, enriched data
│       ├── anomaly_summary.csv      # Detected anomaly weeks with flags and z-scores
│       └── narratives.csv           # LLM-generated executive narratives per anomaly
│
├── reports/
│   └── autonarrative_report_*.pdf   # Auto-generated PDF reports (timestamped)
│
└── logs/
    └── autonarrative.log            # Full pipeline execution log
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Docker *(optional)*
- OpenAI API key *(optional — system runs in offline mode without it)*

---

### Option 1 — Full pipeline + dashboard

```bash
git clone https://github.com/PrasanthKumarS777/autonarrative.git
cd autonarrative
python -m venv venv
source venv/Scripts/activate        # Windows
# source venv/bin/activate          # macOS/Linux
pip install -r requirements.txt
python main.py
streamlit run src/dashboard.py
```

### Option 2 — Docker

```bash
docker build -t autonarrative .
docker run -p 8501:8501 autonarrative
```

### Option 3 — Run pipeline steps individually

```bash
python src/data_generator.py
python src/ingest.py
python src/detect_anomalies.py
python src/narrative_engine.py
python src/report_generator.py
streamlit run src/dashboard.py
```

---

### OpenAI API Key Configuration

Add your key to the `.env` file:

```
OPENAI_API_KEY=your_key_here
```

> **No API key?** The system automatically runs in **offline mode** with structured placeholder narratives. The full pipeline including PDF generation and the dashboard remains completely functional for demonstration purposes.

---

## Data Validation

The ingestion layer enforces **6 data quality checks** before any data enters the pipeline:

| # | Check |
|---|---|
| 1 | All required columns must be present |
| 2 | No null values allowed in any critical column |
| 3 | Revenue must never be negative |
| 4 | Active users must always be a positive integer |
| 5 | Churn rate must be between 0 and 1 |
| 6 | Conversion rate must be between 0 and 1 |

If any check fails, **the pipeline stops immediately** with a descriptive error message and logs the failure. This mirrors how production data pipelines handle data quality gates.

---

## Business Context

All metrics are calibrated to **realistic Indian B2B SaaS market benchmarks**:

| Metric | Baseline | Context |
|---|---|---|
| Weekly Revenue | ₹50,00,000 (50 lakhs) | Representative of a mid-market Indian SaaS company |
| Customer Acquisition Cost | ₹8,500 | Reflects Indian digital marketing and inside sales costs |
| Monthly Churn Rate | 4.5% | Within the typical 3–7% range for Indian SaaS |
| Conversion Rate | 3.2% | Realistic B2B free-trial-to-paid benchmark |

The project is deliberately set in the **Indian market** because generic USD-denominated templates do not reflect the operational reality that Indian data science professionals encounter in their careers.

---

## Author

**Prasanth Kumar Sahu**  
Masters in Finance and Information Technology  
Bhubaneswar, Odisha, India  
[GitHub: PrasanthKumarS777](https://github.com/PrasanthKumarS777)

---

*This project was independently conceived, designed, and built to demonstrate end-to-end data science engineering capability — from data pipeline architecture and statistical modelling to LLM integration, automated reporting, and business intelligence dashboard development.*
