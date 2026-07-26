from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.chatbot.gemini_client import (
    GeminiUnavailable,
    generate_candidate_summary,
    parse_search_query,
)
from app.chatbot.ranking import score_candidate
from app.core.db import get_db
from app.embeddings.faiss_index import employee_index
from app.models.models import Employee
from app.schemas.schemas import CandidateResult, EmployeeOut, SearchRequest, SearchResponse

router = APIRouter(tags=["search"])


@router.post("/searchCandidates", response_model=SearchResponse)
def search_candidates(payload: SearchRequest, db: Session = Depends(get_db)):
    criteria = parse_search_query(payload.query)

    # Rebuilds the index if a redeploy wiped it, so search never silently returns nothing.
    # Without embeddings we simply score on skill overlap instead of semantic similarity.
    try:
        employee_index.ensure_built(db)
        semantic_hits = dict(employee_index.search(payload.query, top_k=50))
    except GeminiUnavailable:
        semantic_hits = {}

    all_employees = db.query(Employee).all()
    scored = []
    for emp in all_employees:
        semantic_score = semantic_hits.get(emp.id, 0.0)
        total, breakdown, reasons = score_candidate(emp, criteria, semantic_score)
        scored.append((emp, total, breakdown, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    headcount = max(criteria.get("headcount", 1) or 1, 1)
    top = scored[: max(payload.top_k, headcount)]

    candidates = []
    for emp, total, breakdown, reasons in top:
        summary = emp.ai_summary or generate_candidate_summary(
            {
                "name": emp.name,
                "experience_years": emp.experience_years,
                "skills": emp.skills,
                "domain_experience": emp.domain_experience,
                "certifications": emp.certifications,
                "previous_projects": emp.previous_projects,
                "availability_date": str(emp.availability_date),
                "performance_rating": emp.performance_rating,
            }
        )
        if not emp.ai_summary:
            emp.ai_summary = summary
            db.add(emp)
        candidates.append(
            CandidateResult(
                employee=EmployeeOut.model_validate(emp),
                match_percent=total,
                score_breakdown=breakdown,
                reasons=reasons,
                ai_summary=summary,
            )
        )
    db.commit()

    return SearchResponse(query=payload.query, candidates=candidates)
