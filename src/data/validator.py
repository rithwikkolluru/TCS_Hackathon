import re
import pandas as pd
from typing import Dict, Tuple, List
from src.utils.config import SERVICE_CATEGORIES, BRANCHES


class DataValidator:
    """Validates raw and processed banking datasets for schema integrity, service categories, and strict PII compliance."""

    PII_PATTERNS = {
        "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        "pan": r"\b[A-Z]{5}\d{4}[A-Z]{1}\b",
        "phone": r"\b[6-9]\d{9}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "account_num": r"\b\d{11,16}\b"
    }

    def __init__(self):
        self.allowed_branches = {b["branch_id"] for b in BRANCHES}
        self.allowed_services = set(SERVICE_CATEGORIES)

    def validate_pii(self, df: pd.DataFrame, df_name: str = "dataset") -> Tuple[bool, List[str]]:
        """Scans all string columns for PII regex patterns."""
        pii_violations = []
        string_cols = df.select_dtypes(include=['object', 'string']).columns

        for col in string_cols:
            for idx, val in df[col].dropna().items():
                val_str = str(val)
                # Skip check on IDs like VIS-..., STF-..., APT-..., FBK-...
                if any(val_str.startswith(prefix) for prefix in ["VIS-", "STF-", "APT-", "FBK-"]):
                    continue

                for pii_type, pattern in self.PII_PATTERNS.items():
                    if re.search(pattern, val_str, re.IGNORECASE):
                        pii_violations.append(f"Potential {pii_type} found in {df_name} col '{col}' at index {idx}: '{val_str}'")

        is_clean = len(pii_violations) == 0
        return is_clean, pii_violations

    def validate_visits(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validates visits dataset structure and values."""
        errors = []
        required_cols = [
            "visit_id", "branch_id", "arrival_timestamp", "date", "day_of_week", "hour",
            "service_category", "customer_type", "appointment_status", "token_number",
            "counter_id", "service_start_timestamp", "service_end_timestamp",
            "waiting_time_minutes", "service_time_minutes", "employees_available",
            "employees_absent", "queue_length_at_arrival", "completed_status"
        ]

        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        if df.empty:
            errors.append("Visits dataset is empty")
            return False, errors

        # Validate Branch IDs
        invalid_branches = set(df["branch_id"].unique()) - self.allowed_branches
        if invalid_branches:
            errors.append(f"Invalid branch IDs found: {invalid_branches}")

        # Validate Service Categories
        invalid_services = set(df["service_category"].unique()) - self.allowed_services
        if invalid_services:
            errors.append(f"Invalid service categories found: {invalid_services}")

        # Validate numeric ranges
        if (df["waiting_time_minutes"] < 0).any():
            errors.append("Negative waiting times detected")
        if (df["service_time_minutes"] <= 0).any():
            errors.append("Non-positive service times detected")

        # PII Check
        clean_pii, pii_errs = self.validate_pii(df, "visits")
        errors.extend(pii_errs)

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_all(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Tuple[bool, List[str]]]:
        """Runs full validation suite on all datasets."""
        results = {}
        if "visits" in datasets:
            results["visits"] = self.validate_visits(datasets["visits"])
        if "customer_feedback" in datasets:
            results["customer_feedback"] = self.validate_pii(datasets["customer_feedback"], "customer_feedback")
        return results
