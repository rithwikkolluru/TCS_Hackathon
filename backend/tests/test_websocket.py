import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_websocket_unauthorized_rejected():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/alerts?token=invalid_token") as websocket:
            websocket.receive_text()


def test_websocket_authorized_connection_and_ping():
    # Login to get valid JWT token
    login_resp = client.post("/api/auth/login", json={"email": "manager_hyd@bank.com", "password": "BankDemo#2026"})
    token = login_resp.json()["data"]["access_token"]

    with client.websocket_connect(f"/ws/alerts?token={token}") as websocket:
        # First message is connection confirmation
        data = websocket.receive_json()
        assert data["event"] == "CONNECTED"
        assert data["branch_id"] == "BR001"

        # Send ping
        websocket.send_text("ping")
        resp = websocket.receive_text()
        assert resp == "pong"
