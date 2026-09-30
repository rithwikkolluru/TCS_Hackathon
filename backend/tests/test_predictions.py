import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_manager_token() -> str:
    resp = client.post("/api/auth/login", json={"email": "manager_hyd@bank.com", "password": "BankDemo#2026"})
    return resp.json()["data"]["access_token"]


def test_predict_footfall_api():
    token = get_manager_token()
    payload = {
        "branch_id": "BR001",
        "date": "2026-10-01",
        "start_time": "11:00",
        "end_time": "13:00"
    }
    resp = client.post("/api/predictions/footfall", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["branch_id"] == "BR001"
    assert data["data"]["time_slot"] == "11:00-13:00"
    assert data["data"]["predicted_customers"] >= 100
    assert len(data["explanation"]) > 10


def test_predict_wait_time_api():
    token = get_manager_token()
    payload = {
        "branch_id": "BR001",
        "service_category": "Withdrawal",
        "queue_length": 25,
        "staff_available": 3
    }
    resp = client.post("/api/predictions/wait-time", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["service_category"] == "Withdrawal"
    assert data["data"]["predicted_wait_minutes"] > 0
    assert data["data"]["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_predict_staff_requirement_api():
    token = get_manager_token()
    payload = {
        "branch_id": "BR001",
        "date": "2026-10-01",
        "start_time": "11:00",
        "end_time": "13:00"
    }
    resp = client.post("/api/predictions/staff-requirement", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["staff_required"] >= 1
    assert data["data"]["predicted_customers"] >= 100
    assert "additional_staff_required" in data["data"]
