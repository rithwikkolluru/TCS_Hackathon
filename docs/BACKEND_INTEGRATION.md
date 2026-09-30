# Backend, Database, Security & Real-Time Integration Guide (Member 2)
**Target Audience**: Member 3 (Real-Time WebSocket / Gateway Engineer), Member 4 (React Frontend / Dashboard Engineer)

---

## 📌 Executive Summary

Member 2 has implemented the complete **FastAPI backend, relational database, JWT security gate, RBAC layer, and real-time WebSocket alert infrastructure** for the **Intelligent Branch Service Load and Customer Experience Optimizer**.

All APIs return consistent, typed JSON responses enclosed in a standardized response envelope, strictly sanitized of any Customer PII (Zero Aadhaar, PAN, Phone, Email, or Account Numbers).

---

## 🌐 Base URL & Interactive API Documentation

- **Base URL**: `http://localhost:8000`
- **Interactive Swagger UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **ReDoc Documentation**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
- **System Health Check**: `GET http://localhost:8000/health`

---

## 🔐 Authentication & JWT Standard

All protected routes require an HTTP `Authorization` header containing the JWT Bearer token:
```http
Authorization: Bearer <access_token>
```

### Standard Response Envelope:
```json
{
  "success": true,
  "data": { ... },
  "explanation": "Human-readable context or explanation",
  "timestamp": "2026-09-30 14:45:00"
}
```

### Error Envelope:
```json
{
  "success": false,
  "error": {
    "code": "403_FORBIDDEN",
    "message": "Branch isolation policy violation: User assigned to branch 'BR001' cannot access branch 'BR002'."
  }
}
```

---

## 👥 Demo Accounts & Role-Based Access Control (RBAC)

| Email | Password | Role | Branch Assignment | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| `regional@bank.com` | `BankDemo#2026` | `regional_ops` | `None` (Network Wide) | Access all 8 branches, network bottlenecks, regional staffing, cross-branch comparisons. |
| `manager_hyd@bank.com` | `BankDemo#2026` | `manager` | `BR001` (Hyderabad Central) | Full branch dashboard, ML predictions, bottleneck alerts, generate & accept/reject recommendations, audit logs. |
| `manager_kukatpally@bank.com` | `BankDemo#2026` | `manager` | `BR002` (Hyderabad Kukatpally) | Same as above, restricted strictly to `BR002`. |
| `teller1_hyd@bank.com` | `BankDemo#2026` | `employee` | `BR001` (Hyderabad Central) | View branch queues, bottleneck alerts, service loads. (Cannot accept/reject recommendations). |

---

## 🔌 Core API Endpoints for Frontend (Member 4)

### 1. Authentication
- `POST /api/auth/login`: Authenticate with `{"email": "...", "password": "..."}` -> returns `access_token` and user profile.
- `GET /api/auth/me`: Get current logged-in user profile.
- `POST /api/auth/logout`: Log out current user and write audit entry.

### 2. Dashboard KPIs
- `GET /api/dashboard/summary?branch_id=BR001`: Returns current queues, average wait time, predicted traffic, high-risk bottleneck count, active recommendations.
- `GET /api/dashboard/bottlenecks?branch_id=BR001`: Returns risk assessment (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) for all 14 service categories.
- `GET /api/dashboard/service-load?branch_id=BR001`: Returns breakdown for all 14 strictly enforced banking service categories.

### 3. ML Predictions
- `POST /api/predictions/footfall`:
  ```json
  // Request
  {
    "branch_id": "BR001",
    "date": "2026-10-01",
    "start_time": "11:00",
    "end_time": "13:00"
  }
  // Response
  {
    "success": true,
    "data": {
      "branch_id": "BR001",
      "predicted_customers": 210,
      "time_slot": "11:00-13:00",
      "date": "2026-10-01",
      "category_breakdown": { "Withdrawal": 15, "Loans - Payment and Sanctioning": 15, ... }
    },
    "explanation": "Expected footfall is estimated at 210 customers for branch BR001 at 11:00 primarily because it falls during the salary/pension payment period (1st-5th of month), 10:00 AM - 11:30 AM is the morning peak operating window."
  }
  ```
- `POST /api/predictions/wait-time`:
  ```json
  // Request
  {
    "branch_id": "BR001",
    "service_category": "Withdrawal",
    "queue_length": 25,
    "staff_available": 3
  }
  ```
- `POST /api/predictions/staff-requirement`:
  Calculates required employees for future time slots considering service processing durations and safety buffers.

### 4. Recommendation Management
- `GET /api/recommendations?branch_id=BR001&status_filter=PENDING`: List active AI recommendations.
- `POST /api/recommendations/generate`: Trigger AI recommendation generation based on current bottleneck risks.
- `POST /api/recommendations/{id}/accept`: Manager approves recommendation.
- `POST /api/recommendations/{id}/reject`: Manager declines recommendation with reason.
- `GET /api/recommendations/digital-redirection?service_category=Money%20Transfer`: Get digital channel guidance.

### 5. Recommendation Outcome Feedback Loop
- `POST /api/feedback/recommendation-outcome`:
  ```json
  // Request
  {
    "recommendation_id": 10,
    "action": "ACCEPTED",
    "actual_wait_after_action": 14.5,
    "actual_queue_after_action": 4,
    "reason": "Wait time decreased after opening extra teller counter."
  }
  // Response
  {
    "success": true,
    "data": {
      "impact": "POSITIVE",
      "wait_reduction_minutes": 17.5,
      "queue_reduction": 14,
      "message": "Outcome recorded successfully. Impact evaluated as POSITIVE (Wait time reduced by 17.5 minutes)."
    }
  }
  ```

### 6. Customer Feedback Sentiment NLP
- `GET /api/feedback/summary?branch_id=BR001`: Returns aggregated sentiment metrics (positive %, negative %, neutral %), top topics (`waiting_time`, `staff_behavior`, etc.), and branch sentiment scores with zero raw customer identifiers.

---

## ⚡ Real-Time WebSocket Gateway for Member 3

Connect to the authenticated WebSocket alert gateway:
```
ws://localhost:8000/ws/alerts?token=<jwt_access_token>
```

### Event Payload Example (Surge / Critical Bottleneck):
```json
{
  "event": "BOTTLENECK_ALERT",
  "branch_id": "BR001",
  "service_category": "Withdrawal",
  "risk_level": "CRITICAL",
  "message": "CRITICAL: Withdrawal queue at branch BR001 is predicted to exceed 21.5 minutes.",
  "data": {
    "queue_length": 49,
    "predicted_wait_minutes": 21.5,
    "staff_available": 1,
    "staff_required": 4,
    "staff_gap": 3,
    "explanation": "Withdrawal services at branch BR001 are at CRITICAL risk. Queue length of 49 severely exceeds threshold of 15.",
    "digital_redirection": {
      "digital_available": true,
      "digital_channel": "24/7 ATM Kiosk",
      "instructions": "Withdraw cash from any nationwide ATM kiosk."
    }
  },
  "timestamp": "2026-09-30 14:53:00"
}
```

---

## 🚀 How to Run Backend Locally

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Seed Database with Demo Branches, Users, Visits & Recommendations
python scripts/seed_database.py

# 3. Start Backend Server
uvicorn backend.app.main:app --reload --port 8000

# 4. Run Demonstration Scenario
python scripts/demo_scenario.py

# 5. Run Test Suite
pytest backend/tests/
```
