import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.db.schemas import UserRegister, UserLogin, UserOut, TokenResponse, ResponseEnvelope
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.dependencies import get_current_user
from backend.app.core.sanitizer import sanitize_data
from backend.app.services.audit_service import record_audit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ResponseEnvelope[UserOut])
def register_user(req: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Registers a new internal bank staff user (Manager, Employee, or Regional Ops)."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Validate branch assignment: regional_ops can have None, but manager and employee require branch_id
    if req.role in ["manager", "employee"] and not req.branch_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{req.role}' requires a valid branch_id assignment."
        )

    user = User(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
        branch_id=req.branch_id,
        is_active=True,
        created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    record_audit(
        db=db,
        action="user_register",
        user_id=user.id,
        role=user.role,
        resource="users",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
        metadata={"email": user.email, "role": user.role, "branch_id": user.branch_id}
    )

    user_out = UserOut.from_orm(user)
    return ResponseEnvelope[UserOut](
        success=True,
        data=user_out,
        explanation=f"User {user.email} successfully registered with role {user.role}."
    )


@router.post("/login", response_model=ResponseEnvelope[TokenResponse])
def login_user(req: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticates user credentials and issues a signed JWT bearer access token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        record_audit(
            db=db,
            action="login_failure",
            resource="auth",
            ip_address=request.client.host if request.client else None,
            metadata={"attempted_email": req.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact branch administrator."
        )

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "branch_id": user.branch_id
    }
    access_token = create_access_token(token_payload)

    record_audit(
        db=db,
        action="login_success",
        user_id=user.id,
        role=user.role,
        resource="auth",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None
    )

    user_out = UserOut.from_orm(user)
    token_resp = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_out
    )

    return ResponseEnvelope[TokenResponse](
        success=True,
        data=token_resp,
        explanation=f"Welcome {user.name}. Authenticated successfully as {user.role}."
    )


@router.post("/refresh", response_model=ResponseEnvelope[TokenResponse])
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refreshes the current active user's JWT access token."""
    token_payload = {
        "sub": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "branch_id": current_user.branch_id
    }
    new_token = create_access_token(token_payload)
    user_out = UserOut.from_orm(current_user)

    return ResponseEnvelope[TokenResponse](
        success=True,
        data=TokenResponse(access_token=new_token, token_type="bearer", user=user_out),
        explanation="Access token refreshed successfully."
    )


@router.get("/me", response_model=ResponseEnvelope[UserOut])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the authenticated user."""
    user_out = UserOut.from_orm(current_user)
    return ResponseEnvelope[UserOut](
        success=True,
        data=user_out,
        explanation=f"Profile retrieved for user {current_user.email}."
    )


@router.post("/logout", response_model=ResponseEnvelope[Dict[str, str]])
def logout_user(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logs out the user and writes an audit log."""
    record_audit(
        db=db,
        action="logout",
        user_id=current_user.id,
        role=current_user.role,
        resource="auth",
        resource_id=str(current_user.id),
        ip_address=request.client.host if request.client else None
    )

    return ResponseEnvelope[Dict[str, str]](
        success=True,
        data={"message": "Logged out successfully."},
        explanation="Session terminated."
    )
