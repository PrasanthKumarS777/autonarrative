import subprocess
import sys
import logging
import os
from datetime import datetime

# Setting up logging for the master pipeline runner
# This gives a single log entry point that shows the entire pipeline execution status
logging.basicConfig(
    filename="logs/autonarrative.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# These are the pipeline steps in the exact order they must run
# Each step depends on the output of the previous step
PIPELINE_STEPS = [
    ("Data Generation",     "src/data_generator.py"),
    ("Data Ingestion",      "src/ingest.py"),
    ("Anomaly Detection",   "src/detect_anomalies.py"),
    ("Narrative Engine",    "src/narrative_engine.py"),
    ("Report Generation",   "src/report_generator.py"),
]

def run_step(step_name, script_path):
    # This function runs a single pipeline step as a subprocess
    # Using subprocess means each script runs in isolation exactly as it would in production
    print("Running: " + step_name + "...")
    logging.info("Pipeline step started: " + step_name)

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False
    )

    # Check if the step succeeded - returncode 0 means success in Unix convention
    if result.returncode == 0:
        print(step_name + " completed successfully")
        logging.info("Pipeline step completed: " + step_name)
        return True
    else:
        print("ERROR: " + step_name + " failed - stopping pipeline")
        logging.error("Pipeline step failed: " + step_name)
        return False

def run_pipeline():
    print("AutoNarrative Pipeline Started at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # Create required folders if they do not exist yet
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Run each step in sequence and stop immediately if any step fails
    for step_name, script_path in PIPELINE_STEPS:
        success = run_step(step_name, script_path)
        if not success:
            print("Pipeline aborted at step: " + step_name)
            sys.exit(1)

    print("=" * 60)
    print("Pipeline completed successfully at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Reports saved to: reports/")
    print("Launch dashboard with: streamlit run src/dashboard.py")
    logging.info("Full pipeline completed successfully")

if __name__ == "__main__":
    run_pipeline()
