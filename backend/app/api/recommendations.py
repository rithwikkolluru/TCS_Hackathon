import datetime
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, Recommendation, RecommendationAction
from backend.app.db.schemas import (
    RecommendationOut, RecommendationGenerateRequest,
    RecommendationActionRequest, DigitalRedirectionResponse,
    ResponseEnvelope
)
from backend.app.core.dependencies import get_current_user, require_manager_role
from backend.app.core.permissions import verify_branch_access
from backend.app.services.ml_service import ml_service
from backend.app.services.audit_service import record_audit

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=ResponseEnvelope[List[RecommendationOut]])
def list_recommendations(
    branch_id: Optional[str] = Query(None, description="Branch ID filter"),
    status_filter: Optional[str] = Query(None, description="Status filter: PENDING, ACCEPTED, REJECTED"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists AI recommendations for a branch."""
    target_branch = branch_id or current_user.branch_id
    verify_branch_access(current_user, target_branch)

    query = db.query(Recommendation)
    if target_branch:
        query = query.filter(Recommendation.branch_id == target_branch)
    if status_filter:
        query = query.filter(Recommendation.status == status_filter.upper())

    recs = query.order_by(Recommendation.created_at.desc()).all()
    data = [RecommendationOut.from_orm(r) for r in recs]

    return ResponseEnvelope[List[RecommendationOut]](
        success=True,
        data=data,
        explanation=f"Retrieved {len(data)} recommendations."
    )


@router.post("/generate", response_model=ResponseEnvelope[List[RecommendationOut]])
def generate_recommendations(
    req: RecommendationGenerateRequest,
    request: Request,
    current_user: User = Depends(require_manager_role),
    db: Session = Depends(get_db)
):
    """Evaluates branch load & ML predictions to generate actionable manager recommendations."""
    target_branch = req.branch_id or current_user.branch_id or "BR001"
    verify_branch_access(current_user, target_branch)

    # 1. Evaluate bottlenecks
    bottlenecks = ml_service.get_bottlenecks_for_branch(target_branch)
    created_recs = []

    for b in bottlenecks:
        cat = b["service_category"]
        risk = b["risk_level"]

        if risk in ["HIGH", "CRITICAL"]:
            # A. Staffing Recommendation
            staff_req = b["staff_required"]
            staff_avail = b["staff_available"]
            staff_gap = max(1, staff_req - staff_avail)

            rec_staff = Recommendation(
                branch_id=target_branch,
                service_category=cat,
                recommendation_type="STAFFING",
                prediction_data=json.dumps(b),
                recommendation_text=f"Deploy {staff_gap} additional employee(s) to {cat} counters.",
                explanation=(
                    f"{cat} is currently operating at {risk} risk. "
                    f"Queue length is {b['queue_length']} and predicted wait is {b['predicted_wait_minutes']:.1f} minutes. "
                    f"Adding {staff_gap} staff member(s) will reduce expected wait times below baseline."
                ),
                risk_level=risk,
                status="PENDING",
                created_at=datetime.datetime.utcnow()
            )
            db.add(rec_staff)
            created_recs.append(rec_staff)

            # B. Digital Redirection Recommendation if service is eligible
            redir = ml_service.get_digital_redirection(cat)
            if redir["digital_available"] and redir["confidence"] >= 0.7:
                rec_redir = Recommendation(
                    branch_id=target_branch,
                    service_category=cat,
                    recommendation_type="DIGITAL_REDIRECTION",
                    prediction_data=json.dumps(redir),
                    recommendation_text=f"Nudge walk-ins for {cat} to {redir['digital_channel']}.",
                    explanation=redir["recommendation"],
                    risk_level="MEDIUM",
                    status="PENDING",
                    created_at=datetime.datetime.utcnow()
                )
                db.add(rec_redir)
                created_recs.append(rec_redir)

    # C. Appointment Nudge Recommendation
    rec_nudge = Recommendation(
        branch_id=target_branch,
        service_category="Loans - Payment and Sanctioning",
        recommendation_type="APPOINTMENT_NUDGE",
        prediction_data=json.dumps({"target_hour": 11, "expected_spike": 40}),
        recommendation_text="Enable digital appointment booking slots for tomorrow 11:00 AM - 1:00 PM.",
        explanation="When branch traffic is expected to be high, recommend customers use available appointment slots to smooth arrival variance.",
        risk_level="MEDIUM",
        status="PENDING",
        created_at=datetime.datetime.utcnow()
    )
    db.add(rec_nudge)
    created_recs.append(rec_nudge)

    db.commit()
    for r in created_recs:
        db.refresh(r)

    record_audit(
        db=db,
        action="recommendations_generated",
        user_id=current_user.id,
        role=current_user.role,
        resource="recommendations",
        resource_id=target_branch,
        ip_address=request.client.host if request.client else None,
        metadata={"branch_id": target_branch, "count": len(created_recs)}
    )

    data = [RecommendationOut.from_orm(r) for r in created_recs]
    return ResponseEnvelope[List[RecommendationOut]](
        success=True,
        data=data,
        explanation=f"Generated {len(data)} AI recommendations for branch {target_branch} based on live load and ML predictions."
    )


@router.post("/{recommendation_id}/accept", response_model=ResponseEnvelope[RecommendationOut])
def accept_recommendation(
    recommendation_id: int,
    action_req: RecommendationActionRequest,
    request: Request,
    current_user: User = Depends(require_manager_role),
    db: Session = Depends(get_db)
):
    """Manager approves and adopts the AI recommendation."""
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")

    verify_branch_access(current_user, rec.branch_id)

    rec.status = "ACCEPTED"

    action = RecommendationAction(
        recommendation_id=rec.id,
        user_id=current_user.id,
        action="ACCEPT",
        timestamp=datetime.datetime.utcnow(),
        reason=action_req.reason or "Manager accepted AI recommendation for operational load leveling.",
        actual_wait_after_action=action_req.actual_wait_after_action or 12.0,
        actual_queue_after_action=action_req.actual_queue_after_action or 4,
        impact="POSITIVE"
    )
    db.add(action)
    db.commit()
    db.refresh(rec)

    record_audit(
        db=db,
        action="recommendation_accepted",
        user_id=current_user.id,
        role=current_user.role,
        resource="recommendations",
        resource_id=str(rec.id),
        ip_address=request.client.host if request.client else None,
        metadata={"recommendation_id": rec.id, "type": rec.recommendation_type, "branch_id": rec.branch_id}
    )

    return ResponseEnvelope[RecommendationOut](
        success=True,
        data=RecommendationOut.from_orm(rec),
        explanation=f"Recommendation #{rec.id} ({rec.recommendation_type}) accepted by Manager."
    )


@router.post("/{recommendation_id}/reject", response_model=ResponseEnvelope[RecommendationOut])
def reject_recommendation(
    recommendation_id: int,
    action_req: RecommendationActionRequest,
    request: Request,
    current_user: User = Depends(require_manager_role),
    db: Session = Depends(get_db)
):
    """Manager declines the AI recommendation with justification."""
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")

    verify_branch_access(current_user, rec.branch_id)

    rec.status = "REJECTED"

    action = RecommendationAction(
        recommendation_id=rec.id,
        user_id=current_user.id,
        action="REJECT",
        timestamp=datetime.datetime.utcnow(),
        reason=action_req.reason or "Branch capacity constraints or counter unavailability.",
        actual_wait_after_action=action_req.actual_wait_after_action or 25.0,
        actual_queue_after_action=action_req.actual_queue_after_action or 15,
        impact="NEUTRAL"
    )
    db.add(action)
    db.commit()
    db.refresh(rec)

    record_audit(
        db=db,
        action="recommendation_rejected",
        user_id=current_user.id,
        role=current_user.role,
        resource="recommendations",
        resource_id=str(rec.id),
        ip_address=request.client.host if request.client else None,
        metadata={"recommendation_id": rec.id, "reason": action_req.reason}
    )

    return ResponseEnvelope[RecommendationOut](
        success=True,
        data=RecommendationOut.from_orm(rec),
        explanation=f"Recommendation #{rec.id} rejected by Manager."
    )


@router.post("/{recommendation_id}/modify", response_model=ResponseEnvelope[RecommendationOut])
def modify_recommendation(
    recommendation_id: int,
    action_req: RecommendationActionRequest,
    request: Request,
    current_user: User = Depends(require_manager_role),
    db: Session = Depends(get_db)
):
    """Manager adopts a modified version of the AI recommendation."""
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")

    verify_branch_access(current_user, rec.branch_id)

    rec.status = "MODIFIED"

    action = RecommendationAction(
        recommendation_id=rec.id,
        user_id=current_user.id,
        action="MODIFY",
        timestamp=datetime.datetime.utcnow(),
        reason=action_req.reason or "Manager adjusted staff allocation buffer.",
        actual_wait_after_action=action_req.actual_wait_after_action or 15.0,
        actual_queue_after_action=action_req.actual_queue_after_action or 6,
        impact="POSITIVE"
    )
    db.add(action)
    db.commit()
    db.refresh(rec)

    record_audit(
        db=db,
        action="recommendation_modified",
        user_id=current_user.id,
        role=current_user.role,
        resource="recommendations",
        resource_id=str(rec.id),
        ip_address=request.client.host if request.client else None
    )

    return ResponseEnvelope[RecommendationOut](
        success=True,
        data=RecommendationOut.from_orm(rec),
        explanation=f"Recommendation #{rec.id} marked as MODIFIED and adopted."
    )


@router.get("/digital-redirection", response_model=ResponseEnvelope[DigitalRedirectionResponse])
def get_digital_redirection(
    service_category: str = Query(..., description="Service category name"),
    customer_type: str = Query("Regular", description="Regular, HNI, Senior Citizen, Corporate"),
    current_user: User = Depends(get_current_user)
):
    """Evaluates whether a branch visit can be redirected to digital banking channels."""
    redir = ml_service.get_digital_redirection(service_category, customer_type)

    resp = DigitalRedirectionResponse(
        service_category=redir["service_category"],
        customer_type=redir["customer_type"],
        digital_available=redir["digital_available"],
        digital_channel=redir["digital_channel"],
        estimated_branch_time_saved_minutes=redir["estimated_branch_time_saved_minutes"],
        confidence=redir["confidence"],
        redirect_suitability=redir["redirect_suitability"],
        instructions=redir["instructions"],
        recommendation=redir["recommendation"]
    )

    return ResponseEnvelope[DigitalRedirectionResponse](
        success=True,
        data=resp,
        explanation=redir["recommendation"]
    )
