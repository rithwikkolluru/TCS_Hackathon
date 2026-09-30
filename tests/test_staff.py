import pytest
from src.recommendation.staff_requirement import calculate_required_staff


def test_calculate_required_staff_scenario():
    # Prompt example: 200 customers expected between 11 AM and 1 PM
    res = calculate_required_staff(
        expected_customers=200,
        service_category="Loans - Payment and Sanctioning",
        operating_duration_hours=2.0,
        employees_available=3,
        branch_id="BR002",
        time_window="11:00 AM - 1:00 PM"
    )

    assert res["expected_customers"] == 200
    assert res["employees_required"] > 3
    assert res["staff_gap"] > 0
    assert "required" in res["explanation"]


def test_calculate_required_staff_low_demand():
    res = calculate_required_staff(
        expected_customers=10,
        service_category="Withdrawal",
        operating_duration_hours=2.0,
        employees_available=3
    )

    assert res["employees_required"] <= 3
    assert res["staff_gap"] == 0
