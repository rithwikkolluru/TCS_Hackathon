import pytest
import pandas as pd
import numpy as np

from src.models.footfall_model import FootfallModel, predict_footfall
from src.models.wait_time_model import WaitTimeModel, predict_wait_time
from src.models.live_predictor import predict_live


def test_footfall_model_prediction():
    sample_df = pd.DataFrame([{
        "branch_id": "BR001",
        "service_category": "Withdrawal",
        "day_of_week": "Monday",
        "hour": 10,
        "day_num": 0,
        "day_of_month": 1,
        "is_weekend": 0,
        "is_month_end": 0,
        "is_salary_day": 1,
        "appointment_count": 2,
        "employees_available": 5,
        "employees_absent": 0,
        "historical_arrivals": 15.0,
        "previous_slot_arrivals": 12.0,
        "previous_day_arrivals": 14.0,
        "rolling_15min_arrivals": 8.0,
        "rolling_30min_arrivals": 16.0,
        "rolling_60min_arrivals": 30.0,
        "rolling_wait_time": 5.0,
        "queue_per_employee": 1.5
    }])

    preds = predict_footfall(sample_df)
    assert len(preds) == 1
    assert preds[0] >= 0.0


def test_wait_time_model_prediction():
    sample_df = pd.DataFrame([{
        "branch_id": "BR002",
        "service_category": "Loans - Payment and Sanctioning",
        "day_of_week": "Friday",
        "queue_length_at_arrival": 8,
        "employees_available": 2,
        "employees_absent": 1,
        "arrival_rate": 15.0,
        "service_time_minutes": 25.0,
        "appointment_count": 1,
        "hour": 11,
        "day_num": 4,
        "day_of_month": 28,
        "is_weekend": 0,
        "is_month_end": 1,
        "is_salary_day": 0,
        "rolling_15min_arrivals": 5.0,
        "rolling_30min_arrivals": 10.0,
        "rolling_60min_arrivals": 20.0,
        "historical_wait": 22.0,
        "queue_per_employee": 4.0
    }])

    preds = predict_wait_time(sample_df)
    assert len(preds) == 1
    assert preds[0] >= 0.0


def test_live_predictor_interface():
    res = predict_live(
        branch_id="BR001",
        service_category="Money Transfer",
        current_queue=10,
        staff_available=3
    )

    assert res["branch_id"] == "BR001"
    assert "predicted_wait_minutes" in res
    assert "bottleneck_risk" in res
    assert "explanation" in res
    assert res["bottleneck_risk"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
