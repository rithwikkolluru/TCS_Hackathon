import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURES_DATA_DIR = DATA_DIR / "features"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"

# Ensure directories exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FEATURES_DATA_DIR, MODELS_DIR, REPORTS_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Service Categories (Strictly enforced 14 categories)
SERVICE_CATEGORIES = [
    "Loans - Payment and Sanctioning",
    "Insurance",
    "Deposit",
    "Withdrawal",
    "Account Opening",
    "Credit Card",
    "Debit Card",
    "Locker Issuing",
    "Cheque Withdrawal",
    "KYC Related",
    "Money Transfer",
    "Aadhaar Linking",
    "PAN Linking",
    "Other"
]

# Service Category Average Duration Metadata (in minutes)
SERVICE_DURATION_DEFAULTS = {
    "Withdrawal": (2.0, 5.0),
    "Cheque Withdrawal": (3.0, 6.0),
    "Money Transfer": (3.0, 7.0),
    "Deposit": (4.0, 8.0),
    "Credit Card": (5.0, 10.0),
    "Debit Card": (5.0, 10.0),
    "Aadhaar Linking": (6.0, 12.0),
    "PAN Linking": (6.0, 12.0),
    "KYC Related": (8.0, 15.0),
    "Account Opening": (15.0, 25.0),
    "Insurance": (15.0, 30.0),
    "Locker Issuing": (20.0, 35.0),
    "Loans - Payment and Sanctioning": (25.0, 45.0),
    "Other": (5.0, 15.0)
}

# Branch Metadata (Indian Banking Context)
BRANCHES = [
    {
        "branch_id": "BR001",
        "branch_name": "Hyderabad Central",
        "city": "Hyderabad",
        "tier": "Metro",
        "base_footfall_multiplier": 1.4,
        "total_counters": 12,
        "base_staff_count": 15
    },
    {
        "branch_id": "BR002",
        "branch_name": "Hyderabad Kukatpally",
        "city": "Hyderabad",
        "tier": "Metro",
        "base_footfall_multiplier": 1.6,
        "total_counters": 14,
        "base_staff_count": 18
    },
    {
        "branch_id": "BR003",
        "branch_name": "Hyderabad Secunderabad",
        "city": "Hyderabad",
        "tier": "Metro",
        "base_footfall_multiplier": 1.3,
        "total_counters": 10,
        "base_staff_count": 13
    },
    {
        "branch_id": "BR004",
        "branch_name": "Warangal Main",
        "city": "Warangal",
        "tier": "Tier-2",
        "base_footfall_multiplier": 1.0,
        "total_counters": 8,
        "base_staff_count": 10
    },
    {
        "branch_id": "BR005",
        "branch_name": "Vijayawada Main",
        "city": "Vijayawada",
        "tier": "Tier-2",
        "base_footfall_multiplier": 1.2,
        "total_counters": 10,
        "base_staff_count": 12
    },
    {
        "branch_id": "BR006",
        "branch_name": "Karimnagar Main",
        "city": "Karimnagar",
        "tier": "Tier-3",
        "base_footfall_multiplier": 0.8,
        "total_counters": 6,
        "base_staff_count": 8
    },
    {
        "branch_id": "BR007",
        "branch_name": "Visakhapatnam Central",
        "city": "Visakhapatnam",
        "tier": "Tier-2",
        "base_footfall_multiplier": 1.25,
        "total_counters": 11,
        "base_staff_count": 14
    },
    {
        "branch_id": "BR008",
        "branch_name": "Tirupati Main",
        "city": "Tirupati",
        "tier": "Tier-2",
        "base_footfall_multiplier": 1.1,
        "total_counters": 8,
        "base_staff_count": 10
    }
]

CUSTOMER_TYPES = ["Regular", "HNI", "Senior Citizen", "Corporate"]
STAFF_ROLES = [
    "Manager",
    "Loan Officer",
    "Teller",
    "Insurance Officer",
    "KYC Officer",
    "Account Officer",
    "General Employee"
]
