from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import Allocation, Employee, Project
from app.schemas.schemas import AllocationRequest, AllocationOut

router = APIRouter(prefix="/allocations", tags=["allocations"])


@router.post("", response_model=AllocationOut)
def create_allocation(
    allocation: AllocationRequest,
    db: Session = Depends(get_db),
):
    """Create a new allocation for an employee to a project."""
    employee = db.query(Employee).filter(Employee.id == allocation.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    existing_allocation = db.query(Allocation).filter(Allocation.employee_id == allocation.employee_id).first()
    if existing_allocation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee is already allocated to a project",
        )

    project = db.query(Project).filter(Project.id == allocation.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    new_allocation = Allocation(
        employee_id=allocation.employee_id,
        project_id=allocation.project_id,
        allocation_date=allocation.allocation_date,
        allocation_status="Allocated",
    )

    db.add(new_allocation)
    db.commit()
    db.refresh(new_allocation)

    return new_allocation


@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    """Get list of all projects for allocation dropdown."""
    projects = db.query(Project).all()
    return [{"id": p.id, "name": p.project_name, "location": p.location} for p in projects]


@router.get("/{employee_id}")
def get_employee_allocations(employee_id: int, db: Session = Depends(get_db)):
    """Get all allocations for an employee."""
    allocations = db.query(Allocation).filter(Allocation.employee_id == employee_id).all()
    return allocations
