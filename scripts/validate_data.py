import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.validator import DataValidator
from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def main():
    print("==========================================")
    print("  DATA VALIDATION & PII SANITY CHECK")
    print("==========================================")
    validator = DataValidator()

    raw_visits_path = RAW_DATA_DIR / "visits.csv"
    raw_feedback_path = RAW_DATA_DIR / "customer_feedback.csv"

    if not raw_visits_path.exists():
        print(f"Error: Raw visits data not found at {raw_visits_path}. Please run generate_data.py first.")
        sys.exit(1)

    visits_df = pd.read_csv(raw_visits_path)
    feedback_df = pd.read_csv(raw_feedback_path) if raw_feedback_path.exists() else pd.DataFrame()

    results = validator.validate_all({
        "visits": visits_df,
        "customer_feedback": feedback_df
    })

    for ds_name, (is_valid, errors) in results.items():
        if is_valid:
            print(f"  [PASS] {ds_name}: PASS (No PII detected, schema & range rules intact)")
        else:
            print(f"  [FAIL] {ds_name}: FAIL ({len(errors)} errors found)")
            for err in errors:
                print(f"    - {err}")

if __name__ == "__main__":
    main()
