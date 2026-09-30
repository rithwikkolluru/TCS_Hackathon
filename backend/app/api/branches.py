from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Branch, Staff, User
from backend.app.db.schemas import BranchOut, ResponseEnvelope
from backend.app.core.dependencies import get_current_user
from backend.app.core.permissions import verify_branch_access

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("", response_model=ResponseEnvelope[List[BranchOut]])
def list_branches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all available banking branches."""
    branches = db.query(Branch).all()
    branches_out = [BranchOut.from_orm(b) for b in branches]
    return ResponseEnvelope[List[BranchOut]](
        success=True,
        data=branches_out,
        explanation=f"Retrieved {len(branches_out)} active bank branches."
    )


@router.get("/{branch_code}", response_model=ResponseEnvelope[BranchOut])
def get_branch(branch_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches details for a specific branch."""
    verify_branch_access(current_user, branch_code)

    branch = db.query(Branch).filter(Branch.branch_code == branch_code).first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch {branch_code} not found.")

    return ResponseEnvelope[BranchOut](
        success=True,
        data=BranchOut.from_orm(branch),
        explanation=f"Branch details for {branch.branch_name} ({branch.branch_code})."
    )


@router.get("/{branch_code}/staff", response_model=ResponseEnvelope[List[Dict[str, Any]]])
def get_branch_staff(branch_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches the active staff roster for a branch."""
    verify_branch_access(current_user, branch_code)

    staff_members = db.query(Staff).filter(Staff.branch_id == branch_code).all()
    staff_data = [
        {
            "id": s.id,
            "employee_role": s.employee_role,
            "status": s.status,
            "supported_services": s.supported_services.split(",") if isinstance(s.supported_services, str) else s.supported_services,
            "shift_start": s.shift_start,
            "shift_end": s.shift_end
        }
        for s in staff_members
    ]

    return ResponseEnvelope[List[Dict[str, Any]]](
        success=True,
        data=staff_data,
        explanation=f"Retrieved {len(staff_data)} staff assignments for branch {branch_code}."
    )
