import json
import logging
import asyncio
import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import redis

from backend.app.config import settings
from backend.app.db.models import LiveEvent
from backend.app.services.ml_service import ml_service
from backend.app.websocket.manager import ws_manager

logger = logging.getLogger("live_service")


class LiveService:
    """Processes real-time events, manages branch queues, runs live prediction, and triggers WebSocket alerts."""

    def __init__(self):
        self.redis_client = None
        self._init_redis()
        # In-memory branch state tracker: {branch_id: {service_category: {"queue": int, "staff": int}}}
        self.branch_states: Dict[str, Dict[str, Dict[str, int]]] = {}

    def _init_redis(self):
        try:
            r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
            r.ping()
            self.redis_client = r
            logger.info(f"[LiveService] Connected to Redis Streams at {settings.REDIS_URL}")
        except Exception as e:
            self.redis_client = None
            logger.warning(f"[LiveService] Redis not available ({e}). Using in-memory event bus fallback.")

    def check_redis(self) -> bool:
        if self.redis_client:
            try:
                return bool(self.redis_client.ping())
            except Exception:
                return False
        return False

    def get_state(self, branch_id: str, service_category: str) -> Dict[str, int]:
        if branch_id not in self.branch_states:
            self.branch_states[branch_id] = {}
        if service_category not in self.branch_states[branch_id]:
            self.branch_states[branch_id][service_category] = {
                "queue": 5,
                "staff": 2,
                "recent_arrivals": 10
            }
        return self.branch_states[branch_id][service_category]

    async def ingest_event(self, event_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Ingests live event, updates queue/staff state, evaluates live ML predictor, and broadcasts critical alerts."""
        event_id = event_data.get("event_id") or f"EVT-{int(datetime.datetime.utcnow().timestamp() * 1000)}"
        branch_id = event_data["branch_id"]
        event_type = event_data["event_type"]
        service_category = event_data["service_category"]
        queue_override = event_data.get("queue_length")
        staff_override = event_data.get("staff_available")

        state = self.get_state(branch_id, service_category)

        # Update real-time state based on event type
        if queue_override is not None and queue_override > 0:
            state["queue"] = queue_override
        else:
            if event_type == "CUSTOMER_ARRIVAL":
                state["queue"] += 1
                state["recent_arrivals"] += 1
            elif event_type == "SERVICE_COMPLETED":
                state["queue"] = max(0, state["queue"] - 1)

        if staff_override is not None and staff_override > 0:
            state["staff"] = staff_override
        else:
            if event_type == "STAFF_AVAILABLE":
                state["staff"] += 1
            elif event_type == "STAFF_ABSENT":
                state["staff"] = max(1, state["staff"] - 1)

        # Record to Database
        db_event = LiveEvent(
            event_id=event_id,
            branch_id=branch_id,
            event_type=event_type,
            service_category=service_category,
            timestamp=datetime.datetime.utcnow(),
            queue_length=state["queue"],
            staff_available=state["staff"]
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        # Run Live Prediction with Member 1's model
        prediction = ml_service.live_predictor.predict_live(
            branch_id=branch_id,
            service_category=service_category,
            current_queue=state["queue"],
            staff_available=state["staff"],
            recent_arrivals=state["recent_arrivals"]
        )

        risk_level = prediction["bottleneck_risk"]
        pred_wait = prediction["predicted_wait_minutes"]

        # If HIGH or CRITICAL risk detected, broadcast real-time WebSocket alert!
        if risk_level in ["HIGH", "CRITICAL"]:
            alert_payload = {
                "event": "BOTTLENECK_ALERT",
                "branch_id": branch_id,
                "service_category": service_category,
                "risk_level": risk_level,
                "message": f"{risk_level}: {service_category} queue at branch {branch_id} is predicted to exceed {pred_wait:.1f} minutes.",
                "data": {
                    "queue_length": state["queue"],
                    "predicted_wait_minutes": pred_wait,
                    "staff_available": state["staff"],
                    "staff_required": prediction["staff_required"],
                    "staff_gap": prediction["staff_gap"],
                    "explanation": prediction["explanation"],
                    "digital_redirection": prediction["digital_redirection"]
                },
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            await ws_manager.broadcast(alert_payload, target_branch_id=branch_id)

        # Also publish to Redis Stream if Redis is connected
        if self.redis_client:
            try:
                self.redis_client.xadd(
                    "bank_branch_events",
                    {"event_id": event_id, "branch_id": branch_id, "risk": risk_level, "payload": json.dumps(prediction)}
                )
            except Exception as e:
                logger.debug(f"[LiveService] Redis publish skipped: {e}")

        return {
            "event_id": event_id,
            "branch_id": branch_id,
            "service_category": service_category,
            "event_type": event_type,
            "queue_length": state["queue"],
            "staff_available": state["staff"],
            "prediction": prediction
        }


live_service = LiveService()
