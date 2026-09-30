import sys
import json
import time
from pathlib import Path
from fastapi.testclient import TestClient

# Add repo root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app

client = TestClient(app)


def run_full_demo_scenario():
    print("=" * 75)
    print("  INTELLIGENT BRANCH SERVICE LOAD & CUSTOMER EXPERIENCE OPTIMIZER")
    print("            MEMBER 2 BACKEND END-TO-END DEMONSTRATION")
    print("=" * 75)

    # STEP 1: Login as Manager
    print("\n[STEP 1] Login as Branch Manager (manager_hyd@bank.com)...")
    login_resp = client.post("/api/auth/login", json={
        "email": "manager_hyd@bank.com",
        "password": "BankDemo#2026"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    user_info = login_resp.json()["data"]["user"]
    print(f"  ✓ Authenticated: {user_info['name']} (Role: {user_info['role']})")
    print(f"  ✓ JWT Token issued: {token[:25]}... (Signed with HS256)")

    # STEP 2: Manager selects Hyderabad Central (BR001)
    print("\n[STEP 2] Manager selects assigned branch (BR001 - Hyderabad Central)...")
    branch_resp = client.get("/api/branches/BR001", headers={"Authorization": f"Bearer {token}"})
    assert branch_resp.status_code == 200
    branch_data = branch_resp.json()["data"]
    print(f"  ✓ Branch loaded: {branch_data['branch_name']} in {branch_data['city']}")
    print(f"  ✓ Total active counters: {branch_data['total_counters']}")

    # STEP 3 & 4: Request tomorrow's prediction (11 AM - 1 PM)
    print("\n[STEP 3 & 4] Request tomorrow's footfall prediction (11:00 AM - 1:00 PM)...")
    footfall_resp = client.post(
        "/api/predictions/footfall",
        json={
            "branch_id": "BR001",
            "date": "2026-10-01",
            "start_time": "11:00",
            "end_time": "13:00"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert footfall_resp.status_code == 200
    ff_data = footfall_resp.json()["data"]
    print(f"  ✓ Predicted Customers: {ff_data['predicted_customers']} customers")
    print(f"  ✓ Time Window: {ff_data['time_slot']} on {ff_data['date']}")
    print(f"  ✓ Explainability: {footfall_resp.json()['explanation']}")

    # STEP 5: System analyzes service categories
    print("\n[STEP 5] System analyzes load breakdown across all 14 service categories...")
    load_resp = client.get("/api/dashboard/service-load?branch_id=BR001", headers={"Authorization": f"Bearer {token}"})
    assert load_resp.status_code == 200
    categories = load_resp.json()["data"]
    print(f"  ✓ Analyzed {len(categories)} distinct banking service categories.")
    sample_cats = [c for c in categories if c["service_category"] in ["Loans - Payment and Sanctioning", "Withdrawal", "Money Transfer"]]
    for sc in sample_cats:
        print(f"    - {sc['service_category']}: Queue: {sc['queue_length']}, Avg Wait: {sc['average_wait']:.1f}m, Risk: {sc['risk_level']}")

    # STEP 6: System calculates current staff and required staff
    print("\n[STEP 6] System calculates staff capacity and requirement...")
    staff_resp = client.post(
        "/api/predictions/staff-requirement",
        json={
            "branch_id": "BR001",
            "date": "2026-10-01",
            "start_time": "11:00",
            "end_time": "13:00"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert staff_resp.status_code == 200
    staff_data = staff_resp.json()["data"]
    print(f"  ✓ Staff Available: {staff_data['staff_available']} employees")
    print(f"  ✓ Staff Required:  {staff_data['staff_required']} employees")
    print(f"  ✓ Additional Staff Required (Gap): {staff_data['additional_staff_required']} employees")
    print(f"  ✓ Recommendation Explanation: {staff_data['explanation']}")

    # STEP 7: System identifies bottlenecks
    print("\n[STEP 7] System identifies active service bottlenecks...")
    bottleneck_resp = client.get("/api/dashboard/bottlenecks?branch_id=BR001", headers={"Authorization": f"Bearer {token}"})
    assert bottleneck_resp.status_code == 200
    bottlenecks = bottleneck_resp.json()["data"]
    high_risks = [b for b in bottlenecks if b["risk_level"] in ["HIGH", "CRITICAL"]]
    print(f"  ✓ Flagged {len(high_risks)} high-risk bottlenecks:")
    for b in high_risks[:2]:
        print(f"    - [{b['risk_level']}] {b['service_category']}: Queue: {b['queue_length']}, Pred Wait: {b['predicted_wait_minutes']:.1f}m")
        print(f"      Reason: {b['explanation']}")

    # STEP 8: System generates recommendations
    print("\n[STEP 8] System generates operational AI recommendations...")
    gen_resp = client.post(
        "/api/recommendations/generate",
        json={"branch_id": "BR001"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert gen_resp.status_code == 200
    recommendations = gen_resp.json()["data"]
    print(f"  ✓ Generated {len(recommendations)} actionable recommendations.")
    chosen_rec = recommendations[0]
    print(f"    Selected Rec ID #{chosen_rec['id']} [{chosen_rec['recommendation_type']}]:")
    print(f"    Action: {chosen_rec['recommendation_text']}")
    print(f"    Explanation: {chosen_rec['explanation']}")

    # STEP 9: Manager accepts recommendation
    print(f"\n[STEP 9] Manager reviews and ACCEPTS Recommendation #{chosen_rec['id']}...")
    accept_resp = client.post(
        f"/api/recommendations/{chosen_rec['id']}/accept",
        json={"reason": "Deployed 2 floating tellers to loan verification counter.", "actual_wait_after_action": 14.5, "actual_queue_after_action": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert accept_resp.status_code == 200
    accepted_data = accept_resp.json()["data"]
    print(f"  ✓ Recommendation #{accepted_data['id']} status updated to: {accepted_data['status']}")

    # STEP 10: Audit log records the action
    print("\n[STEP 10] Audit log records the acceptance action...")
    audit_resp = client.get("/api/audit/logs?limit=5", headers={"Authorization": f"Bearer {token}"})
    assert audit_resp.status_code == 200
    latest_log = audit_resp.json()["data"][0]
    print(f"  ✓ Tamper-evident Audit Entry: Action='{latest_log['action']}', UserID={latest_log['user_id']}, Role='{latest_log['role']}', Resource='{latest_log['resource']}:{latest_log['resource_id']}'")

    # STEP 11 & 12 & 13 & 14 & 15: Live Surge Simulation & WebSocket Alert
    print("\n[STEP 11-15] Trigger live surge simulation (30-50 queue spike) & WebSocket alert...")
    with client.websocket_connect(f"/ws/alerts?token={token}") as ws:
        # Initial greeting
        ws_msg = ws.receive_json()
        print(f"  ✓ WebSocket Connected: {ws_msg['message']}")

        # Trigger surge API
        surge_resp = client.post(
            "/api/live/simulate-surge?branch_id=BR001&service_category=Withdrawal",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert surge_resp.status_code == 200
        surge_result = surge_resp.json()["data"]
        print(f"  ✓ Surge Event Received by Backend: Queue={surge_result['queue_length']}, Staff={surge_result['staff_available']}")
        print(f"  ✓ Live ML Predictor Risk Level: {surge_result['prediction']['bottleneck_risk']}")

        # Receive WebSocket real-time broadcast
        ws_alert = ws.receive_json()
        print(f"  ✓ Real-time WebSocket Alert Received:")
        print(f"    Event: {ws_alert['event']}")
        print(f"    Alert Message: \"{ws_alert['message']}\"")
        print(f"    Risk Level: {ws_alert['risk_level']}")
        print(f"    Digital Redirection Nudge: {ws_alert['data']['digital_redirection']['instructions']}")

    # STEP 16 & 17 & 18: Feedback loop outcome tracking and wait time impact
    print("\n[STEP 16-18] Record recommendation outcome in continuous learning feedback loop...")
    outcome_resp = client.post(
        "/api/feedback/recommendation-outcome",
        json={
            "recommendation_id": chosen_rec["id"],
            "action": "ACCEPTED",
            "actual_wait_after_action": 13.5,
            "actual_queue_after_action": 4,
            "reason": "Wait time reduced from 35m to 13.5m after extra counter opened."
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert outcome_resp.status_code == 200
    outcome_data = outcome_resp.json()["data"]
    print(f"  ✓ Outcome Recorded:")
    print(f"    Impact Assessment: {outcome_data['impact']}")
    print(f"    Wait Time Reduction: {outcome_data['wait_reduction_minutes']} minutes")
    print(f"    Queue Reduction: {outcome_data['queue_reduction']} customers")
    print(f"    Feedback Message: {outcome_data['message']}")

    print("\n" + "=" * 75)
    print("      ALL 18 STEPS OF THE END-TO-END DEMO SCENARIO PASSED 100%!")
    print("=" * 75)


if __name__ == "__main__":
    run_full_demo_scenario()
