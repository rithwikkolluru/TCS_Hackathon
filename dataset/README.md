# 📊 Official Banking Dataset — Intelligent Branch Service Load & CX Optimizer

This directory contains the production-grade synthetic banking operations dataset simulating **8 retail bank branches**, **14 banking service categories**, and **350,000+ data points** capturing realistic customer footfall, counter service times, queuing bottlenecks, and staff allocations.

---

## 🗂️ Dataset Architecture & Files

| File | Records | Format | Description |
|---|---|---|---|
| [`1_branches_network.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/1_branches_network.csv) | 8 | CSV | Tier-1 & Tier-2 branch network, geo-coordinates, active counters, managers |
| [`2_customer_visits_sample.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/2_customer_visits_sample.csv) | 1,500 | CSV | Representative customer journeys (arrival, token, counter, wait time, SLA flag) |
| [`3_service_bottlenecks_kpi.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/3_service_bottlenecks_kpi.csv) | 14 | CSV | SLA benchmarks, average wait times, bottleneck risk classification |
| [`4_customer_feedback_sentiment.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/4_customer_feedback_sentiment.csv) | 500 | CSV | Customer ratings, reviews, NLP sentiment scores, operational topics |
| [`5_staff_roster_allocation.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/5_staff_roster_allocation.csv) | 102 | CSV | Bank officers, roles, shift timings, cross-skilling tags, absence records |
| [`6_appointments_schedule.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/6_appointments_schedule.csv) | 1,000 | CSV | Booked vs walk-in appointments, arrival punctuality, no-show rate |
| [`7_ml_footfall_features_sample.csv`](file:///Users/krithvik/Desktop/TCS_Hackathon/dataset/7_ml_footfall_features_sample.csv) | 1,000 | CSV | Engineered feature store (lagged footfall, cyclical hour, day-of-week) |
| `data/raw/visits.csv` | **99,801** | CSV | Full underlying transaction history used to train ML models |

---

## 📋 Data Dictionary (Key Customer Visit Schema)

| Field | Type | Example | Description |
|---|---|---|---|
| `visit_id` | String | `VIS-20260601-100001` | Unique transaction journey identifier |
| `branch_id` | String | `BR001` | Branch Code (`BR001` to `BR008`) |
| `arrival_timestamp` | DateTime | `2026-06-01 09:01:33` | Timestamp when customer enters branch |
| `service_category` | String | `Loans - Sanctioning` | One of 14 standard retail banking services |
| `customer_type` | String | `Regular` / `Priority` | Customer segment (Senior Citizen, NRI, Regular) |
| `token_number` | String | `K329`, `W457` | Service-specific counter queue ticket |
| `counter_id` | String | `C7`, `C12` | Assigned service desk counter |
| `waiting_time_minutes`| Float | `10.05` | Measured time from token generation to counter call |
| `service_time_minutes`| Float | `13.24` | Duration spent at the counter with the teller |
| `employees_available` | Integer | `15` | Active desk employees at time of customer arrival |
| `queue_length_at_arrival`| Integer | `8` | Number of waiting customers in the category |
| `sla_breached` | Boolean | `False` | Flag indicating if wait exceeded the 20-minute threshold |

---

## 🏦 8-Branch Regional Network Coverage

| Branch ID | Branch Name | City | State | Tier | Counters | Daily Footfall |
|---|---|---|---|---|---|---|
| `BR001` | Hyderabad Central | Hyderabad | Telangana | Tier-1 | 12 | 485 |
| `BR002` | Hyderabad Kukatpally | Hyderabad | Telangana | Tier-1 | 14 | 520 |
| `BR003` | Secunderabad Station | Secunderabad | Telangana | Tier-1 | 10 | 390 |
| `BR004` | Warangal Main | Warangal | Telangana | Tier-2 | 8 | 295 |
| `BR005` | Vijayawada Commercial | Vijayawada | Andhra Pradesh | Tier-2 | 10 | 360 |
| `BR006` | Karimnagar Market | Karimnagar | Telangana | Tier-2 | 6 | 240 |
| `BR007` | Visakhapatnam Central | Visakhapatnam | Andhra Pradesh | Tier-1 | 11 | 440 |
| `BR008` | Tirupati Pilgrim Road | Tirupati | Andhra Pradesh | Tier-2 | 8 | 310 |

---

## ⚡ Real-World Banking Dynamics Modeled

1. **Morning Rush (10:00 AM – 11:30 AM)**: High volume of cash withdrawals and deposits.
2. **Lunchtime Bottleneck (1:00 PM – 2:30 PM)**: Counter staffing drops due to staggered lunches, causing loan & account opening queues to surge.
3. **Month-End & Salary Peaks**: 30% footfall increase on the 1st and last working days of each month.
4. **Service Variance**: Fast cash transactions (3–5 min) vs complex documentation like Loans and Account Opening (18–30 min).

---

## 🔒 Privacy & Regulatory Compliance
- **Zero Personally Identifiable Information (PII)**: All simulated customer records contain token IDs, timestamps, and service categories without Aadhaar, PAN, phone numbers, or account balances.
- **Synthetically Calibrated**: Modeled after standard Indian retail banking queue dynamics adhering to regulatory service level standards.

---

## 💻 Quick CLI Inspection
Run the terminal inspector at any time:
```bash
python3 scripts/explore_dataset.py
```
