import pandas as pd
import numpy as np
from typing import Dict, Any, List

from src.utils.config import SERVICE_DURATION_DEFAULTS


class BottleneckDetector:
    """Detects service-level bottlenecks using explainable rule logic and ML prediction features."""

    def __init__(self):
        # Service-specific queue thresholds
        self.queue_thresholds = {
            "Loans - Payment and Sanctioning": 5,
            "Locker Issuing": 4,
            "Account Opening": 6,
            "Insurance": 6,
            "KYC Related": 8,
            "Deposit": 12,
            "Withdrawal": 15,
            "Money Transfer": 10,
            "Cheque Withdrawal": 10,
            "Credit Card": 8,
            "Debit Card": 8,
            "Aadhaar Linking": 8,
            "PAN Linking": 8,
            "Other": 8
        }

    def detect_bottleneck(
        self,
        branch_id: str,
        service_category: str,
        queue_length: int,
        predicted_wait_minutes: float,
        staff_available: int,
        staff_required: int,
        arrival_rate: float = 0.0,
        employee_utilization: float = 0.0
    ) -> Dict[str, Any]:
        """Evaluates operational metrics and returns structured bottleneck risk level with plain-language explanation."""

        reasons = []
        risk_score = 0

        # Thresholds
        q_thresh = self.queue_thresholds.get(service_category, 8)
        min_dur, max_dur = SERVICE_DURATION_DEFAULTS.get(service_category, (5.0, 15.0))
        avg_service_min = (min_dur + max_dur) / 2.0

        # Calculate processing capacity per hour per staff member
        hourly_capacity_per_staff = 60.0 / max(1.0, avg_service_min)
        total_hourly_capacity = staff_available * hourly_capacity_per_staff

        # 1. Queue Length check
        if queue_length > q_thresh * 2:
            risk_score += 3
            reasons.append(f"Queue length of {queue_length} severely exceeds threshold of {q_thresh}.")
        elif queue_length > q_thresh:
            risk_score += 2
            reasons.append(f"Queue length of {queue_length} exceeds service threshold of {q_thresh}.")

        # 2. Predicted Waiting Time check
        if predicted_wait_minutes >= 30.0:
            risk_score += 3
            reasons.append(f"Expected wait time ({predicted_wait_minutes:.1f} mins) is critically high (>30 mins).")
        elif predicted_wait_minutes >= 18.0:
            risk_score += 2
            reasons.append(f"Expected wait time ({predicted_wait_minutes:.1f} mins) exceeds 18 minutes baseline.")

        # 3. Staffing Deficit check
        if staff_available < staff_required:
            deficit = staff_required - staff_available
            risk_score += 2
            reasons.append(f"Staff shortage: {staff_available} active employees vs {staff_required} required (Shortfall of {deficit}).")

        # 4. Utilization check
        if employee_utilization > 0.85:
            risk_score += 2
            reasons.append(f"Employee utilization is very high at {employee_utilization*100:.0f}%.")

        # 5. Arrival Rate vs Capacity
        if arrival_rate > total_hourly_capacity and total_hourly_capacity > 0:
            risk_score += 2
            reasons.append(f"Arrival rate ({arrival_rate:.1f} cust/hr) exceeds branch capacity ({total_hourly_capacity:.1f} cust/hr).")

        # Map score to Risk Level
        if risk_score >= 6:
            risk_level = "CRITICAL"
        elif risk_score >= 4:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            reasons.append("Operations are running smoothly within optimal wait and queue parameters.")

        # Plain language explanation synthesis
        explanation = f"{service_category} services at branch {branch_id} are at {risk_level} risk. " + " ".join(reasons)

        return {
            "branch_id": branch_id,
            "service_category": service_category,
            "risk_level": risk_level,
            "queue_length": queue_length,
            "predicted_wait_minutes": round(predicted_wait_minutes, 1),
            "staff_available": staff_available,
            "staff_required": staff_required,
            "reason": explanation
        }


def analyze_bottlenecks(df_current_state: pd.DataFrame) -> List[Dict[str, Any]]:
    detector = BottleneckDetector()
    results = []
    for _, row in df_current_state.iterrows():
        res = detector.detect_bottleneck(
            branch_id=row["branch_id"],
            service_category=row["service_category"],
            queue_length=int(row.get("queue_length", 0)),
            predicted_wait_minutes=float(row.get("predicted_wait_minutes", 0.0)),
            staff_available=int(row.get("staff_available", 1)),
            staff_required=int(row.get("staff_required", 1)),
            arrival_rate=float(row.get("arrival_rate", 0.0)),
            employee_utilization=float(row.get("employee_utilization", 0.0))
        )
        results.append(res)
    return results


if __name__ == "__main__":
    detector = BottleneckDetector()
    sample = detector.detect_bottleneck(
        branch_id="BR002",
        service_category="Loans - Payment and Sanctioning",
        queue_length=12,
        predicted_wait_minutes=35.5,
        staff_available=2,
        staff_required=5,
        arrival_rate=15.0,
        employee_utilization=0.92
    )
    print(sample)
