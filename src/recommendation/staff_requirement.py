import math
from typing import Dict, Any
from src.utils.config import SERVICE_DURATION_DEFAULTS


def calculate_required_staff(
    expected_customers: int,
    service_category: str,
    operating_duration_hours: float = 2.0,
    employees_available: int = 3,
    branch_id: str = "BR001",
    time_window: str = "11:00 AM - 1:00 PM",
    efficiency_factor: float = 0.85,
    safety_buffer: float = 0.15,
    target_wait_minutes: float = 10.0
) -> Dict[str, Any]:
    """Calculates required staffing for expected customer load considering service durations, efficiency, and safety buffers."""

    min_dur, max_dur = SERVICE_DURATION_DEFAULTS.get(service_category, (5.0, 15.0))
    avg_service_time = (min_dur + max_dur) / 2.0

    # Total workload in minutes
    total_workload_minutes = expected_customers * avg_service_time

    # Work capacity of one staff member in the given time window
    effective_working_minutes = (operating_duration_hours * 60.0) * efficiency_factor

    # Raw employees required
    raw_staff = total_workload_minutes / max(1.0, effective_working_minutes)

    # Apply safety buffer to handle peak arrival clustering
    buffered_staff = raw_staff * (1.0 + safety_buffer)
    employees_required = max(1, math.ceil(buffered_staff))

    staff_gap = max(0, employees_required - employees_available)

    explanation = (
        f"For expected volume of {expected_customers} customers requesting {service_category} during {time_window}, "
        f"with average service time of {avg_service_time:.1f} minutes, {employees_required} employees are required. "
        f"Currently {employees_available} employees are available (Staff shortage: {staff_gap})."
    )

    return {
        "branch_id": branch_id,
        "service_category": service_category,
        "time_window": time_window,
        "expected_customers": expected_customers,
        "employees_available": employees_available,
        "employees_required": employees_required,
        "staff_gap": staff_gap,
        "average_service_time_min": avg_service_time,
        "explanation": explanation
    }


if __name__ == "__main__":
    result = calculate_required_staff(
        expected_customers=200,
        service_category="Loans - Payment and Sanctioning",
        operating_duration_hours=2.0,
        employees_available=3,
        branch_id="BR002"
    )
    print(result)
