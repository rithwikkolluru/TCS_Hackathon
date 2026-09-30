import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="employee")  # 'manager', 'employee', 'regional_ops'
    branch_id = Column(String(50), nullable=True, index=True)  # Nullable for regional_ops
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    recommendation_actions = relationship("RecommendationAction", back_populates="user")


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    branch_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "BR001"
    branch_name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False, default="Telangana")
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    total_counters = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    branch_id = Column(String(50), index=True, nullable=False)
    employee_role = Column(String(50), nullable=False)  # 'Manager', 'Loan Officer', 'Teller', etc.
    supported_services = Column(Text, nullable=False)  # JSON string or comma-separated list of services
    status = Column(String(50), default="AVAILABLE")  # AVAILABLE, BUSY, BREAK, ABSENT, OFFLINE
    shift_start = Column(String(20), default="09:00")
    shift_end = Column(String(20), default="17:00")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CustomerReport(Base):
    """Sanitized customer visit/service record with ZERO PII."""
    __tablename__ = "customer_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    branch_id = Column(String(50), index=True, nullable=False)
    service_category = Column(String(100), index=True, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    service_start_time = Column(DateTime, nullable=True)
    service_end_time = Column(DateTime, nullable=True)
    waiting_time_minutes = Column(Float, default=0.0)
    service_time_minutes = Column(Float, default=0.0)
    token_number = Column(String(50), nullable=False)
    counter_id = Column(String(50), nullable=True)
    status = Column(String(50), default="COMPLETED")  # COMPLETED, WAITING, IN_SERVICE, CANCELLED


class LiveEvent(Base):
    __tablename__ = "live_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(String(50), index=True, nullable=False)
    branch_id = Column(String(50), index=True, nullable=False)
    event_type = Column(String(50), nullable=False)  # CUSTOMER_ARRIVAL, SERVICE_STARTED, SERVICE_COMPLETED, STAFF_AVAILABLE, STAFF_ABSENT
    service_category = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    queue_length = Column(Integer, default=0)
    staff_available = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    branch_id = Column(String(50), index=True, nullable=False)
    service_category = Column(String(100), nullable=False)
    recommendation_type = Column(String(50), nullable=False)  # STAFFING, DIGITAL_REDIRECTION, APPOINTMENT_NUDGE, BOTTLENECK_ALERT
    prediction_data = Column(Text, nullable=True)  # JSON formatted metadata
    recommendation_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    risk_level = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, ACCEPTED, REJECTED, EXPIRED

    # Actions taken on this recommendation
    actions = relationship("RecommendationAction", back_populates="recommendation")


class RecommendationAction(Base):
    """Tracks feedback and manager decision on AI recommendations for continuous feedback loop."""
    __tablename__ = "recommendation_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    action = Column(String(50), nullable=False)  # ACCEPT, REJECT, MODIFY
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    reason = Column(Text, nullable=True)
    actual_wait_after_action = Column(Float, default=0.0)
    actual_queue_after_action = Column(Integer, default=0)
    impact = Column(String(50), default="POSITIVE")  # POSITIVE, NEUTRAL, NEGATIVE

    # Relationships
    recommendation = relationship("Recommendation", back_populates="actions")
    user = relationship("User", back_populates="recommendation_actions")


class Feedback(Base):
    """Sanitized customer feedback record."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feedback_id = Column(String(50), index=True, nullable=False)
    branch_id = Column(String(50), index=True, nullable=False)
    service_category = Column(String(100), nullable=False)
    rating = Column(Integer, default=3)
    comment = Column(Text, nullable=False)
    sentiment = Column(String(50), default="Neutral")  # Positive, Negative, Neutral
    sentiment_score = Column(Float, default=0.0)
    topic = Column(String(100), default="general_service")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    """Tamper-evident audit log for tracking all sensitive backend events with zero PII."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    role = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String(50), nullable=True)
    metadata_json = Column(Text, nullable=True)
