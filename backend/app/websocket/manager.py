import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
from backend.app.core.sanitizer import sanitize_data

logger = logging.getLogger("websocket")


class ConnectionManager:
    """Manages authenticated WebSocket clients with RBAC and branch isolation routing."""

    def __init__(self):
        # Maps websocket to connection metadata dict: {"user_id": ..., "role": ..., "branch_id": ...}
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, role: str, branch_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections[websocket] = {
            "user_id": user_id,
            "role": role,
            "branch_id": branch_id
        }
        logger.info(f"[WebSocket] Connected user={user_id} role={role} branch={branch_id}. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            meta = self.active_connections.pop(websocket)
            logger.info(f"[WebSocket] Disconnected user={meta.get('user_id')}. Remaining active: {len(self.active_connections)}")

    async def broadcast(self, event_data: Dict[str, Any], target_branch_id: Optional[str] = None):
        """Broadcasts an alert event to authorized connections with branch isolation and PII sanitization."""
        # Enforce sanitization
        sanitized_event = sanitize_data(event_data)
        message_json = json.dumps(sanitized_event)

        disconnected = []
        for ws, meta in self.active_connections.items():
            user_role = meta.get("role")
            user_branch = meta.get("branch_id")

            # Route based on RBAC and branch isolation:
            # - regional_ops receives alerts across all branches
            # - manager/employee receives alerts only for their assigned branch
            if target_branch_id:
                if user_role != "regional_ops" and user_branch != target_branch_id:
                    continue

            try:
                await ws.send_text(message_json)
            except Exception as e:
                logger.warning(f"[WebSocket] Error sending message to connection: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Sends a private message to a specific connection."""
        sanitized = sanitize_data(message)
        try:
            await websocket.send_text(json.dumps(sanitized))
        except Exception as e:
            logger.warning(f"[WebSocket] Error sending personal message: {e}")
            self.disconnect(websocket)


ws_manager = ConnectionManager()
