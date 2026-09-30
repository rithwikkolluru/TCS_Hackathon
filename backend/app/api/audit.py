from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, AuditLog
from backend.app.db.schemas import AuditLogOut, ResponseEnvelope
from backend.app.core.dependencies import require_manager_role

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("", response_model=ResponseEnvelope[List[AuditLogOut]])
@router.get("/logs", response_model=ResponseEnvelope[List[AuditLogOut]])
def get_audit_logs(
    action: Optional[str] = Query(None, description="Action filter"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_manager_role),
    db: Session = Depends(get_db)
):
    """Retrieves immutable security and compliance audit logs."""
    query = db.query(AuditLog)

    if current_user.role == "manager":
        # Managers view events for their branch or actions they performed
        query = query.filter((AuditLog.resource_id == current_user.branch_id) | (AuditLog.user_id == current_user.id))

    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    data = [AuditLogOut.from_orm(l) for l in logs]

    return ResponseEnvelope[List[AuditLogOut]](
        success=True,
        data=data,
        explanation=f"Retrieved {len(data)} audit log events."
    )
