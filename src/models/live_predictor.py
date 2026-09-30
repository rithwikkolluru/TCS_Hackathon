import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from src.models.wait_time_model import WaitTimeModel
from src.models.footfall_model import FootfallModel
from src.models.bottleneck_detector import BottleneckDetector
from src.recommendation.staff_requirement import calculate_required_staff
from src.recommendation.digital_redirection import get_digital_recommendation
from src.utils.explainability import generate_explanation


class LivePredictor:
    """Unified Live Predictor Service designed for seamless integration by API and WebSocket gateways."""

    def __init__(self):
        self.wait_model = WaitTimeModel()
        self.footfall_model = FootfallModel()
        self.bottleneck_detector = BottleneckDetector()

    def predict_live(
        self,
        branch_id: str,
        service_category: str,
        current_queue: int,
        staff_available: int,
        recent_arrivals: int = 10,
        timestamp: Optional[str] = None,
        customer_type: str = "Regular"
    ) -> Dict[str, Any]:
        """Unified prediction function for live branch load, waiting time, bottleneck risk, and staff requirements."""

        if timestamp:
            dt = pd.to_datetime(timestamp)
        else:
            dt = datetime.datetime.now()

        hour = dt.hour
        day_of_week = dt.strftime("%A")
        day_num = dt.weekday()
        day_of_month = dt.day

        is_weekend = int(day_num in [5, 6])
        is_month_end = int(day_of_month in [28, 29, 30, 31])
        is_salary_day = int(day_of_month in [1, 2, 3, 4, 5])

        # 1. Predict Footfall for current slot
        ff_input = pd.DataFrame([{
            "branch_id": branch_id,
            "service_category": service_category,
            "day_of_week": day_of_week,
            "hour": hour,
            "day_num": day_num,
            "day_of_month": day_of_month,
            "is_weekend": is_weekend,
            "is_month_end": is_month_end,
            "is_salary_day": is_salary_day,
            "appointment_count": 3,
            "employees_available": staff_available,
            "employees_absent": 1,
            "historical_arrivals": float(recent_arrivals),
            "previous_slot_arrivals": float(recent_arrivals * 0.9),
            "previous_day_arrivals": float(recent_arrivals * 1.1),
            "rolling_15min_arrivals": float(recent_arrivals * 0.5),
            "rolling_30min_arrivals": float(recent_arrivals),
            "rolling_60min_arrivals": float(recent_arrivals * 1.8),
            "rolling_wait_time": 12.0,
            "queue_per_employee": float(current_queue / max(1, staff_available))
        }])

        try:
            pred_footfall = float(self.footfall_model.predict(ff_input)[0])
        except Exception:
            pred_footfall = float(recent_arrivals * 1.2)

        # 2. Predict Waiting Time
        wt_input = pd.DataFrame([{
            "branch_id": branch_id,
            "service_category": service_category,
            "day_of_week": day_of_week,
            "queue_length_at_arrival": current_queue,
            "employees_available": staff_available,
            "employees_absent": 1,
            "arrival_rate": round(recent_arrivals / 0.5, 2),  # arrivals per hour
            "service_time_minutes": 10.0,
            "appointment_count": 1,
            "hour": hour,
            "day_num": day_num,
            "day_of_month": day_of_month,
            "is_weekend": is_weekend,
            "is_month_end": is_month_end,
            "is_salary_day": is_salary_day,
            "rolling_15min_arrivals": float(recent_arrivals * 0.5),
            "rolling_30min_arrivals": float(recent_arrivals),
            "rolling_60min_arrivals": float(recent_arrivals * 1.8),
            "historical_wait": 15.0,
            "queue_per_employee": float(current_queue / max(1, staff_available))
        }])

        try:
            pred_wait = float(self.wait_model.predict(wt_input)[0])
        except Exception:
            pred_wait = float((current_queue * 10.0) / max(1, staff_available))

        # 3. Staff Requirement Calculation
        staff_rec = calculate_required_staff(
            expected_customers=int(max(current_queue, round(pred_footfall))),
            service_category=service_category,
            operating_duration_hours=1.0,
            employees_available=staff_available,
            branch_id=branch_id
        )

        # 4. Bottleneck Detection
        bottleneck_info = self.bottleneck_detector.detect_bottleneck(
            branch_id=branch_id,
            service_category=service_category,
            queue_length=current_queue,
            predicted_wait_minutes=pred_wait,
            staff_available=staff_available,
            staff_required=staff_rec["employees_required"],
            arrival_rate=round(recent_arrivals / 0.5, 2)
        )

        # 5. Digital Redirection Option
        digital_info = get_digital_recommendation(service_category, customer_type)

        # 6. Synthesize Plain Language Explanation
        explanation = generate_explanation(
            "wait_time",
            predicted_wait=pred_wait,
            service_category=service_category,
            queue_length=current_queue,
            staff_available=staff_available
        )

        return {
            "branch_id": branch_id,
            "service_category": service_category,
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "current_queue": current_queue,
            "staff_available": staff_available,
            "predicted_wait_minutes": round(pred_wait, 1),
            "predicted_footfall": int(round(pred_footfall)),
            "bottleneck_risk": bottleneck_info["risk_level"],
            "staff_required": staff_rec["employees_required"],
            "staff_gap": staff_rec["staff_gap"],
            "explanation": bottleneck_info["reason"],
            "digital_redirection": digital_info
        }


def predict_live(
    branch_id: str,
    service_category: str,
    current_queue: int,
    staff_available: int,
    recent_arrivals: int = 10,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    predictor = LivePredictor()
    return predictor.predict_live(
        branch_id=branch_id,
        service_category=service_category,
        current_queue=current_queue,
        staff_available=staff_available,
        recent_arrivals=recent_arrivals,
        timestamp=timestamp
    )


if __name__ == "__main__":
    predictor = LivePredictor()
    res = predictor.predict_live(
        branch_id="BR002",
        service_category="Loans - Payment and Sanctioning",
        current_queue=15,
        staff_available=2,
        recent_arrivals=25
    )
    import pprint
    pprint.pprint(res)
