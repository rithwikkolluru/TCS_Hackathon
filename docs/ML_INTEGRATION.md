# Machine Learning & Data Foundation Integration Guide
**Target Audience**: Members 2 (FastAPI/Backend & RBAC), Member 3 (WebSocket & Live Gateway), Member 4 (Frontend UI & Dashboard)

---

## 📌 Executive Summary

This document describes how to integrate with the Data Engineering and Machine Learning Foundation module built for **Intelligent Branch Service Load and Customer Experience Optimizer**.

All modules produce **clean, standard Python data structures (dictionaries, lists, DataFrames)** that are natively **JSON-serializable** for direct consumption by FastAPI endpoints, Pydantic schemas, and WebSocket message handlers.

---

## 📁 Data and Model File Artifacts

| Location | Content | Description |
| :--- | :--- | :--- |
| `data/raw/` | `visits.parquet`, `visits.csv`, `staff_roster.csv`, `appointments.csv`, `customer_feedback.csv` | 90-day synthetic Indian banking historical datasets (Zero PII). |
| `data/processed/` | `processed_visits.parquet`, `processed_visits.csv`, `processed_feedback.csv` | Cleaned, category-normalized, PII-verified datasets. |
| `data/features/` | `features_footfall.parquet`, `features_wait_time.parquet` | Aggregated lag, rolling, temporal, and ratio feature matrices. |
| `models/` | `footfall_model.pkl`, `wait_time_model.pkl` | Trained scikit-learn ML model pipelines. |
| `reports/` | `footfall_metrics.json`, `wait_time_metrics.json`, `service_category_analysis.csv`, `feedback_analysis.csv` | Model metrics, branch service statistics, and NLP sentiment analysis. |

---

## ⚡ Quick Start Commands

```bash
# 1. Run Complete Master Pipeline (Generate Data -> ETL -> Features -> Models -> Reports)
python run_ml_pipeline.py

# 2. Individual Pipeline Scripts
python scripts/generate_data.py   # Generate raw datasets
python scripts/run_etl.py          # Clean data & verify PII
python scripts/build_features.py   # Build ML feature matrices
python scripts/train_models.py     # Train models & export metrics
python scripts/validate_data.py    # Validate raw data schema & PII

# 3. Simulate Live Surge Events (for Member 3 WebSocket integration)
python scripts/live_event_simulator.py --surge --count 20

# 4. Run Pytest Test Suite
python -m pytest
```

---

## 🔌 Module API Reference for Members 2, 3 & 4

### 1. Unified Live Predictor (`src.models.live_predictor`)

Use this for live API endpoints (`/api/v1/predict/live`) and WebSocket streams.

```python
from src.models.live_predictor import predict_live

result = predict_live(
    branch_id="BR002",
    service_category="Loans - Payment and Sanctioning",
    current_queue=15,
    staff_available=2,
    recent_arrivals=25
)
```

#### JSON Response Format:
```json
{
  "branch_id": "BR002",
  "service_category": "Loans - Payment and Sanctioning",
  "timestamp": "2026-09-30 14:15:00",
  "current_queue": 15,
  "staff_available": 2,
  "predicted_wait_minutes": 32.4,
  "predicted_footfall": 30,
  "bottleneck_risk": "CRITICAL",
  "staff_required": 5,
  "staff_gap": 3,
  "explanation": "Loans - Payment and Sanctioning services at branch BR002 are at CRITICAL risk. Queue length of 15 severely exceeds threshold of 5. Expected wait time (32.4 mins) is critically high (>30 mins). Staff shortage: 2 active employees vs 5 required (Shortfall of 3). Arrival rate (50.0 cust/hr) exceeds branch capacity (6.0 cust/hr).",
  "digital_redirection": {
    "service_category": "Loans - Payment and Sanctioning",
    "customer_type": "Regular",
    "digital_available": false,
    "digital_channel": "Pre-approved Digital Loan Portal",
    "estimated_branch_time_saved_minutes": 35.0,
    "confidence": 0.45,
    "redirect_suitability": "Low",
    "instructions": "Check pre-approved loan eligibility online; final sanctioning requires branch verification.",
    "recommendation": "Branch visit is recommended for Loans - Payment and Sanctioning. Digital options are limited or require physical verification."
  }
}
```

---

### 2. Staff Requirement Calculation (`src.recommendation.staff_requirement`)

Use this for staff optimization endpoints (`/api/v1/staff/recommendation`).

```python
from src.recommendation.staff_requirement import calculate_required_staff

result = calculate_required_staff(
    expected_customers=200,
    service_category="Loans - Payment and Sanctioning",
    operating_duration_hours=2.0,
    employees_available=3,
    branch_id="BR002",
    time_window="11:00 AM - 1:00 PM"
)
```

#### JSON Response Format:
```json
{
  "branch_id": "BR002",
  "service_category": "Loans - Payment and Sanctioning",
  "time_window": "11:00 AM - 1:00 PM",
  "expected_customers": 200,
  "employees_available": 3,
  "employees_required": 8,
  "staff_gap": 5,
  "average_service_time_min": 35.0,
  "explanation": "For expected volume of 200 customers requesting Loans - Payment and Sanctioning during 11:00 AM - 1:00 PM, with average service time of 35.0 minutes, 8 employees are required. Currently 3 employees are available (Staff shortage: 5)."
}
```

---

### 3. Bottleneck Detector (`src.models.bottleneck_detector`)

Use this for branch risk assessments (`/api/v1/bottlenecks/detect`).

```python
from src.models.bottleneck_detector import BottleneckDetector

detector = BottleneckDetector()
result = detector.detect_bottleneck(
    branch_id="BR001",
    service_category="Money Transfer",
    queue_length=22,
    predicted_wait_minutes=25.0,
    staff_available=2,
    staff_required=4,
    arrival_rate=40.0
)
```

---

### 4. Digital Channel Redirection (`src.recommendation.digital_redirection`)

Use this for customer redirection suggestions (`/api/v1/redirection/suggest`).

```python
from src.recommendation.digital_redirection import get_digital_recommendation

result = get_digital_recommendation(
    service_category="Money Transfer",
    customer_type="Regular"
)
```

---

### 5. Customer Feedback NLP (`src.nlp.feedback_analysis`)

Use this for feedback sentiment analytics dashboard (`/api/v1/analytics/feedback`).

```python
from src.nlp.feedback_analysis import FeedbackAnalyzer

analyzer = FeedbackAnalyzer()
res = analyzer.analyze_comment("Quick service and polite counter staff!", rating=5)
```

---

### 6. Recommendation Feedback Loop (`src.recommendation.feedback_loop`)

Use this when managers accept/reject recommendations (`/api/v1/recommendations/feedback`).

```python
from src.recommendation.feedback_loop import record_recommendation_outcome

outcome = record_recommendation_outcome(
    recommendation_id="REC-101",
    branch_id="BR002",
    recommendation_type="Staff Allocation",
    predicted_value=5,
    action_taken="Deployed 2 extra tellers",
    action_status="accepted",
    actual_wait_after_action=10.5,
    actual_queue_after_action=3
)
```

---

## 🏢 Service Categories Enforced (Exact 14)

1. Loans - Payment and Sanctioning
2. Insurance
3. Deposit
4. Withdrawal
5. Account Opening
6. Credit Card
7. Debit Card
8. Locker Issuing
9. Cheque Withdrawal
10. KYC Related
11. Money Transfer
12. Aadhaar Linking
13. PAN Linking
14. Other
