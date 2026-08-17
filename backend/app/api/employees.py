from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import Allocation, Employee
from app.schemas.schemas import EmployeeOut

router = APIRouter(tags=["employees"])


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    allocated_ids = {employee_id for (employee_id,) in db.query(Allocation.employee_id).distinct()}
    return db.query(Employee).filter(Employee.id.not_in(allocated_ids)).order_by(Employee.name).all()


@router.get("/employee/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
