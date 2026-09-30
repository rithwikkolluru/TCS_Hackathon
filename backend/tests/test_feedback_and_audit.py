import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_manager_token() -> str:
    resp = client.post("/api/auth/login", json={"email": "manager_hyd@bank.com", "password": "BankDemo#2026"})
    return resp.json()["data"]["access_token"]


def test_recommendation_outcome_feedback_loop():
    token = get_manager_token()

    # Create recommendation first
    gen_resp = client.post(
        "/api/recommendations/generate",
        json={"branch_id": "BR001"},
        headers={"Authorization": f"Bearer {token}"}
    )
    rec_id = gen_resp.json()["data"][0]["id"]

    # Record outcome
    outcome_resp = client.post(
        "/api/feedback/recommendation-outcome",
        json={
            "recommendation_id": rec_id,
            "action": "ACCEPTED",
            "actual_wait_after_action": 12.0,
            "actual_queue_after_action": 4,
            "reason": "Wait time significantly decreased"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert outcome_resp.status_code == 200
    data = outcome_resp.json()
    assert data["success"] is True
    assert data["data"]["action"] == "ACCEPTED"
    assert data["data"]["impact"] == "POSITIVE"
    assert data["data"]["wait_reduction_minutes"] > 0


def test_feedback_summary_nlp():
    token = get_manager_token()
    resp = client.get("/api/feedback/summary?branch_id=BR001", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "average_rating" in data
    assert "positive_percentage" in data
    assert len(data["top_topics"]) > 0


def test_analyze_comment_nlp():
    token = get_manager_token()
    resp = client.post(
        "/api/feedback/analyze-comment?comment=Staff%20was%20very%20polite%20and%20the%20queue%20moved%20fast&rating=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["sentiment"] == "Positive"
    assert data["sentiment_score"] > 0


def test_audit_logs():
    token = get_manager_token()
    resp = client.get("/api/audit/logs?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    logs = resp.json()["data"]
    assert len(logs) > 0
    assert any(log["action"] in ["login_success", "recommendations_generated", "recommendation_accepted", "database_seeded"] for log in logs)
