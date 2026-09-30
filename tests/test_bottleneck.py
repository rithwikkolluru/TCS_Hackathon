import pytest
from src.models.bottleneck_detector import BottleneckDetector


def test_bottleneck_detector_low_risk():
    detector = BottleneckDetector()
    res = detector.detect_bottleneck(
        branch_id="BR001",
        service_category="Withdrawal",
        queue_length=2,
        predicted_wait_minutes=4.0,
        staff_available=5,
        staff_required=4
    )

    assert res["risk_level"] == "LOW"
    assert "smoothly" in res["reason"] or "LOW risk" in res["reason"]


def test_bottleneck_detector_critical_risk():
    detector = BottleneckDetector()
    res = detector.detect_bottleneck(
        branch_id="BR002",
        service_category="Loans - Payment and Sanctioning",
        queue_length=25,
        predicted_wait_minutes=45.0,
        staff_available=2,
        staff_required=6,
        arrival_rate=30.0,
        employee_utilization=0.95
    )

    assert res["risk_level"] == "CRITICAL"
    assert "CRITICAL risk" in res["reason"]
    assert "severely exceeds" in res["reason"] or "critically high" in res["reason"]
