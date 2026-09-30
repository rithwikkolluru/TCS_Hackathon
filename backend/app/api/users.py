from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.db.schemas import UserOut, ResponseEnvelope
from backend.app.core.dependencies import get_current_user, require_manager_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=ResponseEnvelope[List[UserOut]])
def list_users(current_user: User = Depends(require_manager_role), db: Session = Depends(get_db)):
    """Lists staff users. Regional ops can see all; managers see their own branch staff."""
    query = db.query(User)
    if current_user.role == "manager":
        query = query.filter(User.branch_id == current_user.branch_id)

    users = query.all()
    users_out = [UserOut.from_orm(u) for u in users]
    return ResponseEnvelope[List[UserOut]](
        success=True,
        data=users_out,
        explanation=f"Retrieved {len(users_out)} staff users."
    )


@router.get("/{user_id}", response_model=ResponseEnvelope[UserOut])
def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches details for a single staff member."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if current_user.role == "manager" and user.branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access users of other branches.")

    return ResponseEnvelope[UserOut](
        success=True,
        data=UserOut.from_orm(user),
        explanation=f"Details for user {user.email}."
    )
