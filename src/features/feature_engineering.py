import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

from src.utils.config import (
    PROCESSED_DATA_DIR,
    FEATURES_DATA_DIR,
    SERVICE_CATEGORIES
)


class FeatureEngineer:
    """Computes features for Footfall Prediction and Waiting Time Prediction."""

    def __init__(self):
        pass

    def build_footfall_features(self, df_visits: pd.DataFrame) -> pd.DataFrame:
        """Aggregates visit data by branch_id, date, hour, service_category to build footfall training dataset."""
        df = df_visits.copy()
        df["date_dt"] = pd.to_datetime(df["date"])

        # Group by branch, date, hour, service_category
        grp_cols = ["branch_id", "date", "hour", "service_category"]
        
        aggregated = df.groupby(grp_cols).agg(
            predicted_customer_count=("visit_id", "count"),
            current_queue_length=("queue_length_at_arrival", "mean"),
            employees_available=("employees_available", "mean"),
            employees_absent=("employees_absent", "mean"),
            average_service_time=("service_time_minutes", "mean"),
            historical_wait=("waiting_time_minutes", "mean"),
            appointment_count=("appointment_status", lambda s: (s == "Booked").sum())
        ).reset_index()

        # Add calendar and temporal features
        aggregated["date_dt"] = pd.to_datetime(aggregated["date"])
        aggregated["day_of_week"] = aggregated["date_dt"].dt.day_name()
        aggregated["day_num"] = aggregated["date_dt"].dt.dayofweek
        aggregated["day_of_month"] = aggregated["date_dt"].dt.day
        aggregated["is_weekend"] = aggregated["day_num"].isin([5, 6]).astype(int)
        aggregated["is_month_end"] = aggregated["day_of_month"].isin([28, 29, 30, 31]).astype(int)
        aggregated["is_salary_day"] = aggregated["day_of_month"].isin([1, 2, 3, 4, 5]).astype(int)

        # Sort chronologically for lag/rolling features
        aggregated = aggregated.sort_values(by=["branch_id", "service_category", "date", "hour"]).reset_index(drop=True)

        # Lag features within each branch & service_category
        b_s_grp = aggregated.groupby(["branch_id", "service_category"])

        aggregated["previous_slot_arrivals"] = b_s_grp["predicted_customer_count"].shift(1).fillna(0)
        aggregated["previous_day_arrivals"] = b_s_grp["predicted_customer_count"].shift(8).fillna(0)  # ~8 working hours prior
        aggregated["rolling_30min_arrivals"] = b_s_grp["predicted_customer_count"].transform(lambda x: x.rolling(2, min_periods=1).sum()).fillna(0)
        aggregated["rolling_60min_arrivals"] = b_s_grp["predicted_customer_count"].transform(lambda x: x.rolling(4, min_periods=1).sum()).fillna(0)
        aggregated["rolling_15min_arrivals"] = (aggregated["rolling_30min_arrivals"] / 2.0).round()
        
        aggregated["rolling_wait_time"] = b_s_grp["historical_wait"].transform(lambda x: x.rolling(3, min_periods=1).mean()).fillna(0)
        aggregated["historical_arrivals"] = b_s_grp["predicted_customer_count"].transform(lambda x: x.expanding(min_periods=1).mean()).fillna(0)

        # Derived ratio
        aggregated["queue_per_employee"] = (aggregated["current_queue_length"] / aggregated["employees_available"].clip(lower=1)).round(2)

        return aggregated

    def build_wait_time_features(self, df_visits: pd.DataFrame) -> pd.DataFrame:
        """Prepares visit-level features for waiting time model."""
        df = df_visits.copy()
        df["arrival_dt"] = pd.to_datetime(df["arrival_timestamp"])
        df = df.sort_values(by=["branch_id", "arrival_dt"]).reset_index(drop=True)

        # Date features
        df["day_num"] = df["arrival_dt"].dt.dayofweek
        df["day_of_month"] = df["arrival_dt"].dt.day
        df["is_weekend"] = df["day_num"].isin([5, 6]).astype(int)
        df["is_month_end"] = df["day_of_month"].isin([28, 29, 30, 31]).astype(int)
        df["is_salary_day"] = df["day_of_month"].isin([1, 2, 3, 4, 5]).astype(int)

        # Rolling arrival rate per branch (last 15m, 30m, 60m)
        df = df.set_index("arrival_dt")
        
        # Calculate rolling arrivals per branch
        rolling_15 = df.groupby("branch_id")["visit_id"].rolling("15min").count().reset_index()
        rolling_30 = df.groupby("branch_id")["visit_id"].rolling("30min").count().reset_index()
        rolling_60 = df.groupby("branch_id")["visit_id"].rolling("60min").count().reset_index()

        df = df.reset_index()

        df["rolling_15min_arrivals"] = rolling_15["visit_id"].values
        df["rolling_30min_arrivals"] = rolling_30["visit_id"].values
        df["rolling_60min_arrivals"] = rolling_60["visit_id"].values

        # Queue per employee
        df["queue_per_employee"] = (df["queue_length_at_arrival"] / df["employees_available"].clip(lower=1)).round(2)
        df["arrival_rate"] = (df["rolling_30min_arrivals"] / 30.0).round(3)

        # Historical wait window (rolling 50 visits average wait)
        df["historical_wait"] = df.groupby(["branch_id", "service_category"])["waiting_time_minutes"].transform(
            lambda x: x.shift(1).rolling(50, min_periods=1).mean()
        ).fillna(df["waiting_time_minutes"].mean())

        # Appointment count feature
        df["appointment_count"] = (df["appointment_status"] == "Booked").astype(int)

        return df

    def run_feature_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Loads processed visits and builds footfall & wait time feature datasets."""
        processed_visits_path = PROCESSED_DATA_DIR / "processed_visits.parquet"
        if not processed_visits_path.exists():
            raise FileNotFoundError("Processed visits file not found. Run ETL pipeline first.")

        df_visits = pd.read_parquet(processed_visits_path)

        print("Building footfall features...")
        footfall_df = self.build_footfall_features(df_visits)
        footfall_df.to_parquet(FEATURES_DATA_DIR / "features_footfall.parquet", index=False)
        footfall_df.to_csv(FEATURES_DATA_DIR / "features_footfall.csv", index=False)

        print("Building wait time features...")
        wait_df = self.build_wait_time_features(df_visits)
        wait_df.to_parquet(FEATURES_DATA_DIR / "features_wait_time.parquet", index=False)
        wait_df.to_csv(FEATURES_DATA_DIR / "features_wait_time.csv", index=False)

        print(f"Features generated successfully! Saved to {FEATURES_DATA_DIR}")
        return footfall_df, wait_df


if __name__ == "__main__":
    fe = FeatureEngineer()
    fe.run_feature_pipeline()
