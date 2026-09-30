"""
Interactive Dataset Showcase CLI for Judges & Evaluators.
Run:
    python3 scripts/explore_dataset.py
"""
import os
import pandas as pd

def header(title):
    print("\n" + "=" * 70)
    print(f"  📊 {title}")
    print("=" * 70)

def main():
    print("""
┌────────────────────────────────────────────────────────────────────────┐
│  INTELLIGENT BRANCH OPTIMIZER — OFFICIAL DATASET CATALOG & EXPLORER    │
│  Designed for High-Volume Retail Banking Service & Footfall Analytics  │
└────────────────────────────────────────────────────────────────────────┘
""")
    
    # 1. Overview & Volume
    header("DATASET VOLUMES & ARCHITECTURE")
    volumes = [
        ("Full Customer Transactions (data/raw/visits.csv)", "99,801 rows", "Customer arrival, wait, service duration, token, counter"),
        ("Clean Sample Dataset (dataset/2_customer_visits_sample.csv)", "1,500 rows", "Fast-loading representative sample for audit/demo"),
        ("Branch Network Master (dataset/1_branches_network.csv)", "8 branches", "Tier-1 & Tier-2 branches with geo-coords, counters"),
        ("Service Bottlenecks & KPIs (dataset/3_service_bottlenecks_kpi.csv)", "14 services", "Target vs actual wait times, SLA compliance %"),
        ("Customer Feedback & NLP (dataset/4_customer_feedback_sentiment.csv)", "500 reviews", "Ratings, text reviews, sentiment categories"),
        ("Staff Roster & Skills (dataset/5_staff_roster_allocation.csv)", "102 officers", "Shifts, cross-skilling tags, absence history"),
        ("Customer Appointments (dataset/6_appointments_schedule.csv)", "1,000 samples", "Pre-booked vs walk-in arrival and no-show flags"),
        ("ML Feature Store (dataset/7_ml_footfall_features_sample.csv)", "45,319 total", "Time-lags, day of week, weather, cyclical encodings"),
    ]
    print(f"{'Dataset Table':<42} | {'Volume':<13} | {'Content'}")
    print("-" * 95)
    for name, vol, desc in volumes:
        print(f"{name:<42} | {vol:<13} | {desc}")
    print(f"\n👉 TOTAL SYSTEM DATASET VOLUME: 350,000+ data points across 8 branches")

    # 2. Branch Network Preview
    header("BRANCH NETWORK MASTER (dataset/1_branches_network.csv)")
    df_b = pd.read_csv("dataset/1_branches_network.csv")
    print(df_b[["branch_id", "branch_name", "city", "tier", "total_counters", "daily_avg_footfall", "avg_wait_min"]].to_string(index=False))

    # 3. Service Bottlenecks
    header("TOP BOTTLENECK SERVICES & SLA COMPLIANCE (dataset/3_service_bottlenecks_kpi.csv)")
    df_kpi = pd.read_csv("dataset/3_service_bottlenecks_kpi.csv")
    print(df_kpi[["service_category", "target_wait_min", "avg_wait_min", "sla_compliance_pct", "bottleneck_risk"]].head(8).to_string(index=False))

    # 4. Customer Visits Sample
    header("SAMPLE CUSTOMER JOURNEYS (dataset/2_customer_visits_sample.csv)")
    df_v = pd.read_csv("dataset/2_customer_visits_sample.csv")
    cols = ["visit_id", "branch_id", "service_category", "token_number", "waiting_time_minutes", "service_time_minutes", "sla_breached"]
    print(df_v[cols].head(6).to_string(index=False))

    # 5. Customer Feedback Sentiment
    header("NLP FEEDBACK & SENTIMENT SUMMARY (dataset/4_customer_feedback_sentiment.csv)")
    df_fb = pd.read_csv("dataset/4_customer_feedback_sentiment.csv")
    sent_counts = df_fb["sentiment_category"].value_counts()
    for cat, count in sent_counts.items():
        pct = 100 * count / len(df_fb)
        bar = "█" * int(pct / 4)
        print(f"  {cat:<10} : {count:3d} ({pct:5.1f}%) | {bar}")

    print("\n" + "=" * 70)
    print("  ✅ All CSV files ready to inspect in: /Users/krithvik/Desktop/TCS_Hackathon/dataset/")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
