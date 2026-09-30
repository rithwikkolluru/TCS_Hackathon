import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class WebSocketAlertEvent(BaseModel):
    event: str  # BOTTLENECK_ALERT, STAFFING_RECOMMENDATION, QUEUE_SPIKE, WAIT_TIME_SPIKE, STAFF_SHORTAGE
    branch_id: str
    service_category: Optional[str] = None
    risk_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
