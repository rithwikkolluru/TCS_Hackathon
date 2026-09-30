import pytest
import pandas as pd
from pathlib import Path

from src.data.generator import SyntheticDataGenerator
from src.data.validator import DataValidator
from src.data.etl import ETLPipeline
from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, SERVICE_CATEGORIES


def test_synthetic_data_generation(tmp_path):
    generator = SyntheticDataGenerator(seed=123, num_days=5)
    datasets = generator.generate_all()

    assert "visits" in datasets
    assert "staff_roster" in datasets
    assert "appointments" in datasets
    assert "customer_feedback" in datasets

    visits = datasets["visits"]
    assert not visits.empty
    assert len(visits) > 500

    # Test 14 service categories
    unique_cats = set(visits["service_category"].unique())
    assert unique_cats.issubset(set(SERVICE_CATEGORIES))


def test_pii_validation():
    validator = DataValidator()

    # Clean dataset
    clean_df = pd.DataFrame({
        "visit_id": ["VIS-1001", "VIS-1002"],
        "comment": ["Great service at Hyderabad Central", "Long queue for money transfer"]
    })
    is_clean, errs = validator.validate_pii(clean_df)
    assert is_clean
    assert len(errs) == 0

    # Dataset with PII (Aadhaar number)
    pii_df = pd.DataFrame({
        "visit_id": ["VIS-1003"],
        "comment": ["Customer Aadhaar is 1234 5678 9012"]
    })
    is_clean, errs = validator.validate_pii(pii_df)
    assert not is_clean
    assert len(errs) > 0


def test_etl_pipeline():
    pipeline = ETLPipeline()
    res = pipeline.run_pipeline()

    assert "processed_visits" in res
    assert "processed_feedback" in res

    processed_visits = res["processed_visits"]
    assert not processed_visits["arrival_timestamp"].isna().any()
    assert (processed_visits["waiting_time_minutes"] >= 0).all()
