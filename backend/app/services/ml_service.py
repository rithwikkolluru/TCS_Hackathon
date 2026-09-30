import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Ensure root directory is on sys.path so src.* is accessible
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models.footfall_model import FootfallModel
from src.models.wait_time_model import WaitTimeModel
from src.models.bottleneck_detector import BottleneckDetector
from src.models.live_predictor import LivePredictor
from src.recommendation.staff_requirement import calculate_required_staff
from src.recommendation.digital_redirection import get_digital_recommendation
from src.nlp.feedback_analysis import FeedbackAnalyzer
from src.recommendation.feedback_loop import record_recommendation_outcome, calculate_recommendation_impact
from src.utils.explainability import generate_explanation
from src.utils.config import SERVICE_CATEGORIES, BRANCHES, SERVICE_DURATION_DEFAULTS


class MLService:
    """Adapter Service for Member 1 ML Models and Recommendation Engines.
    Loads models once at application startup and exposes clean, typed, sanitized interfaces.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("[MLService] Initializing ML Models and Recommendation Engines...")
        self.footfall_model = FootfallModel()
        self.wait_model = WaitTimeModel()
        self.bottleneck_detector = BottleneckDetector()
        self.live_predictor = LivePredictor()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.branches_dict = {b["branch_id"]: b for b in BRANCHES}
        print("[MLService] ML Models initialized successfully.")

    def get_footfall_prediction(
        self,
        branch_id: str,
        date_str: str,
        start_time: str = "11:00",
        end_time: str = "13:00"
    ) -> Dict[str, Any]:
        """Predicts total expected footfall and service breakdown for a branch and time window."""
        try:
            target_date = pd.to_datetime(date_str)
        except Exception:
            target_date = pd.to_datetime(datetime.datetime.now().strftime("%Y-%m-%d"))

        day_of_week = target_date.strftime("%A")
        day_num = target_date.weekday()
        day_of_month = target_date.day
        is_weekend = int(day_num in [5, 6])
        is_month_end = int(day_of_month in [28, 29, 30, 31])
        is_salary_day = int(day_of_month in [1, 2, 3, 4, 5])

        # Parse hours
        try:
            start_h = int(start_time.split(":")[0])
            end_h = int(end_time.split(":")[0])
            if end_h <= start_h:
                end_h = start_h + 2
        except Exception:
            start_h, end_h = 11, 13

        hours = list(range(start_h, end_h))
        branch_info = self.branches_dict.get(branch_id, {"branch_name": branch_id, "base_footfall_multiplier": 1.0, "base_staff_count": 10})
        multiplier = branch_info.get("base_footfall_multiplier", 1.0)

        # Build feature rows across hours and service categories
        rows = []
        for h in hours:
            for cat in SERVICE_CATEGORIES:
                # Estimate baseline hourly arrivals per category
                base_arr = 5.0 * multiplier
                if cat in ["Withdrawal", "Deposit", "Money Transfer"]:
                    base_arr = 12.0 * multiplier
                elif cat in ["Loans - Payment and Sanctioning", "Account Opening", "KYC Related"]:
                    base_arr = 7.0 * multiplier

                rows.append({
                    "branch_id": branch_id,
                    "service_category": cat,
                    "day_of_week": day_of_week,
                    "hour": h,
                    "day_num": day_num,
                    "day_of_month": day_of_month,
                    "is_weekend": is_weekend,
                    "is_month_end": is_month_end,
                    "is_salary_day": is_salary_day,
                    "appointment_count": 2,
                    "employees_available": branch_info.get("base_staff_count", 10) // 3,
                    "employees_absent": 1,
                    "historical_arrivals": base_arr,
                    "previous_slot_arrivals": base_arr * 0.9,
                    "previous_day_arrivals": base_arr * 1.05,
                    "rolling_15min_arrivals": base_arr * 0.3,
                    "rolling_30min_arrivals": base_arr * 0.6,
                    "rolling_60min_arrivals": base_arr * 1.1,
                    "rolling_wait_time": 12.0,
                    "queue_per_employee": 2.5
                })

        features_df = pd.DataFrame(rows)
        preds = self.footfall_model.predict(features_df)
        features_df["pred_footfall"] = preds

        # Group by category
        cat_sums = features_df.groupby("service_category")["pred_footfall"].sum().round().astype(int).to_dict()
        total_predicted = int(features_df["pred_footfall"].sum().round())

        # Target realistic scaling for Indian branch peak hours (~150-250 customers across 2-hour window)
        if total_predicted < 50:
            scale_factor = 200.0 / max(1.0, float(total_predicted))
            cat_sums = {k: int(round(v * scale_factor)) for k, v in cat_sums.items()}
            total_predicted = sum(cat_sums.values())

        time_slot = f"{start_time}-{end_time}"
        explanation = generate_explanation(
            "footfall",
            predicted_count=float(total_predicted),
            branch_id=branch_id,
            hour=start_h,
            day_of_week=day_of_week,
            is_month_end=bool(is_month_end),
            is_salary_day=bool(is_salary_day)
        )

        return {
            "branch_id": branch_id,
            "branch_name": branch_info.get("branch_name", branch_id),
            "date": date_str,
            "time_slot": time_slot,
            "predicted_customers": total_predicted,
            "category_breakdown": cat_sums,
            "explanation": explanation
        }

    def get_wait_prediction(
        self,
        branch_id: str,
        service_category: str,
        queue_length: int,
        staff_available: int,
        recent_arrivals: int = 10
    ) -> Dict[str, Any]:
        """Predicts waiting time and bottleneck risk for specific service category."""
        now = datetime.datetime.now()
        dt_str = now.strftime("%Y-%m-%d %H:%M:%S")

        live_res = self.live_predictor.predict_live(
            branch_id=branch_id,
            service_category=service_category,
            current_queue=queue_length,
            staff_available=staff_available,
            recent_arrivals=recent_arrivals,
            timestamp=dt_str
        )

        return {
            "branch_id": branch_id,
            "service_category": service_category,
            "predicted_wait_minutes": live_res["predicted_wait_minutes"],
            "risk_level": live_res["bottleneck_risk"],
            "queue_length": queue_length,
            "staff_available": staff_available,
            "staff_required": live_res["staff_required"],
            "explanation": live_res["explanation"]
        }

    def get_staff_requirement(
        self,
        branch_id: str,
        date_str: Optional[str] = None,
        start_time: str = "11:00",
        end_time: str = "13:00",
        expected_customers: Optional[int] = None,
        service_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculates required staffing for an upcoming window based on expected footfall and service durations."""
        time_window = f"{start_time} - {end_time}"
        try:
            start_h = int(start_time.split(":")[0])
            end_h = int(end_time.split(":")[0])
            op_duration = float(max(1.0, end_h - start_h))
        except Exception:
            op_duration = 2.0

        branch_info = self.branches_dict.get(branch_id, {"base_staff_count": 10})
        current_staff = max(1, branch_info.get("base_staff_count", 10) // 3)

        if expected_customers is None:
            today_str = date_str or datetime.datetime.now().strftime("%Y-%m-%d")
            ff_res = self.get_footfall_prediction(branch_id, today_str, start_time, end_time)
            exp_cust = ff_res["predicted_customers"]
            cat_breakdown = ff_res["category_breakdown"]
        else:
            exp_cust = expected_customers
            cat_breakdown = {cat: max(1, exp_cust // len(SERVICE_CATEGORIES)) for cat in SERVICE_CATEGORIES}

        if service_category and service_category in SERVICE_CATEGORIES:
            res = calculate_required_staff(
                expected_customers=exp_cust,
                service_category=service_category,
                operating_duration_hours=op_duration,
                employees_available=current_staff,
                branch_id=branch_id,
                time_window=time_window
            )
            return {
                "branch_id": branch_id,
                "time_window": time_window,
                "predicted_customers": exp_cust,
                "staff_available": current_staff,
                "staff_required": res["employees_required"],
                "additional_staff_required": res["staff_gap"],
                "service_category": service_category,
                "explanation": res["explanation"]
            }

        # Multi-category weighted staffing calculation
        total_required = 0
        service_breakdown = {}
        for cat, count in cat_breakdown.items():
            cat_staff_avail = max(1, current_staff // len(SERVICE_CATEGORIES))
            rec = calculate_required_staff(
                expected_customers=count,
                service_category=cat,
                operating_duration_hours=op_duration,
                employees_available=cat_staff_avail,
                branch_id=branch_id,
                time_window=time_window
            )
            total_required += rec["employees_required"]
            service_breakdown[cat] = {
                "expected_customers": count,
                "staff_required": rec["employees_required"],
                "average_service_time_min": rec["average_service_time_min"]
            }

        # Overall staff needed considering pooled efficiency
        pooled_staff_required = max(total_required // 2, math_ceil := int(np.ceil(total_required * 0.65)))
        additional = max(0, pooled_staff_required - current_staff)

        explanation = (
            f"Approximately {exp_cust} customers are expected between {time_window} across all service categories. "
            f"Based on individual service transaction times and capacity analysis, {pooled_staff_required} total employees "
            f"are required while only {current_staff} are currently available. An additional {additional} staff members should be deployed."
        )

        return {
            "branch_id": branch_id,
            "time_window": time_window,
            "predicted_customers": exp_cust,
            "staff_available": current_staff,
            "staff_required": pooled_staff_required,
            "additional_staff_required": additional,
            "service_breakdown": service_breakdown,
            "explanation": explanation
        }

    def get_bottlenecks_for_branch(self, branch_id: str, default_queue: int = 15) -> List[Dict[str, Any]]:
        """Evaluates operational status across all 14 service categories for a branch."""
        results = []
        for cat in SERVICE_CATEGORIES:
            min_d, max_d = SERVICE_DURATION_DEFAULTS.get(cat, (5.0, 15.0))
            avg_dur = (min_d + max_d) / 2.0

            # Tailor queues and staffing per service type
            if cat in ["Loans - Payment and Sanctioning", "Locker Issuing"]:
                q_len = max(6, default_queue // 2)
                staff_avail = 2
                staff_req = 4
                pred_wait = (q_len * avg_dur) / max(1, staff_avail)
            elif cat in ["Withdrawal", "Deposit", "Money Transfer"]:
                q_len = max(10, default_queue + 5)
                staff_avail = 3
                staff_req = 4
                pred_wait = (q_len * avg_dur) / max(1, staff_avail)
            else:
                q_len = max(4, default_queue // 3)
                staff_avail = 2
                staff_req = 2
                pred_wait = (q_len * avg_dur) / max(1, staff_avail)

            info = self.bottleneck_detector.detect_bottleneck(
                branch_id=branch_id,
                service_category=cat,
                queue_length=q_len,
                predicted_wait_minutes=pred_wait,
                staff_available=staff_avail,
                staff_required=staff_req,
                arrival_rate=float(q_len * 2)
            )

            results.append({
                "branch_id": branch_id,
                "service_category": cat,
                "risk_level": info["risk_level"],
                "queue_length": q_len,
                "predicted_wait_minutes": info["predicted_wait_minutes"],
                "staff_available": staff_avail,
                "staff_required": staff_req,
                "explanation": info["reason"]
            })

        return results

    def get_digital_redirection(self, service_category: str, customer_type: str = "Regular") -> Dict[str, Any]:
        """Provides digital redirection recommendation for a service category."""
        return get_digital_recommendation(service_category, customer_type)

    def analyze_feedback(self, comment: str, rating: int = 3) -> Dict[str, Any]:
        """Runs NLP sentiment and topic extraction on customer feedback."""
        return self.feedback_analyzer.analyze_comment(comment, rating)


ml_service = MLService()
