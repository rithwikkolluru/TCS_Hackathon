import sys
import logging
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add repo root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.db.database import engine, Base, check_db_connection
from backend.app.core.security import decode_access_token
from backend.app.core.sanitizer import sanitize_data
from backend.app.services.ml_service import ml_service
from backend.app.services.live_service import live_service
from backend.app.websocket.manager import ws_manager

# Import API Routers
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.api.branches import router as branches_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.live import router as live_router
from backend.app.api.feedback import router as feedback_router
from backend.app.api.audit import router as audit_router
from backend.app.api.reports import router as regional_router
from backend.app.api.hybrid_ai import router as hybrid_ai_router
from backend.app.api.dataset import router as dataset_router


# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("main")

# Create tables in DB
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-grade Backend, Database, Security & Real-time Layer for "
        "Intelligent Branch Service Load and Customer Experience Optimizer."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "frontend": "http://localhost:5173",
        "health": "/health"
    }


# Register API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(branches_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(live_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(regional_router, prefix="/api")
app.include_router(hybrid_ai_router, prefix="/api")
app.include_router(dataset_router, prefix="/api")



@app.get("/health", tags=["Health"])
def health_check():
    """System health check endpoint verifying database, Redis streams, and ML model states."""
    db_ok = check_db_connection()
    redis_ok = live_service.check_redis()
    models_ok = ml_service.footfall_model is not None and ml_service.wait_model is not None

    return {
        "status": "healthy" if db_ok and models_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "offline (in-memory fallback active)",
        "ml_models": "loaded" if models_ok else "error"
    }


@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Bearer access token")
):
    """Secure real-time WebSocket channel for operational surge & bottleneck alerts with RBAC routing."""
    # Authenticate token
    payload = decode_access_token(token)
    if not payload:
        logger.warning("[WebSocket] Rejected connection: invalid or expired token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = int(payload.get("sub", 0))
    role = payload.get("role", "employee")
    branch_id = payload.get("branch_id")

    await ws_manager.connect(websocket, user_id=user_id, role=role, branch_id=branch_id)

    # Send initial welcome confirmation
    await ws_manager.send_personal(websocket, {
        "event": "CONNECTED",
        "message": f"Connected to Real-time Alert Gateway as {role}.",
        "branch_id": branch_id
    })

    try:
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"[WebSocket] Exception in connection: {e}")
        ws_manager.disconnect(websocket)
