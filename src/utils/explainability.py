from typing import Dict, Any, List


class ExplainabilityEngine:
    """Generates human-readable, feature-impact explanations for ML predictions and recommendations."""

    def __init__(self):
        pass

    def explain_footfall(
        self,
        predicted_count: float,
        branch_id: str,
        hour: int,
        day_of_week: str,
        is_month_end: bool = False,
        is_salary_day: bool = False,
        appointment_count: int = 0,
        historical_arrivals: float = 0.0
    ) -> str:
        """Generates plain-language explanation for footfall predictions."""

        factors = []
        if is_month_end:
            factors.append("it is near month-end when transaction volumes spike")
        if is_salary_day:
            factors.append("it falls during the salary/pension payment period (1st-5th of month)")
        if day_of_week in ["Monday", "Friday"]:
            factors.append(f"{day_of_week}s historically receive higher walk-in traffic")
        if hour in [10, 11]:
            factors.append("10:00 AM - 11:30 AM is the morning peak operating window")
        elif hour in [14, 15]:
            factors.append("afternoon hours experience steady post-lunch customer visits")

        if appointment_count > 5:
            factors.append(f"appointment booking volume is elevated ({appointment_count} scheduled)")

        if not factors:
            factors.append("historical baseline traffic patterns for this time slot")

        explanation = (
            f"Expected footfall is estimated at {int(round(predicted_count))} customers for branch {branch_id} at {hour}:00 "
            f"primarily because " + ", ".join(factors) + "."
        )
        return explanation

    def explain_wait_time(
        self,
        predicted_wait: float,
        service_category: str,
        queue_length: int,
        staff_available: int,
        appointment_status: str = "Walk-in"
    ) -> str:
        """Generates plain-language explanation for wait time predictions."""

        factors = []
        if queue_length > 8:
            factors.append(f"queue length at arrival is high ({queue_length} waiting customers)")
        elif queue_length > 0:
            factors.append(f"there are {queue_length} customers currently queued ahead")
        else:
            factors.append("counters are currently clear with zero queue")

        if staff_available <= 2:
            factors.append(f"staff availability is limited ({staff_available} active counters)")
        else:
            factors.append(f"{staff_available} staff members are actively serving counters")

        if appointment_status == "Booked":
            factors.append("priority appointment status reduces waiting duration")

        explanation = (
            f"Predicted waiting time is {predicted_wait:.1f} minutes for {service_category} because "
            + " and ".join(factors) + "."
        )
        return explanation

    def explain_staff_recommendation(
        self,
        expected_customers: int,
        service_category: str,
        staff_available: int,
        staff_required: int,
        time_window: str
    ) -> str:
        """Generates explanation for staff requirement recommendations."""

        staff_gap = max(0, staff_required - staff_available)
        if staff_gap > 0:
            status_text = f"an additional {staff_gap} employee(s) should be deployed to prevent severe bottlenecking"
        else:
            status_text = "current staffing is sufficient to maintain optimal queue flow"

        explanation = (
            f"{staff_required} employees are recommended for {service_category} during {time_window} because approximately "
            f"{expected_customers} customers are expected and {status_text}."
        )
        return explanation


def generate_explanation(explanation_type: str, **kwargs) -> str:
    engine = ExplainabilityEngine()
    if explanation_type == "footfall":
        return engine.explain_footfall(**kwargs)
    elif explanation_type == "wait_time":
        return engine.explain_wait_time(**kwargs)
    elif explanation_type == "staff":
        return engine.explain_staff_recommendation(**kwargs)
    else:
        return "Explanation available upon prediction input."


if __name__ == "__main__":
    engine = ExplainabilityEngine()
    print(engine.explain_footfall(
        predicted_count=45, branch_id="BR002", hour=11, day_of_week="Monday",
        is_month_end=True, appointment_count=8
    ))
    print(engine.explain_wait_time(
        predicted_wait=28.5, service_category="Loans - Payment and Sanctioning",
        queue_length=12, staff_available=2
    ))
