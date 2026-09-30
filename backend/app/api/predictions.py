from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.db.schemas import (
    FootfallRequest, FootfallResponse,
    WaitTimeRequest, WaitTimeResponse,
    StaffRequirementRequest, StaffRequirementResponse,
    ResponseEnvelope
)
from backend.app.core.dependencies import get_current_user
from backend.app.core.permissions import verify_branch_access
from backend.app.services.ml_service import ml_service
from backend.app.services.audit_service import record_audit

router = APIRouter(prefix="/predictions", tags=["ML Predictions"])


@router.post("/footfall", response_model=ResponseEnvelope[FootfallResponse])
def predict_footfall(req: FootfallRequest, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Predicts customer arrival volume and category breakdown for a branch time window."""
    verify_branch_access(current_user, req.branch_id)

    prediction = ml_service.get_footfall_prediction(
        branch_id=req.branch_id,
        date_str=req.date,
        start_time=req.start_time,
        end_time=req.end_time
    )

    record_audit(
        db=db,
        action="prediction_footfall",
        user_id=current_user.id,
        role=current_user.role,
        resource="predictions",
        resource_id=req.branch_id,
        ip_address=request.client.host if request.client else None,
        metadata={"branch_id": req.branch_id, "predicted_customers": prediction["predicted_customers"]}
    )

    resp_data = FootfallResponse(
        branch_id=prediction["branch_id"],
        predicted_customers=prediction["predicted_customers"],
        time_slot=prediction["time_slot"],
        date=prediction["date"],
        explanation=prediction["explanation"],
        category_breakdown=prediction["category_breakdown"]
    )

    return ResponseEnvelope[FootfallResponse](
        success=True,
        data=resp_data,
        explanation=prediction["explanation"]
    )


@router.post("/wait-time", response_model=ResponseEnvelope[WaitTimeResponse])
def predict_wait_time(req: WaitTimeRequest, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Predicts expected waiting time and operational risk for a specific service category."""
    verify_branch_access(current_user, req.branch_id)

    prediction = ml_service.get_wait_prediction(
        branch_id=req.branch_id,
        service_category=req.service_category,
        queue_length=req.queue_length,
        staff_available=req.staff_available,
        recent_arrivals=req.recent_arrivals or 10
    )

    record_audit(
        db=db,
        action="prediction_wait_time",
        user_id=current_user.id,
        role=current_user.role,
        resource="predictions",
        resource_id=req.branch_id,
        ip_address=request.client.host if request.client else None,
        metadata={"branch_id": req.branch_id, "service": req.service_category, "wait": prediction["predicted_wait_minutes"]}
    )

    resp_data = WaitTimeResponse(
        branch_id=prediction["branch_id"],
        service_category=prediction["service_category"],
        predicted_wait_minutes=prediction["predicted_wait_minutes"],
        risk_level=prediction["risk_level"],
        queue_length=prediction["queue_length"],
        staff_available=prediction["staff_available"],
        explanation=prediction["explanation"]
    )

    return ResponseEnvelope[WaitTimeResponse](
        success=True,
        data=resp_data,
        explanation=prediction["explanation"]
    )


@router.post("/staff-requirement", response_model=ResponseEnvelope[StaffRequirementResponse])
def predict_staff_requirement(
    req: StaffRequirementRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Answers how many employees are required for a future time slot to prevent bottlenecks."""
    verify_branch_access(current_user, req.branch_id)

    prediction = ml_service.get_staff_requirement(
        branch_id=req.branch_id,
        date_str=req.date,
        start_time=req.start_time or "11:00",
        end_time=req.end_time or "13:00",
        expected_customers=req.expected_customers,
        service_category=req.service_category
    )

    record_audit(
        db=db,
        action="prediction_staff_requirement",
        user_id=current_user.id,
        role=current_user.role,
        resource="predictions",
        resource_id=req.branch_id,
        ip_address=request.client.host if request.client else None,
        metadata={"branch_id": req.branch_id, "staff_required": prediction["staff_required"]}
    )

    resp_data = StaffRequirementResponse(
        branch_id=prediction["branch_id"],
        time_window=prediction["time_window"],
        predicted_customers=prediction["predicted_customers"],
        staff_available=prediction["staff_available"],
        staff_required=prediction["staff_required"],
        additional_staff_required=prediction["additional_staff_required"],
        service_breakdown=prediction.get("service_breakdown"),
        explanation=prediction["explanation"]
    )

    return ResponseEnvelope[StaffRequirementResponse](
        success=True,
        data=resp_data,
        explanation=prediction["explanation"]
    )
