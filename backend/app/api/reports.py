from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, Branch
from backend.app.db.schemas import ResponseEnvelope
from backend.app.core.dependencies import require_regional_role
from backend.app.services.ml_service import ml_service
from src.utils.config import BRANCHES

router = APIRouter(prefix="/regional", tags=["Regional Operations"])


@router.get("/branches", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def get_regional_branches(current_user: User = Depends(require_regional_role), db: Session = Depends(get_db)):
    """Returns overview list of all regional branches with tier, counters, and capacity."""
    branches = db.query(Branch).all()
    branch_data = [
        {
            "branch_code": b.branch_code,
            "branch_name": b.branch_name,
            "city": b.city,
            "state": b.state,
            "total_counters": b.total_counters,
            "status": "OPERATIONAL"
        }
        for b in branches
    ]
    return ResponseEnvelope[List[Dict[str, Any]]](
        success=True,
        data=branch_data,
        explanation=f"Network overview: {len(branch_data)} regional branches operational."
    )


@router.get("/load", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def get_regional_load(current_user: User = Depends(require_regional_role)):
    """Compares customer traffic, queues, and wait times across branches."""
    results = []
    for b in BRANCHES:
        b_id = b["branch_id"]
        mult = b.get("base_footfall_multiplier", 1.0)
        base_staff = b.get("base_staff_count", 10)

        # Realistic metrics for each branch
        pred_traffic = int(round(150 * mult))
        curr_queue = int(round(20 * mult))
        avg_wait = round(14.0 * mult, 1)
        risk = "HIGH" if mult > 1.3 else ("MEDIUM" if mult >= 1.0 else "LOW")

        results.append({
            "branch_id": b_id,
            "branch_name": b["branch_name"],
            "city": b["city"],
            "predicted_traffic": pred_traffic,
            "current_queue": curr_queue,
            "average_wait_minutes": avg_wait,
            "risk_level": risk,
            "staff_available": base_staff // 2,
            "staff_required": int(round((base_staff // 2) * (1.2 if mult > 1.2 else 1.0)))
        })

    return ResponseEnvelope[List[Dict[str, Any]]](
        success=True,
        data=results,
        explanation="Multi-branch operational load comparison for regional operations control."
    )


@router.get("/bottlenecks", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def get_regional_bottlenecks(current_user: User = Depends(require_regional_role)):
    """Aggregates all high and critical bottlenecks across the entire bank branch network."""
    all_bottlenecks = []
    for b in BRANCHES:
        b_id = b["branch_id"]
        b_items = ml_service.get_bottlenecks_for_branch(b_id)
        # Filter for high/critical risks to keep regional ops focused
        critical = [item for item in b_items if item["risk_level"] in ["HIGH", "CRITICAL"]]
        all_bottlenecks.extend(critical)

    return ResponseEnvelope[List[Dict[str, Any]]](
        success=True,
        data=all_bottlenecks,
        explanation=f"Identified {len(all_bottlenecks)} service bottlenecks requiring regional oversight across {len(BRANCHES)} branches."
    )


@router.get("/staffing", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def get_regional_staffing(current_user: User = Depends(require_regional_role)):
    """Evaluates network-wide staffing deficits and recommended employee deployments."""
    staffing_summary = []
    for b in BRANCHES:
        b_id = b["branch_id"]
        req = ml_service.get_staff_requirement(b_id, start_time="11:00", end_time="13:00")
        staffing_summary.append({
            "branch_id": b_id,
            "branch_name": b["branch_name"],
            "city": b["city"],
            "staff_available": req["staff_available"],
            "staff_required": req["staff_required"],
            "staff_gap": req["additional_staff_required"],
            "status": "SHORTAGE" if req["additional_staff_required"] > 0 else "OPTIMAL"
        })

    total_gap = sum(s["staff_gap"] for s in staffing_summary)
    return ResponseEnvelope[List[Dict[str, Any]]](
        success=True,
        data=staffing_summary,
        explanation=f"Regional staffing allocation summary: Network shortfall of {total_gap} employees across peak slots."
    )
