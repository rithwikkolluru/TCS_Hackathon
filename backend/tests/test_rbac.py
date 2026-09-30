import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_token_for(email: str, password: str = "BankDemo#2026") -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.json()["data"]["access_token"]


def test_manager_can_access_own_branch():
    token = get_token_for("manager_hyd@bank.com")
    resp = client.get("/api/branches/BR001", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["branch_code"] == "BR001"


def test_manager_cannot_access_other_branch_isolation():
    token = get_token_for("manager_hyd@bank.com")
    # Attempt to access Kukatpally branch (BR002)
    resp = client.get("/api/branches/BR002", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "Branch isolation policy violation" in resp.json()["detail"]


def test_regional_ops_can_access_all_branches():
    token = get_token_for("regional@bank.com")
    # Access BR001
    resp1 = client.get("/api/branches/BR001", headers={"Authorization": f"Bearer {token}"})
    assert resp1.status_code == 200

    # Access BR002
    resp2 = client.get("/api/branches/BR002", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200


def test_employee_cannot_generate_or_accept_recommendations():
    token = get_token_for("teller1_hyd@bank.com")

    # Employee attempts to generate recommendations
    resp = client.post(
        "/api/recommendations/generate",
        json={"branch_id": "BR001"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403
    assert "Access denied" in resp.json()["detail"]
