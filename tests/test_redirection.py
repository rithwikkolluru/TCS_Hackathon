import pytest
from src.recommendation.digital_redirection import get_digital_recommendation


def test_digital_redirection_available():
    res = get_digital_recommendation("Money Transfer")
    assert res["digital_available"] is True
    assert "Mobile Banking" in res["digital_channel"]
    assert res["confidence"] > 0.7


def test_digital_redirection_not_available():
    res = get_digital_recommendation("Locker Issuing")
    assert res["digital_available"] is False
    assert "Branch visit is recommended" in res["recommendation"]
