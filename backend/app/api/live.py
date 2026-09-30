import datetime
import random
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, LiveEvent
from backend.app.db.schemas import LiveEventCreate, LiveEventOut, ResponseEnvelope
from backend.app.core.dependencies import get_current_user
from backend.app.core.permissions import verify_branch_access
from backend.app.services.live_service import live_service
from backend.app.services.audit_service import record_audit
from src.utils.config import SERVICE_CATEGORIES

router = APIRouter(prefix="/live", tags=["Real-time Live Events"])


@router.post("/events", response_model=ResponseEnvelope[Dict[str, Any]])
async def ingest_live_event(
    event_req: LiveEventCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingests a real-time event from branch counter kiosk or event simulator."""
    verify_branch_access(current_user, event_req.branch_id)

    event_dict = event_req.dict()
    result = await live_service.ingest_event(event_dict, db)

    return ResponseEnvelope[Dict[str, Any]](
        success=True,
        data=result,
        explanation=f"Processed {event_req.event_type} for {event_req.service_category} at branch {event_req.branch_id}. Queue: {result['queue_length']}."
    )


@router.get("/events", response_model=ResponseEnvelope[List[LiveEventOut]])
def get_recent_live_events(
    branch_id: Optional[str] = Query(None, description="Branch ID"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves recent live events recorded at the branch."""
    target_branch = branch_id or current_user.branch_id
    verify_branch_access(current_user, target_branch)

    query = db.query(LiveEvent)
    if target_branch:
        query = query.filter(LiveEvent.branch_id == target_branch)

    events = query.order_by(LiveEvent.timestamp.desc()).limit(limit).all()
    data = [LiveEventOut.from_orm(e) for e in events]

    return ResponseEnvelope[List[LiveEventOut]](
        success=True,
        data=data,
        explanation=f"Retrieved {len(data)} recent live events."
    )


@router.post("/simulate-surge", response_model=ResponseEnvelope[Dict[str, Any]])
async def trigger_surge_simulation(
    branch_id: Optional[str] = Query(None, description="Branch ID to surge"),
    service_category: Optional[str] = Query(None, description="Service category to surge"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers an instantaneous traffic surge (30-50 queue spike) generating HIGH/CRITICAL alert broadcast."""
    target_branch = branch_id or current_user.branch_id or "BR001"
    verify_branch_access(current_user, target_branch)

    target_service = service_category or "Withdrawal"

    # Surge payload
    surge_queue = random.randint(35, 50)
    surge_staff = random.randint(1, 2)  # severely depleted staff

    surge_event = {
        "event_id": f"SURGE-{int(datetime.datetime.utcnow().timestamp())}",
        "branch_id": target_branch,
        "event_type": "CUSTOMER_ARRIVAL",
        "service_category": target_service,
        "queue_length": surge_queue,
        "staff_available": surge_staff
    }

    result = await live_service.ingest_event(surge_event, db)

    record_audit(
        db=db,
        action="surge_triggered",
        user_id=current_user.id,
        role=current_user.role,
        resource="live",
        resource_id=target_branch,
        metadata={"queue": surge_queue, "service": target_service}
    )

    return ResponseEnvelope[Dict[str, Any]](
        success=True,
        data=result,
        explanation=(
            f"SURGE EVENT TRIGGERED for {target_service} at branch {target_branch}. "
            f"Queue spiked to {surge_queue} with only {surge_staff} staff available. "
            f"Risk elevated to {result['prediction']['bottleneck_risk']} with live WebSocket broadcast."
        )
    )
