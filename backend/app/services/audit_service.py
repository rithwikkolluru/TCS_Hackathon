import json
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.db.models import AuditLog
from backend.app.core.sanitizer import sanitize_data

logger = logging.getLogger("audit")


def record_audit(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Records an audit log entry ensuring all metadata is sanitized of PII."""
    sanitized_meta = sanitize_data(metadata) if metadata else None
    meta_json = json.dumps(sanitized_meta) if sanitized_meta else None

    entry = AuditLog(
        user_id=user_id,
        role=role,
        action=action,
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        metadata_json=meta_json
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    logger.info(f"[AUDIT] action={action} user={user_id} role={role} resource={resource}:{resource_id}")
    return entry
