import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

from src.utils.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SERVICE_CATEGORIES
)
from src.data.validator import DataValidator


class ETLPipeline:
    """ETL Pipeline for Cleaning, Timestamp Normalization, Category Standardisation, and PII verification."""

    def __init__(self):
        self.validator = DataValidator()
        self.valid_categories_map = {c.lower().strip(): c for c in SERVICE_CATEGORIES}

    def clean_visits(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans raw visit records."""
        df = df.copy()

        # 1. Drop complete duplicates
        df = df.drop_duplicates(subset=["visit_id"])

        # 2. Timestamp Normalization
        ts_cols = ["arrival_timestamp", "service_start_timestamp", "service_end_timestamp"]
        for col in ts_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Drop records with bad arrival timestamps
        df = df.dropna(subset=["arrival_timestamp"])

        # Normalize date and hour from arrival_timestamp
        df["date"] = df["arrival_timestamp"].dt.strftime("%Y-%m-%d")
        df["day_of_week"] = df["arrival_timestamp"].dt.day_name()
        df["hour"] = df["arrival_timestamp"].dt.hour

        # 3. Service Category Normalization & Fallback handling
        def normalize_category(cat):
            if pd.isna(cat):
                return "Other"
            cat_str = str(cat).lower().strip()
            return self.valid_categories_map.get(cat_str, "Other")

        df["service_category"] = df["service_category"].apply(normalize_category)

        # 4. Fill missing numeric values with logical defaults
        df["employees_available"] = df["employees_available"].fillna(1).astype(int)
        df["employees_absent"] = df["employees_absent"].fillna(0).astype(int)
        df["queue_length_at_arrival"] = df["queue_length_at_arrival"].fillna(0).astype(int)
        df["waiting_time_minutes"] = df["waiting_time_minutes"].clip(lower=0.0)
        df["service_time_minutes"] = df["service_time_minutes"].clip(lower=0.5)

        # Ensure completed status fallback
        df["completed_status"] = df["completed_status"].fillna("Completed")

        return df

    def clean_feedback(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans customer feedback dataset."""
        df = df.copy()
        df = df.drop_duplicates(subset=["feedback_id"])
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

        # Clean rating values
        df["rating"] = pd.to_numeric(df["rating"], errors='coerce').fillna(3).astype(int)
        df["rating"] = df["rating"].clip(1, 5)

        # Strip whitespace in comments
        df["comment"] = df["comment"].astype(str).str.strip()

        return df

    def run_pipeline(self) -> Dict[str, pd.DataFrame]:
        """Runs the full ETL pipeline from raw to processed."""
        raw_visits_path = RAW_DATA_DIR / "visits.csv"
        raw_feedback_path = RAW_DATA_DIR / "customer_feedback.csv"

        if not raw_visits_path.exists():
            raise FileNotFoundError(f"Raw data file not found at {raw_visits_path}. Run generate_data.py first.")

        raw_visits = pd.read_csv(raw_visits_path)
        raw_feedback = pd.read_csv(raw_feedback_path) if raw_feedback_path.exists() else pd.DataFrame()

        print("Running ETL Step 1: Cleaning & Normalizing Visits...")
        processed_visits = self.clean_visits(raw_visits)

        print("Running ETL Step 2: Cleaning & Normalizing Feedback...")
        processed_feedback = self.clean_feedback(raw_feedback)

        print("Running ETL Step 3: PII Verification...")
        is_clean, pii_errs = self.validator.validate_pii(processed_visits, "processed_visits")
        if not is_clean:
            raise ValueError(f"PII Verification failed during ETL: {pii_errs}")

        # Save processed datasets
        processed_visits.to_parquet(PROCESSED_DATA_DIR / "processed_visits.parquet", index=False)
        processed_visits.to_csv(PROCESSED_DATA_DIR / "processed_visits.csv", index=False)
        processed_feedback.to_csv(PROCESSED_DATA_DIR / "processed_feedback.csv", index=False)

        print(f"ETL completed successfully! Clean datasets saved to {PROCESSED_DATA_DIR}")
        return {
            "processed_visits": processed_visits,
            "processed_feedback": processed_feedback
        }


if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run_pipeline()
