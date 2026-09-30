import datetime
from typing import Dict, Any, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


# --- Output Contracts ---
class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    explanation: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorDetail


# --- Auth & User Schemas ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=6)
    role: str = Field("employee", pattern="^(manager|employee|regional_ops)$")
    branch_id: Optional[str] = None


class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    branch_id: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Branch Schemas ---
class BranchOut(BaseModel):
    id: int
    branch_code: str
    branch_name: str
    city: str
    state: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_counters: int

    class Config:
        from_attributes = True


# --- Prediction Schemas ---
class FootfallRequest(BaseModel):
    branch_id: str
    date: str = Field(..., description="YYYY-MM-DD format")
    start_time: str = Field("11:00", description="HH:MM")
    end_time: str = Field("13:00", description="HH:MM")


class FootfallResponse(BaseModel):
    branch_id: str
    predicted_customers: int
    time_slot: str
    date: str
    explanation: str
    category_breakdown: Optional[Dict[str, int]] = None


class WaitTimeRequest(BaseModel):
    branch_id: str
    service_category: str
    queue_length: int = Field(..., ge=0)
    staff_available: int = Field(..., ge=1)
    recent_arrivals: Optional[int] = 10


class WaitTimeResponse(BaseModel):
    branch_id: str
    service_category: str
    predicted_wait_minutes: float
    risk_level: str
    queue_length: int
    staff_available: int
    explanation: str


class StaffRequirementRequest(BaseModel):
    branch_id: str
    date: Optional[str] = None
    start_time: Optional[str] = "11:00"
    end_time: Optional[str] = "13:00"
    expected_customers: Optional[int] = None
    service_category: Optional[str] = None


class StaffRequirementResponse(BaseModel):
    branch_id: str
    time_window: str
    predicted_customers: int
    staff_available: int
    staff_required: int
    additional_staff_required: int
    service_breakdown: Optional[Dict[str, Any]] = None
    explanation: str


# --- Bottleneck & Dashboard Schemas ---
class BottleneckItem(BaseModel):
    branch_id: str
    service_category: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    queue_length: int
    predicted_wait_minutes: float
    staff_available: int
    staff_required: int
    explanation: str


class ServiceLoadItem(BaseModel):
    service_category: str
    arrival_count: int
    queue_length: int
    average_wait: float
    predicted_wait: float
    staff_available: int
    staff_required: int
    risk_level: str


class DashboardSummary(BaseModel):
    branch_id: Optional[str] = None
    total_customers: int
    current_queue: int
    average_wait: float
    predicted_traffic: int
    high_risk_services: int
    staff_available: int
    staff_required: int
    active_recommendations: int


# --- Recommendation Schemas ---
class RecommendationOut(BaseModel):
    id: int
    branch_id: str
    service_category: str
    recommendation_type: str
    recommendation_text: str
    explanation: str
    risk_level: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class RecommendationGenerateRequest(BaseModel):
    branch_id: Optional[str] = None


class RecommendationActionRequest(BaseModel):
    reason: Optional[str] = None
    actual_wait_after_action: Optional[float] = None
    actual_queue_after_action: Optional[int] = None


class DigitalRedirectionResponse(BaseModel):
    service_category: str
    customer_type: str
    digital_available: bool
    digital_channel: str
    estimated_branch_time_saved_minutes: float
    confidence: float
    redirect_suitability: str
    instructions: str
    recommendation: str


# --- Feedback Loop Schemas ---
class RecommendationOutcomeRequest(BaseModel):
    recommendation_id: int
    action: str = Field(..., pattern="^(ACCEPTED|REJECTED|PARTIALLY_ACCEPTED|MODIFIED)$")
    actual_wait_after_action: float
    actual_queue_after_action: int
    reason: Optional[str] = None


class RecommendationOutcomeResponse(BaseModel):
    recommendation_id: int
    action: str
    wait_reduction_minutes: float
    queue_reduction: int
    impact: str  # POSITIVE, NEUTRAL, NEGATIVE
    message: str


class FeedbackSummaryResponse(BaseModel):
    branch_id: Optional[str] = None
    total_feedback: int
    average_rating: float
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    top_topics: List[Dict[str, Any]]
    service_sentiment: Dict[str, Any]
    branch_sentiment: Dict[str, Any]


# --- Live Event Schemas ---
class LiveEventCreate(BaseModel):
    event_id: Optional[str] = None
    branch_id: str
    event_type: str = Field(..., pattern="^(CUSTOMER_ARRIVAL|SERVICE_STARTED|SERVICE_COMPLETED|STAFF_AVAILABLE|STAFF_ABSENT)$")
    service_category: str
    queue_length: int = 0
    staff_available: int = 1


class LiveEventOut(BaseModel):
    id: int
    event_id: str
    branch_id: str
    event_type: str
    service_category: str
    queue_length: int
    staff_available: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


# --- Audit Log Schemas ---
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    role: Optional[str] = None
    action: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    timestamp: datetime.datetime
    ip_address: Optional[str] = None
    metadata_json: Optional[str] = None

    class Config:
        from_attributes = True
