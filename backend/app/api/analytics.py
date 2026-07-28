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

    # Count only skills the workforce actually has, matched against the query text.
    # Splitting on whitespace instead would rank filler words ("find", "with",
    # "developers") above real skills, and would break multi-word skills like
    # "Oracle EBS" into meaningless fragments.
    known_skills = {skill.lower(): skill for skill in skill_counter}
    shortlists = db.query(Shortlist).all()
    requested_skill_counter: Counter = Counter()
    for s in shortlists:
        if not s.query_text:
            continue
        lowered = s.query_text.lower()
        for skill_lower, skill in known_skills.items():
            if skill_lower in lowered:
                requested_skill_counter[skill] += 1

    alloc_days = [
        max((a.allocation_date - e.created_at.date()).days, 0)
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
