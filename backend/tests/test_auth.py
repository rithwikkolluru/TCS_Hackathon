import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_auth_login_success():
    resp = client.post("/api/auth/login", json={
        "email": "manager_hyd@bank.com",
        "password": "BankDemo#2026"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "manager_hyd@bank.com"
    assert data["data"]["user"]["role"] == "manager"
    assert data["data"]["user"]["branch_id"] == "BR001"


def test_auth_login_invalid_password():
    resp = client.post("/api/auth/login", json={
        "email": "manager_hyd@bank.com",
        "password": "WrongPassword123"
    })
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


def test_auth_register_and_me():
    import uuid
    rand_email = f"staff_{uuid.uuid4().hex[:6]}@bank.com"
    reg_resp = client.post("/api/auth/register", json={
        "name": "New Counter Officer",
        "email": rand_email,
        "password": "SecurePassword#2026",
        "role": "employee",
        "branch_id": "BR001"
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["email"] == rand_email

    # Login with new account
    login_resp = client.post("/api/auth/login", json={
        "email": rand_email,
        "password": "SecurePassword#2026"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]

    # Verify /api/auth/me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["data"]["email"] == rand_email
    assert me_data["data"]["role"] == "employee"


def test_auth_refresh():
    login_resp = client.post("/api/auth/login", json={
        "email": "regional@bank.com",
        "password": "BankDemo#2026"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]

    ref_resp = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    assert ref_data["success"] is True
    assert "access_token" in ref_data["data"]
