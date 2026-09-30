import os
import sys
import datetime
import random
from pathlib import Path
import pandas as pd

# Add repo root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.db.database import SessionLocal, engine, Base
from backend.app.db.models import User, Branch, Staff, CustomerReport, Recommendation, RecommendationAction, Feedback, AuditLog
from backend.app.core.security import hash_password
from src.utils.config import BRANCHES, SERVICE_CATEGORIES, RAW_DATA_DIR


def seed_database():
    print("==================================================")
    print("      SEEDING BANKING AI OPTIMIZER DATABASE       ")
    print("==================================================")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    demo_password = os.getenv("DEMO_PASSWORD", "BankDemo#2026")
    hashed_pwd = hash_password(demo_password)

    try:
        # 1. Seed Branches
        print("[1/6] Seeding Branches...")
        branch_coords = {
            "BR001": (17.3850, 78.4867, "Abids Road, Gunfoundry, Hyderabad, Telangana 500001"),
            "BR002": (17.4933, 78.3914, "KPHB Colony Phase 1, Kukatpally, Hyderabad 500072"),
            "BR003": (17.4399, 78.4983, "MG Road, Secunderabad, Telangana 500003"),
            "BR004": (17.9689, 79.5941, "Main Road, Hanamkonda, Warangal, Telangana 506001"),
            "BR005": (16.5062, 80.6480, "Besant Road, Governorpet, Vijayawada, Andhra Pradesh 520002"),
            "BR006": (18.4386, 79.1288, "Collectorate Road, Mukarampura, Karimnagar 505001"),
            "BR007": (17.6868, 83.2185, "Dwaraka Nagar 2nd Lane, Visakhapatnam, Andhra Pradesh 530016"),
            "BR008": (13.6288, 79.4192, "Gandhi Road, Balaji Colony, Tirupati, Andhra Pradesh 517501")
        }

        for b in BRANCHES:
            b_id = b["branch_id"]
            existing = db.query(Branch).filter(Branch.branch_code == b_id).first()
            lat, lon, addr = branch_coords.get(b_id, (17.3850, 78.4867, "Commercial Complex, Main Road"))
            state = "Andhra Pradesh" if b_id in ["BR005", "BR007", "BR008"] else "Telangana"

            if not existing:
                br = Branch(
                    branch_code=b_id,
                    branch_name=b["branch_name"],
                    city=b["city"],
                    state=state,
                    address=addr,
                    latitude=lat,
                    longitude=lon,
                    total_counters=b.get("total_counters", 10),
                    created_at=datetime.datetime.utcnow()
                )
                db.add(br)
        db.commit()
        print(f"  ✓ Seeded {len(BRANCHES)} banking branches.")

        # 2. Seed Users
        print("[2/6] Seeding Demo Users (Regional Ops, Managers, Employees)...")
        demo_users = [
            # Regional Ops
            {
                "name": "Regional Ops Director",
                "email": "regional@bank.com",
                "role": "regional_ops",
                "branch_id": None
            },
            # Managers
            {
                "name": "Hyderabad Central Branch Manager",
                "email": "manager_hyd@bank.com",
                "role": "manager",
                "branch_id": "BR001"
            },
            {
                "name": "Kukatpally Branch Manager",
                "email": "manager_kukatpally@bank.com",
                "role": "manager",
                "branch_id": "BR002"
            },
            {
                "name": "Secunderabad Branch Manager",
                "email": "manager_secunderabad@bank.com",
                "role": "manager",
                "branch_id": "BR003"
            },
            {
                "name": "Warangal Branch Manager",
                "email": "manager_warangal@bank.com",
                "role": "manager",
                "branch_id": "BR004"
            },
            {
                "name": "Vijayawada Branch Manager",
                "email": "manager_vijayawada@bank.com",
                "role": "manager",
                "branch_id": "BR005"
            },
            # Employees
            {
                "name": "Hyderabad Cash Teller 1",
                "email": "teller1_hyd@bank.com",
                "role": "employee",
                "branch_id": "BR001"
            },
            {
                "name": "Hyderabad Cash Teller 2",
                "email": "teller2_hyd@bank.com",
                "role": "employee",
                "branch_id": "BR001"
            },
            {
                "name": "Hyderabad Loan Officer",
                "email": "loan_officer_hyd@bank.com",
                "role": "employee",
                "branch_id": "BR001"
            },
            {
                "name": "Hyderabad KYC Officer",
                "email": "kyc_officer_hyd@bank.com",
                "role": "employee",
                "branch_id": "BR001"
            },
            {
                "name": "Kukatpally Counter Officer",
                "email": "teller_kukatpally@bank.com",
                "role": "employee",
                "branch_id": "BR002"
            }
        ]

        created_users = {}
        for u in demo_users:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                usr = User(
                    name=u["name"],
                    email=u["email"],
                    password_hash=hashed_pwd,
                    role=u["role"],
                    branch_id=u["branch_id"],
                    is_active=True,
                    created_at=datetime.datetime.utcnow()
                )
                db.add(usr)
                db.flush()
                created_users[u["email"]] = usr
            else:
                created_users[u["email"]] = existing
        db.commit()
        print(f"  ✓ Seeded {len(demo_users)} authenticated staff users.")

        # 3. Seed Staff Roster
        print("[3/6] Seeding Staff Roster Assignments...")
        if db.query(Staff).count() == 0:
            staff_configs = [
                ("BR001", "Teller", "Withdrawal,Deposit,Money Transfer,Cheque Withdrawal"),
                ("BR001", "Loan Officer", "Loans - Payment and Sanctioning,Insurance"),
                ("BR001", "KYC Officer", "KYC Related,Aadhaar Linking,PAN Linking"),
                ("BR001", "Account Officer", "Account Opening,Debit Card,Credit Card"),
                ("BR001", "General Employee", "Locker Issuing,Other"),
                ("BR002", "Teller", "Withdrawal,Deposit,Money Transfer"),
                ("BR002", "Loan Officer", "Loans - Payment and Sanctioning"),
                ("BR002", "KYC Officer", "KYC Related,Aadhaar Linking,PAN Linking"),
                ("BR003", "Teller", "Withdrawal,Deposit"),
                ("BR004", "Teller", "Withdrawal,Deposit"),
                ("BR005", "Teller", "Withdrawal,Deposit"),
            ]
            for branch_id, role, services in staff_configs:
                st = Staff(
                    branch_id=branch_id,
                    employee_role=role,
                    supported_services=services,
                    status="AVAILABLE",
                    shift_start="09:00",
                    shift_end="17:00",
                    created_at=datetime.datetime.utcnow()
                )
                db.add(st)
            db.commit()
            print("  ✓ Seeded staff roster assignments.")

        # 4. Seed Sanitized Customer Reports (Visits)
        print("[4/6] Seeding Sanitized Historical Visits...")
        if db.query(CustomerReport).count() == 0:
            visits_csv = RAW_DATA_DIR / "visits.csv"
            if visits_csv.exists():
                df_visits = pd.read_csv(visits_csv, nrows=250)
                for _, row in df_visits.iterrows():
                    arr_time = pd.to_datetime(row.get("arrival_timestamp", datetime.datetime.now()))
                    cr = CustomerReport(
                        branch_id=str(row.get("branch_id", "BR001")),
                        service_category=str(row.get("service_category", "Withdrawal")),
                        arrival_time=arr_time.to_pydatetime(),
                        waiting_time_minutes=float(row.get("waiting_time_minutes", 10.0)),
                        service_time_minutes=float(row.get("service_time_minutes", 8.0)),
                        token_number=str(row.get("token_number", "TK101")),
                        counter_id=str(row.get("counter_id", "C1")),
                        status=str(row.get("completed_status", "COMPLETED"))
                    )
                    db.add(cr)
                db.commit()
                print("  ✓ Seeded 250 historical visit records (Strictly Zero PII).")

        # 5. Seed Customer Feedback
        print("[5/6] Seeding Sanitized Feedback Records...")
        if db.query(Feedback).count() == 0:
            fbk_csv = RAW_DATA_DIR / "customer_feedback.csv"
            if fbk_csv.exists():
                df_fbk = pd.read_csv(fbk_csv, nrows=100)
                for _, row in df_fbk.iterrows():
                    fb = Feedback(
                        feedback_id=str(row.get("feedback_id", f"FB-{random.randint(100,999)}")),
                        branch_id=str(row.get("branch_id", "BR001")),
                        service_category=str(row.get("service_category", "Withdrawal")),
                        rating=int(row.get("rating", 4)),
                        comment=str(row.get("comment", "Quick and polite service at the counter.")),
                        sentiment="Positive" if int(row.get("rating", 4)) >= 4 else ("Negative" if int(row.get("rating", 4)) <= 2 else "Neutral"),
                        sentiment_score=0.4 if int(row.get("rating", 4)) >= 4 else -0.3,
                        topic="general_service"
                    )
                    db.add(fb)
                db.commit()
                print("  ✓ Seeded 100 customer feedback records.")

        # 6. Seed Sample Recommendations & Audit Logs
        print("[6/6] Seeding Initial AI Recommendations & Audit Logs...")
        if db.query(Recommendation).count() == 0:
            sample_recs = [
                Recommendation(
                    branch_id="BR001",
                    service_category="Loans - Payment and Sanctioning",
                    recommendation_type="STAFFING",
                    recommendation_text="Deploy 2 additional loan officers between 11:00 AM and 1:00 PM.",
                    explanation="Expected footfall spikes to ~200 customers with 35 min avg service time. 2 extra staff will reduce projected wait time from 42 mins to 14 mins.",
                    risk_level="HIGH",
                    status="PENDING",
                    created_at=datetime.datetime.utcnow()
                ),
                Recommendation(
                    branch_id="BR001",
                    service_category="Money Transfer",
                    recommendation_type="DIGITAL_REDIRECTION",
                    recommendation_text="Redirect routine fund transfers to Mobile Banking & UPI.",
                    explanation="Money Transfer has 95% digital suitability and saves approximately 5.0 minutes of teller queue pressure per customer.",
                    risk_level="MEDIUM",
                    status="PENDING",
                    created_at=datetime.datetime.utcnow()
                ),
                Recommendation(
                    branch_id="BR002",
                    service_category="Withdrawal",
                    recommendation_type="BOTTLENECK_ALERT",
                    recommendation_text="Direct cash withdrawals below Rs 20,000 to the 24/7 ATM kiosk.",
                    explanation="Withdrawal queue is elevated at 18 customers. Kiosk redirection reduces counter backlog.",
                    risk_level="MEDIUM",
                    status="PENDING",
                    created_at=datetime.datetime.utcnow()
                )
            ]
            for r in sample_recs:
                db.add(r)

            init_audit = AuditLog(
                user_id=None,
                role="system",
                action="database_seeded",
                resource="database",
                resource_id="all",
                timestamp=datetime.datetime.utcnow(),
                ip_address="127.0.0.1",
                metadata_json='{"status": "initialized", "environment": "hackathon_ready"}'
            )
            db.add(init_audit)
            db.commit()
            print("  ✓ Seeded sample recommendations and initialization audit log.")

        print("\n==================================================")
        print("          DATABASE SEEDING COMPLETED!             ")
        print("==================================================")
        print("Demo Credentials:")
        print("  Regional Ops:  regional@bank.com            / BankDemo#2026")
        print("  Manager HYD:   manager_hyd@bank.com         / BankDemo#2026")
        print("  Manager KUK:   manager_kukatpally@bank.com  / BankDemo#2026")
        print("  Employee HYD:  teller1_hyd@bank.com         / BankDemo#2026")
        print("==================================================")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
