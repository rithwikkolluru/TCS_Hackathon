import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_manager_token() -> str:
    resp = client.post("/api/auth/login", json={"email": "manager_hyd@bank.com", "password": "BankDemo#2026"})
    return resp.json()["data"]["access_token"]


def test_dashboard_bottlenecks():
    token = get_manager_token()
    resp = client.get("/api/dashboard/bottlenecks?branch_id=BR001", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]) == 14  # All 14 service categories


def test_dashboard_summary():
    token = get_manager_token()
    resp = client.get("/api/dashboard/summary?branch_id=BR001", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["branch_id"] == "BR001"
    assert "current_queue" in data["data"]
    assert "average_wait" in data["data"]


def test_dashboard_service_load():
    token = get_manager_token()
    resp = client.get("/api/dashboard/service-load?branch_id=BR001", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]) == 14


def test_recommendation_workflow_generate_and_accept():
    token = get_manager_token()

    # 1. Generate recommendations
    gen_resp = client.post(
        "/api/recommendations/generate",
        json={"branch_id": "BR001"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert gen_resp.status_code == 200
    recs = gen_resp.json()["data"]
    assert len(recs) > 0
    rec_id = recs[0]["id"]

    # 2. Accept recommendation
    accept_resp = client.post(
        f"/api/recommendations/{rec_id}/accept",
        json={"reason": "Approved extra teller deployment", "actual_wait_after_action": 14.0, "actual_queue_after_action": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["data"]["status"] == "ACCEPTED"


def test_digital_redirection():
    token = get_manager_token()
    resp = client.get(
        "/api/recommendations/digital-redirection?service_category=Money%20Transfer",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["digital_available"] is True
    assert "Mobile Banking" in data["digital_channel"]
    assert data["confidence"] >= 0.8
