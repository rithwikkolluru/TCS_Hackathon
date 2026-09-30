"""
Hybrid AI API — Privacy-First Endpoints
========================================
All sensitive data is processed locally via Ollama.
Only anonymized summaries are sent to online Gemini.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db import models as db_models
from backend.app.core.dependencies import get_current_user
from backend.app.services.hybrid_ai_service import hybrid_ai

router = APIRouter(prefix="/hybrid-ai", tags=["Hybrid AI"])
logger = logging.getLogger("hybrid_ai_api")


# ── Request/Response Schemas ──────────────────────────────────────────────────
class BranchAnalysisRequest(BaseModel):
    branch_id: int
    include_feedback: bool = True
    include_queue: bool = True
    max_customers: int = 100

class QuickRiskRequest(BaseModel):
    branch_id: int

class FeedbackSentimentRequest(BaseModel):
    branch_id: int
    limit: int = 50

class SurgeAlertRequest(BaseModel):
    branch_id: int
    current_queue_length: int
    service_category: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health")
async def hybrid_ai_health():
    """Check status of local Ollama and online Gemini models."""
    return await hybrid_ai.health_check()


@router.post("/branch/full-analysis")
async def full_branch_analysis(
    req: BranchAnalysisRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Full hybrid AI pipeline for a branch:
    - Stage 1 (Local Ollama): Processes all sensitive data privately
    - Stage 2 (Online Gemini): Generates final insights from anonymized data

    Role: manager, admin
    """
    if current_user.role not in ("manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers and admins only")

    # Fetch branch
    branch = db.query(db_models.Branch).filter(db_models.Branch.id == req.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Fetch customer visit records (sensitive — processed locally only)
    visits = db.query(db_models.CustomerVisit).filter(
        db_models.CustomerVisit.branch_id == req.branch_id
    ).limit(req.max_customers).all()

    customer_records = [
        {
            "service_category": v.service_category,
            "wait_time_minutes": v.wait_time_minutes,
            "arrival_hour": v.arrival_time.hour if v.arrival_time else None,
            "status": v.status
        }
        for v in visits
    ]

    # Fetch feedback (sensitive — processed locally only)
    feedback_records = []
    if req.include_feedback:
        feedbacks = db.query(db_models.CustomerFeedback).filter(
            db_models.CustomerFeedback.branch_id == req.branch_id
        ).limit(50).all()
        feedback_records = [{"feedback_text": f.feedback_text, "rating": f.rating} for f in feedbacks]

    # Build branch data (strip PII)
    branch_data = {
        "branch_id": branch.id,
        "branch_code": branch.branch_code,
        "city": branch.city,
        "active_counters": branch.active_counters,
        "total_staff": branch.total_staff,
        "peak_hours": branch.peak_hours,
    }

    # Queue data
    queue_data = {
        "total_in_queue": len([v for v in visits if v.status == "waiting"]),
        "by_service": {},
        "avg_wait": sum(v.wait_time_minutes or 0 for v in visits) / max(len(visits), 1)
    }
    for v in visits:
        svc = v.service_category or "Unknown"
        queue_data["by_service"][svc] = queue_data["by_service"].get(svc, 0) + 1

    # Run full pipeline
    try:
        result = await hybrid_ai.full_branch_analysis(
            branch_data=branch_data,
            customer_records=customer_records,
            feedback_records=feedback_records,
            queue_data=queue_data,
            branch_name=f"{branch.city} Branch"
        )
        return result
    except Exception as e:
        logger.error(f"[HybridAI] Full analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid AI pipeline error: {str(e)}")


@router.post("/branch/quick-risk")
async def quick_branch_risk(
    req: QuickRiskRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick local-only risk scan (Ollama only, instant response).
    No online model call — fastest possible analysis.
    """
    branch = db.query(db_models.Branch).filter(db_models.Branch.id == req.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    visits = db.query(db_models.CustomerVisit).filter(
        db_models.CustomerVisit.branch_id == req.branch_id
    ).limit(50).all()

    branch_data = {
        "branch_code": branch.branch_code,
        "city": branch.city,
        "active_counters": branch.active_counters,
        "total_staff": branch.total_staff,
        "current_queue": len([v for v in visits if v.status == "waiting"]),
        "avg_wait_minutes": sum(v.wait_time_minutes or 0 for v in visits) / max(len(visits), 1)
    }

    try:
        return await hybrid_ai.quick_branch_risk(branch_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/sentiment")
async def analyze_feedback_sentiment(
    req: FeedbackSentimentRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze customer feedback:
    - Local Ollama anonymizes and extracts sentiment
    - Gemini generates strategic CX insights
    """
    feedbacks = db.query(db_models.CustomerFeedback).filter(
        db_models.CustomerFeedback.branch_id == req.branch_id
    ).limit(req.limit).all()

    feedback_list = [{"feedback_text": f.feedback_text, "rating": f.rating} for f in feedbacks]

    try:
        return await hybrid_ai.quick_sentiment(feedback_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/surge/narrative")
async def surge_alert_narrative(
    req: SurgeAlertRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a human-readable surge alert narrative (Gemini).
    Queue metrics are anonymized before sending online.
    """
    branch = db.query(db_models.Branch).filter(db_models.Branch.id == req.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    surge_data = {
        "branch_city": branch.city,
        "current_queue_length": req.current_queue_length,
        "active_counters": branch.active_counters,
        "service_category": req.service_category or "all",
        "congestion_level": "critical" if req.current_queue_length > 30 else "high" if req.current_queue_length > 20 else "medium" if req.current_queue_length > 10 else "low",
        "recommended_staff_increase": max(1, req.current_queue_length // 10)
    }

    try:
        narrative = await hybrid_ai.online.generate_surge_alert_narrative(surge_data)
        return {"branch_id": req.branch_id, "narrative": narrative, "surge_metrics": surge_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
