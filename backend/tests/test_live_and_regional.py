import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_token(email: str) -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": "BankDemo#2026"})
    return resp.json()["data"]["access_token"]


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] == "connected"
    assert data["ml_models"] == "loaded"


def test_live_event_ingestion():
    token = get_token("manager_hyd@bank.com")
    resp = client.post(
        "/api/live/events",
        json={
            "branch_id": "BR001",
            "event_type": "CUSTOMER_ARRIVAL",
            "service_category": "Withdrawal",
            "queue_length": 12,
            "staff_available": 3
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["branch_id"] == "BR001"
    assert "prediction" in data


def test_live_surge_simulation():
    token = get_token("manager_hyd@bank.com")
    resp = client.post(
        "/api/live/simulate-surge?branch_id=BR001&service_category=Withdrawal",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    # Surge queue must be high (>= 30) and risk level elevated
    assert data["queue_length"] >= 30
    assert data["prediction"]["bottleneck_risk"] in ["HIGH", "CRITICAL"]


def test_regional_ops_endpoints():
    token = get_token("regional@bank.com")

    # 1. Regional branches
    r_branches = client.get("/api/regional/branches", headers={"Authorization": f"Bearer {token}"})
    assert r_branches.status_code == 200
    assert len(r_branches.json()["data"]) == 8

    # 2. Regional load
    r_load = client.get("/api/regional/load", headers={"Authorization": f"Bearer {token}"})
    assert r_load.status_code == 200
    assert len(r_load.json()["data"]) == 8

    # 3. Regional bottlenecks
    r_bottlenecks = client.get("/api/regional/bottlenecks", headers={"Authorization": f"Bearer {token}"})
    assert r_bottlenecks.status_code == 200

    # 4. Regional staffing
    r_staffing = client.get("/api/regional/staffing", headers={"Authorization": f"Bearer {token}"})
    assert r_staffing.status_code == 200
    assert len(r_staffing.json()["data"]) == 8
