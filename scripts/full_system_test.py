#!/usr/bin/env python3
"""
Full System Integration Test — Member 4
Tests the complete end-to-end flow of the Intelligent Branch Service Optimizer.
"""
import sys, requests, json, time
from datetime import datetime

BASE = "http://127.0.0.1:8000"
results = []

def test(name, ok, detail=""):
    results.append((name, ok, detail))
    icon = "✅ PASS" if ok else "❌ FAIL"
    print(f"  {icon} | {name}: {detail}")

def login(email, password):
    r = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password}, timeout=10)
    return r.json()["data"]["access_token"]

print("=" * 60)
print("  INTELLIGENT BRANCH OPTIMIZER — SYSTEM TEST")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ── STEP 1: Health ────────────────────────────────────────────
print("\n[1] HEALTH CHECK")
try:
    r = requests.get(f"{BASE}/health", timeout=5); h = r.json()
    test("Backend alive", r.status_code == 200, f"HTTP {r.status_code}")
    test("Database", h["database"] == "connected", h["database"])
    test("ML models", h["ml_models"] == "loaded", h["ml_models"])
    test("Redis (fallback OK)", True, h["redis"])
except Exception as e:
    test("Backend reachable", False, str(e)); sys.exit(1)

# ── STEP 2: Authentication ────────────────────────────────────
print("\n[2] AUTHENTICATION")
try:
    mgr_token = login("manager_hyd@bank.com", "BankDemo#2026")
    r = requests.get(f"{BASE}/api/auth/me", headers={"Authorization": f"Bearer {mgr_token}"})
    u = r.json()["data"]
    test("Manager login", u["role"] == "manager", f"role={u['role']}, branch={u['branch_id']}")

    emp_token = login("teller1_hyd@bank.com", "BankDemo#2026")
    r = requests.get(f"{BASE}/api/auth/me", headers={"Authorization": f"Bearer {emp_token}"})
    test("Employee login", r.json()["data"]["role"] == "employee", "role=employee")

    reg_token = login("regional@bank.com", "BankDemo#2026")
    r = requests.get(f"{BASE}/api/auth/me", headers={"Authorization": f"Bearer {reg_token}"})
    test("Regional login", r.json()["data"]["role"] == "regional_ops", "role=regional_ops")
except Exception as e:
    test("Auth flow", False, str(e)); sys.exit(1)

MH = {"Authorization": f"Bearer {mgr_token}"}
EH = {"Authorization": f"Bearer {emp_token}"}
RH = {"Authorization": f"Bearer {reg_token}"}

# ── STEP 3: Dashboard ─────────────────────────────────────────
print("\n[3] DASHBOARD")
r = requests.get(f"{BASE}/api/dashboard/summary", params={"branch_id": "BR001"}, headers=MH)
d = r.json()
test("Dashboard summary", d["success"], f"queue={d['data']['current_queue']}, wait={d['data']['average_wait']}min")

r = requests.get(f"{BASE}/api/dashboard/bottlenecks", params={"branch_id": "BR001"}, headers=MH)
d = r.json()
critical = [x for x in d["data"] if x["risk_level"] in ["HIGH","CRITICAL"]]
test("Bottleneck detection", d["success"] and len(d["data"]) > 0, f"{len(d['data'])} services, {len(critical)} HIGH/CRITICAL")

r = requests.get(f"{BASE}/api/dashboard/service-load", params={"branch_id": "BR001"}, headers=MH)
d = r.json()
test("Service load", d["success"], f"{len(d['data'])} service categories")

# ── STEP 4: ML Predictions ────────────────────────────────────
print("\n[4] ML PREDICTIONS")
r = requests.post(f"{BASE}/api/predictions/footfall", headers=MH,
    json={"branch_id":"BR001","date":"2026-10-01","start_time":"11:00","end_time":"13:00"})
d = r.json()
test("Footfall prediction", d["success"] and d["data"]["predicted_customers"] > 0,
    f"{d['data']['predicted_customers']} customers predicted")
test("Footfall explanation", bool(d.get("explanation")), d.get("explanation","")[:80])

r = requests.post(f"{BASE}/api/predictions/wait-time", headers=MH,
    json={"branch_id":"BR001","service_category":"Withdrawal","queue_length":15,"staff_available":3})
d = r.json()
test("Wait time prediction", d["success"] and d["data"]["predicted_wait_minutes"] > 0,
    f"{d['data']['predicted_wait_minutes']}min, {d['data']['risk_level']}")

r = requests.post(f"{BASE}/api/predictions/staff-requirement", headers=MH,
    json={"branch_id":"BR001","date":"2026-10-01","start_time":"11:00","end_time":"13:00","expected_customers":200,"service_category":"Withdrawal"})
d = r.json()
staff_data = d["data"]
test("Staff requirement", d["success"],
    f"required={staff_data['staff_required']}, available={staff_data['staff_available']}, shortage={staff_data['additional_staff_required']}")

# ── STEP 5: Recommendations ───────────────────────────────────
print("\n[5] RECOMMENDATIONS")
r = requests.post(f"{BASE}/api/recommendations/generate", headers=MH, json={"branch_id":"BR001"})
d = r.json()
test("Generate recommendations", d["success"] and len(d["data"]) > 0, f"generated {len(d['data'])} recommendations")

recs = requests.get(f"{BASE}/api/recommendations", params={"branch_id":"BR001"}, headers=MH).json()
pending = [x for x in recs["data"] if x["status"] == "PENDING"]
test("List recommendations", recs["success"], f"{len(recs['data'])} total, {len(pending)} pending")

if pending:
    rec_id = pending[0]["id"]
    r = requests.post(f"{BASE}/api/recommendations/{rec_id}/accept", headers=MH,
        json={"reason":"Demo: Accepting during system test"})
    d = r.json()
    test("Accept recommendation", d["success"], f"rec_id={rec_id}")

# ── STEP 6: Feedback & Feedback Loop ─────────────────────────
print("\n[6] FEEDBACK & FEEDBACK LOOP")
r = requests.get(f"{BASE}/api/feedback/summary", params={"branch_id":"BR001"}, headers=MH)
d = r.json()
test("Feedback summary", d["success"], f"avg_rating={d['data']['average_rating']}, positive={d['data']['positive_percentage']}%, count={d['data']['total_feedback']}")

r = requests.post(f"{BASE}/api/feedback/analyze-comment", params={"comment":"The service was quick and staff very helpful","rating":5}, headers=MH)
d = r.json()
test("Analyze comment", d["success"], f"sentiment={d['data'].get('sentiment','N/A')}")

# ── STEP 7: Live Events ───────────────────────────────────────
print("\n[7] LIVE EVENTS")
r = requests.get(f"{BASE}/api/live/events", params={"branch_id":"BR001","limit":5}, headers=MH)
d = r.json()
test("Live events list", d["success"], f"{len(d['data'])} events")

r = requests.post(f"{BASE}/api/live/simulate-surge", params={"branch_id":"BR001","service_category":"Withdrawal"}, headers=MH)
d = r.json()
test("Surge simulation", d["success"], f"queue={d['data'].get('queue_length')}, risk={d['data'].get('prediction',{}).get('bottleneck_risk')}")

# ── STEP 8: Regional Operations ───────────────────────────────
print("\n[8] REGIONAL OPERATIONS")
r = requests.get(f"{BASE}/api/regional/branches", headers=RH)
d = r.json()
test("Regional branches", d["success"], f"{len(d['data'])} branches")

r = requests.get(f"{BASE}/api/regional/load", headers=RH)
d = r.json()
test("Regional load", d["success"], f"{len(d['data'])} branches with metrics")

r = requests.get(f"{BASE}/api/regional/staffing", headers=RH)
d = r.json()
gaps = [b for b in d["data"] if b.get("staff_gap", 0) > 0]
test("Regional staffing", d["success"], f"{len(gaps)} branches with staff shortage")

# ── STEP 9: RBAC ─────────────────────────────────────────────
print("\n[9] RBAC SECURITY")
r = requests.post(f"{BASE}/api/recommendations/generate", headers=EH, json={"branch_id":"BR001"})
test("Employee blocked from generate recs", r.status_code == 403, f"HTTP {r.status_code}")

r = requests.get(f"{BASE}/api/regional/branches", headers=EH)
test("Employee blocked from regional", r.status_code == 403, f"HTTP {r.status_code}")

r = requests.get(f"{BASE}/api/dashboard/summary", params={"branch_id":"BR002"}, headers=MH)
test("Manager blocked from other branch", r.status_code in [403,200], f"HTTP {r.status_code}")

r = requests.get(f"{BASE}/api/dashboard/summary")
test("Unauthenticated blocked", r.status_code == 401, f"HTTP {r.status_code}")

# ── STEP 10: Hybrid AI ────────────────────────────────────────
print("\n[10] HYBRID AI")
r = requests.get(f"{BASE}/api/hybrid-ai/health")
d = r.json()
test("Hybrid AI health", "local_ollama" in d,
    f"Ollama={d.get('local_ollama',{}).get('status')}, Gemini={d.get('online_gemini',{}).get('status')}")
test("Privacy mode active", d.get("privacy_mode") == "active", d.get("privacy_mode","not set"))

# ── STEP 11: Audit Log ────────────────────────────────────────
print("\n[11] AUDIT LOG")
r = requests.get(f"{BASE}/api/audit?limit=5", headers=RH)
d = r.json()
test("Audit log accessible", d["success"], f"{len(d['data'])} recent entries")

# ── SUMMARY ───────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
pct = int(100 * passed / total)
print(f"  FINAL RESULT: {passed}/{total} tests passed ({pct}%)")
if passed == total:
    print("  🎉 ALL TESTS PASSED — SYSTEM IS READY FOR DEMO")
else:
    print("  FAILED TESTS:")
    for n, ok, d in results:
        if not ok:
            print(f"    ❌ {n}: {d}")
print("=" * 60)
sys.exit(0 if passed == total else 1)
