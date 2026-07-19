from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import Allocation, Employee, Shortlist
from app.schemas.schemas import AnalyticsResponse

router = APIRouter(tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    allocations = db.query(Allocation).all()

    allocated_ids = {a.employee_id for a in allocations if a.allocation_status == "Allocated"}
    bench_count = len(employees) - len(allocated_ids)

    skill_counter: Counter = Counter()
    for emp in employees:
        skill_counter.update(emp.skills or [])

    shortlists = db.query(Shortlist).all()
    requested_skill_counter: Counter = Counter()
    for s in shortlists:
        if s.query_text:
            for word in s.query_text.replace(",", " ").split():
                requested_skill_counter[word.strip(".").title()] += 1

    alloc_days = [
        (a.allocation_date - e.created_at.date()).days
        for a in allocations
        for e in [next((emp for emp in employees if emp.id == a.employee_id), None)]
        if e is not None and a.allocation_date and e.created_at
    ]
    avg_allocation_time = sum(alloc_days) / len(alloc_days) if alloc_days else None

    return AnalyticsResponse(
        employees_on_bench=bench_count,
        employees_allocated=len(allocated_ids),
        total_employees=len(employees),
        skill_distribution=dict(skill_counter.most_common(15)),
        most_requested_skills=[{"skill": k, "count": v} for k, v in requested_skill_counter.most_common(10)],
        average_allocation_time_days=avg_allocation_time,
    )
