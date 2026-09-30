import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.footfall_model import train_footfall_model
from src.models.wait_time_model import train_wait_model
from src.utils.config import PROCESSED_DATA_DIR, REPORTS_DIR, BRANCHES, SERVICE_CATEGORIES

def generate_service_category_analysis():
    """Generates branch and service-level aggregate statistics report."""
    processed_visits_path = PROCESSED_DATA_DIR / "processed_visits.parquet"
    if not processed_visits_path.exists():
        print(f"Warning: {processed_visits_path} does not exist. Skipping service category analysis.")
        return

    df = pd.read_parquet(processed_visits_path)

    stats = []
    grp_cols = ["branch_id", "service_category"]

    for (b_id, s_cat), group in df.groupby(grp_cols):
        total_visits = len(group)
        avg_wait = round(group["waiting_time_minutes"].mean(), 2)
        med_wait = round(group["waiting_time_minutes"].median(), 2)
        max_wait = round(group["waiting_time_minutes"].max(), 2)
        avg_serv = round(group["service_time_minutes"].mean(), 2)
        arrival_cnt = total_visits
        comp_cnt = (group["completed_status"] == "Completed").sum()
        emp_cnt = int(group["employees_available"].mean())

        # Estimated utilization formula: (total service minutes) / (available employees * 8 hrs * 60 mins)
        total_service_min = group["service_time_minutes"].sum()
        max_capacity_min = max(1, emp_cnt * 90 * 8 * 60 / len(BRANCHES))  # Approx capacity over horizon
        utilization = min(0.98, round(total_service_min / max_capacity_min, 2))

        # Bottleneck frequency: % of visits where wait time > 20 mins or queue > 10
        bottlenecks = ((group["waiting_time_minutes"] > 20) | (group["queue_length_at_arrival"] > 10)).sum()
        btnk_freq = round(bottlenecks / max(1, total_visits), 3)

        stats.append({
            "branch_id": b_id,
            "service_category": s_cat,
            "total_visits": total_visits,
            "average_wait": avg_wait,
            "median_wait": med_wait,
            "maximum_wait": max_wait,
            "average_service_time": avg_serv,
            "arrival_count": arrival_cnt,
            "completion_count": comp_cnt,
            "employee_count": emp_cnt,
            "utilization": utilization,
            "bottleneck_frequency": btnk_freq
        })

    analysis_df = pd.DataFrame(stats)
    analysis_df.to_csv(REPORTS_DIR / "service_category_analysis.csv", index=False)
    print(f"Service Category Analysis generated and saved to {REPORTS_DIR / 'service_category_analysis.csv'}")

def main():
    print("==========================================")
    print("  TRAINING ML MODELS & GENERATING REPORTS")
    print("==========================================")
    
    print("\n--- Training Footfall Prediction Model ---")
    ff_metrics = train_footfall_model()

    print("\n--- Training Waiting Time Prediction Model ---")
    wt_metrics = train_wait_model()

    print("\n--- Generating Service Category Analysis Report ---")
    generate_service_category_analysis()

    print("\nModel training and reporting complete!")

if __name__ == "__main__":
    main()
