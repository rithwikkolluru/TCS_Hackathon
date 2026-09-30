from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.core.security import decode_access_token
from backend.app.core.permissions import RoleChecker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Extracts and validates JWT bearer token from Header or OAuth2Scheme, returning active User."""
    extracted_token = token
    if not extracted_token and authorization and authorization.startswith("Bearer "):
        extracted_token = authorization.split(" ")[1]

    if not extracted_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(extracted_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


# Role Checkers
def require_manager_role(current_user: User = Depends(get_current_user)) -> User:
    return RoleChecker(["manager", "regional_ops"])(current_user)


def require_strict_manager_role(current_user: User = Depends(get_current_user)) -> User:
    return RoleChecker(["manager"])(current_user)


def require_regional_role(current_user: User = Depends(get_current_user)) -> User:
    return RoleChecker(["regional_ops"])(current_user)


def require_employee_role(current_user: User = Depends(get_current_user)) -> User:
    return RoleChecker(["employee", "manager", "regional_ops"])(current_user)
