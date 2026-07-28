import re
from datetime import date

from app.models.models import Employee

WEIGHTS = {
    "skill_match": 0.40,
    "experience": 0.20,
    "availability": 0.15,
    "certifications": 0.10,
    "projects": 0.10,
    "rating": 0.05,
}


def _tokens(skill: str) -> frozenset[str]:
    """Split a skill into comparable word tokens: 'PL/SQL' -> {'pl', 'sql'}."""
    return frozenset(t for t in re.split(r"[^a-z0-9+#]+", skill.lower()) if t)


def _matches(required: frozenset[str], employee: frozenset[str]) -> bool:
    """True when one skill's tokens fully contain the other's.

    Set equality alone is too strict: a query for "Oracle" or "EBS" never equals
    the stored skill "Oracle EBS", so the strongest Oracle consultants scored zero.
    Containment lets a broad term match a specific skill and vice versa, while
    still keeping "Java" and "JavaScript" apart — they share no token.
    """
    return required <= employee or employee <= required


def _skill_score(employee_skills: list[str], required_skills: list[str], semantic_score: float) -> float:
    if not required_skills:
        return semantic_score
    emp_tokens = [_tokens(s) for s in employee_skills]
    req_tokens = [_tokens(s) for s in required_skills]
    req_tokens = [r for r in req_tokens if r]
    if not req_tokens:
        return semantic_score
    matched = sum(1 for r in req_tokens if any(_matches(r, e) for e in emp_tokens))
    overlap = matched / len(req_tokens)
    # Blend keyword overlap with semantic similarity from FAISS to reward related-but-not-identical skills.
    return max(overlap, semantic_score)


def _experience_score(employee_years: float, min_years: float) -> float:
    if min_years <= 0:
        return min(employee_years / 10, 1.0)
    if employee_years >= min_years:
        return 1.0
    return max(employee_years / min_years, 0.0)


def _availability_score(availability_date, required: bool) -> float:
    if availability_date is None:
        return 0.5
    today = date.today()
    if availability_date <= today:
        return 1.0
    days_out = (availability_date - today).days
    if days_out <= 7:
        return 0.8
    if days_out <= 30:
        return 0.5
    return 0.2


def _certification_score(employee_certs: list[str], required_certs: list[str]) -> float:
    if not required_certs:
        return min(len(employee_certs) / 3, 1.0) if employee_certs else 0.0
    emp_lower = {c.lower() for c in employee_certs}
    req_lower = {c.lower() for c in required_certs}
    if not req_lower:
        return 0.0
    return len(emp_lower & req_lower) / len(req_lower)


def _project_score(previous_projects, domain: str, employee_domains: list[str]) -> float:
    base = min(len(previous_projects or []) / 3, 1.0)
    if domain and employee_domains:
        domain_match = 1.0 if domain.lower() in [d.lower() for d in employee_domains] else 0.0
        return (base + domain_match) / 2
    return base


def score_candidate(employee: Employee, criteria: dict, semantic_score: float) -> tuple[float, dict, list[str]]:
    skill_s = _skill_score(employee.skills or [], criteria.get("skills", []), semantic_score)
    exp_s = _experience_score(employee.experience_years or 0, criteria.get("min_experience_years", 0))
    avail_s = _availability_score(employee.availability_date, criteria.get("availability_required", False))
    cert_s = _certification_score(employee.certifications or [], criteria.get("certifications", []))
    proj_s = _project_score(employee.previous_projects, criteria.get("domain", ""), employee.domain_experience or [])
    rating_s = (employee.performance_rating or 0) / 5

    breakdown = {
        "skill_match": round(skill_s * 100, 1),
        "experience": round(exp_s * 100, 1),
        "availability": round(avail_s * 100, 1),
        "certifications": round(cert_s * 100, 1),
        "projects": round(proj_s * 100, 1),
        "rating": round(rating_s * 100, 1),
    }

    total = (
        skill_s * WEIGHTS["skill_match"]
        + exp_s * WEIGHTS["experience"]
        + avail_s * WEIGHTS["availability"]
        + cert_s * WEIGHTS["certifications"]
        + proj_s * WEIGHTS["projects"]
        + rating_s * WEIGHTS["rating"]
    ) * 100

    reasons = []
    if skill_s >= 0.8:
        reasons.append(f"{breakdown['skill_match']}% skill match")
    if criteria.get("domain") and criteria["domain"].lower() in [d.lower() for d in (employee.domain_experience or [])]:
        reasons.append(f"{criteria['domain']} domain experience")
    if employee.certifications:
        reasons.append(f"Certified: {', '.join(employee.certifications[:2])}")
    if avail_s >= 0.8:
        reasons.append("Available immediately")
    if rating_s >= 0.9:
        reasons.append("Top performance rating")
    if not reasons:
        reasons.append(f"Overall match {round(total, 1)}%")

    return round(total, 1), breakdown, reasons
