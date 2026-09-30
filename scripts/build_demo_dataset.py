"""
Builds a dedicated, presentation-ready dataset package in `dataset/` for demonstration to judges.
Includes:
- 1_branches_network.csv
- 2_customer_visits_sample.csv
- 3_service_bottlenecks_kpi.csv
- 4_customer_feedback_sentiment.csv
- 5_staff_roster_allocation.csv
- 6_appointments_schedule.csv
- 7_ml_footfall_features_sample.csv
"""
import os
import pandas as pd
import numpy as np

DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

print("🚀 Assembling presentation dataset for judges...")

# 1. Branch Network
branches_data = [
    {"branch_id": "BR001", "branch_name": "Hyderabad Central", "city": "Hyderabad", "state": "Telangana", "tier": "Tier-1", "total_counters": 12, "active_counters": 10, "daily_avg_footfall": 485, "avg_wait_min": 18.4, "manager": "Ramesh Sharma"},
    {"branch_id": "BR002", "branch_name": "Hyderabad Kukatpally", "city": "Hyderabad", "state": "Telangana", "tier": "Tier-1", "total_counters": 14, "active_counters": 11, "daily_avg_footfall": 520, "avg_wait_min": 22.1, "manager": "Priya Reddy"},
    {"branch_id": "BR003", "branch_name": "Secunderabad Station", "city": "Secunderabad", "state": "Telangana", "tier": "Tier-1", "total_counters": 10, "active_counters": 8, "daily_avg_footfall": 390, "avg_wait_min": 16.8, "manager": "Vikas Nair"},
    {"branch_id": "BR004", "branch_name": "Warangal Main", "city": "Warangal", "state": "Telangana", "tier": "Tier-2", "total_counters": 8, "active_counters": 6, "daily_avg_footfall": 295, "avg_wait_min": 14.2, "manager": "Sunita Rao"},
    {"branch_id": "BR005", "branch_name": "Vijayawada Commercial", "city": "Vijayawada", "state": "Andhra Pradesh", "tier": "Tier-2", "total_counters": 10, "active_counters": 8, "daily_avg_footfall": 360, "avg_wait_min": 19.5, "manager": "Kiran Kumar"},
    {"branch_id": "BR006", "branch_name": "Karimnagar Market", "city": "Karimnagar", "state": "Telangana", "tier": "Tier-2", "total_counters": 6, "active_counters": 5, "daily_avg_footfall": 240, "avg_wait_min": 12.8, "manager": "Anil Goud"},
    {"branch_id": "BR007", "branch_name": "Visakhapatnam Central", "city": "Visakhapatnam", "state": "Andhra Pradesh", "tier": "Tier-1", "total_counters": 11, "active_counters": 9, "daily_avg_footfall": 440, "avg_wait_min": 17.6, "manager": "Deepika Varma"},
    {"branch_id": "BR008", "branch_name": "Tirupati Pilgrim Road", "city": "Tirupati", "state": "Andhra Pradesh", "tier": "Tier-2", "total_counters": 8, "active_counters": 6, "daily_avg_footfall": 310, "avg_wait_min": 21.0, "manager": "Srinivasulu M"}
]
df_branches = pd.DataFrame(branches_data)
df_branches.to_csv(os.path.join(DATASET_DIR, "1_branches_network.csv"), index=False)
print("  ✅ 1_branches_network.csv generated (8 branches)")

# 2. Customer Visits Sample (1,500 representative rows for easy opening in Excel/Numbers)
if os.path.exists("data/raw/visits.csv"):
    df_visits = pd.read_csv("data/raw/visits.csv")
    df_sample = df_visits.head(1500).copy()
    # Add helpful SLA status column
    df_sample["sla_breached"] = df_sample["waiting_time_minutes"] > 20.0
    df_sample.to_csv(os.path.join(DATASET_DIR, "2_customer_visits_sample.csv"), index=False)
    print(f"  ✅ 2_customer_visits_sample.csv generated (1,500 rows, sampled from {len(df_visits):,} total records)")

# 3. Service Bottlenecks & KPI Benchmarks
services_kpi = [
    {"service_category": "Loans - Payment and Sanctioning", "target_wait_min": 15.0, "avg_wait_min": 28.4, "avg_service_min": 24.5, "bottleneck_risk": "CRITICAL", "sla_compliance_pct": 58.2, "recommended_counters": 3},
    {"service_category": "Account Opening", "target_wait_min": 12.0, "avg_wait_min": 22.1, "avg_service_min": 18.2, "bottleneck_risk": "HIGH", "sla_compliance_pct": 67.4, "recommended_counters": 2},
    {"service_category": "KYC Related", "target_wait_min": 10.0, "avg_wait_min": 17.5, "avg_service_min": 12.8, "bottleneck_risk": "HIGH", "sla_compliance_pct": 72.1, "recommended_counters": 2},
    {"service_category": "Foreign Exchange", "target_wait_min": 10.0, "avg_wait_min": 16.8, "avg_service_min": 14.0, "bottleneck_risk": "HIGH", "sla_compliance_pct": 74.0, "recommended_counters": 1},
    {"service_category": "Wealth Management", "target_wait_min": 15.0, "avg_wait_min": 16.2, "avg_service_min": 26.0, "bottleneck_risk": "MEDIUM", "sla_compliance_pct": 79.5, "recommended_counters": 1},
    {"service_category": "Demand Draft", "target_wait_min": 8.0, "avg_wait_min": 11.4, "avg_service_min": 7.5, "bottleneck_risk": "MEDIUM", "sla_compliance_pct": 82.3, "recommended_counters": 1},
    {"service_category": "Cheque Clearance", "target_wait_min": 8.0, "avg_wait_min": 10.2, "avg_service_min": 6.8, "bottleneck_risk": "MEDIUM", "sla_compliance_pct": 85.0, "recommended_counters": 1},
    {"service_category": "Locker Services", "target_wait_min": 10.0, "avg_wait_min": 9.8, "avg_service_min": 11.2, "bottleneck_risk": "LOW", "sla_compliance_pct": 89.2, "recommended_counters": 1},
    {"service_category": "Deposit", "target_wait_min": 6.0, "avg_wait_min": 7.4, "avg_service_min": 5.1, "bottleneck_risk": "LOW", "sla_compliance_pct": 91.5, "recommended_counters": 2},
    {"service_category": "Withdrawal", "target_wait_min": 5.0, "avg_wait_min": 6.2, "avg_service_min": 4.2, "bottleneck_risk": "LOW", "sla_compliance_pct": 93.0, "recommended_counters": 2},
    {"service_category": "Debit Card", "target_wait_min": 8.0, "avg_wait_min": 7.9, "avg_service_min": 6.0, "bottleneck_risk": "LOW", "sla_compliance_pct": 92.4, "recommended_counters": 1},
    {"service_category": "Credit Card", "target_wait_min": 8.0, "avg_wait_min": 8.5, "avg_service_min": 7.1, "bottleneck_risk": "LOW", "sla_compliance_pct": 90.1, "recommended_counters": 1},
    {"service_category": "Insurance", "target_wait_min": 12.0, "avg_wait_min": 11.8, "avg_service_min": 15.4, "bottleneck_risk": "LOW", "sla_compliance_pct": 88.6, "recommended_counters": 1},
    {"service_category": "Government Schemes", "target_wait_min": 10.0, "avg_wait_min": 13.2, "avg_service_min": 11.6, "bottleneck_risk": "MEDIUM", "sla_compliance_pct": 80.8, "recommended_counters": 1},
]
df_kpi = pd.DataFrame(services_kpi)
df_kpi.to_csv(os.path.join(DATASET_DIR, "3_service_bottlenecks_kpi.csv"), index=False)
print("  ✅ 3_service_bottlenecks_kpi.csv generated (14 service benchmarks)")

# 4. Customer Feedback & Sentiment
if os.path.exists("data/raw/customer_feedback.csv"):
    df_fb = pd.read_csv("data/raw/customer_feedback.csv")
    # Add sentiment category column based on rating
    df_fb["sentiment_category"] = df_fb["rating"].apply(lambda r: "Positive" if r >= 4 else ("Neutral" if r == 3 else "Negative"))
    df_fb.to_csv(os.path.join(DATASET_DIR, "4_customer_feedback_sentiment.csv"), index=False)
    print(f"  ✅ 4_customer_feedback_sentiment.csv generated ({len(df_fb)} feedback rows)")

# 5. Staff Roster & Cross-Skilling
if os.path.exists("data/raw/staff_roster.csv"):
    df_roster = pd.read_csv("data/raw/staff_roster.csv")
    df_roster.to_csv(os.path.join(DATASET_DIR, "5_staff_roster_allocation.csv"), index=False)
    print(f"  ✅ 5_staff_roster_allocation.csv generated ({len(df_roster)} staff members)")

# 6. Appointments Schedule
if os.path.exists("data/raw/appointments.csv"):
    df_appt = pd.read_csv("data/raw/appointments.csv")
    df_appt.head(1000).to_csv(os.path.join(DATASET_DIR, "6_appointments_schedule.csv"), index=False)
    print(f"  ✅ 6_appointments_schedule.csv generated (1,000 appointment samples)")

# 7. ML Footfall Features Sample
if os.path.exists("data/features/features_footfall.csv"):
    df_feat = pd.read_csv("data/features/features_footfall.csv")
    df_feat.head(1000).to_csv(os.path.join(DATASET_DIR, "7_ml_footfall_features_sample.csv"), index=False)
    print(f"  ✅ 7_ml_footfall_features_sample.csv generated (1,000 ML feature rows)")

print("\n🎉 Dataset generation complete in directory: dataset/")
