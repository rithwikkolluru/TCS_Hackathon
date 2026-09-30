from typing import List, Optional
from fastapi import HTTPException, status
from backend.app.db.models import User


class RoleChecker:
    """RBAC checker dependency verifying that current user has one of the required roles."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role in {self.allowed_roles}, but user has role '{user.role}'."
            )
        return user


def verify_branch_access(user: User, branch_id: Optional[str]) -> bool:
    """Enforces branch data isolation:
    - Regional ops can access all branches.
    - Managers & employees can strictly access ONLY their assigned branch.
    """
    if not branch_id:
        return True

    if user.role == "regional_ops":
        return True

    if user.branch_id != branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Branch isolation policy violation: User assigned to branch '{user.branch_id}' cannot access branch '{branch_id}'."
        )

    return True
