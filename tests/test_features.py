import pytest
import pandas as pd

from src.features.feature_engineering import FeatureEngineer
from src.utils.config import PROCESSED_DATA_DIR


def test_feature_engineering():
    fe = FeatureEngineer()
    processed_visits_path = PROCESSED_DATA_DIR / "processed_visits.parquet"

    assert processed_visits_path.exists(), "Processed visits dataset must exist prior to feature testing."

    df_visits = pd.read_parquet(processed_visits_path).head(1000)

    footfall_df = fe.build_footfall_features(df_visits)
    assert not footfall_df.empty
    assert "predicted_customer_count" in footfall_df.columns
    assert "rolling_30min_arrivals" in footfall_df.columns

    wait_df = fe.build_wait_time_features(df_visits)
    assert not wait_df.empty
    assert "queue_per_employee" in wait_df.columns
    assert "arrival_rate" in wait_df.columns
