from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    email: str
    role: str


class EmployeeOut(BaseModel):
    id: int
    name: str
    grade: Optional[str] = None
    location: Optional[str] = None
    experience_years: float
    skills: list[str] = []
    certifications: list[str] = []
    previous_projects: list[Any] = []
    domain_experience: list[str] = []
    current_allocation: Optional[str] = None
    availability_date: Optional[date] = None
    performance_rating: float
    ai_summary: Optional[str] = None

    class Config:
        from_attributes = True


class CandidateResult(BaseModel):
    employee: EmployeeOut
    match_percent: float
    score_breakdown: dict[str, float]
    reasons: list[str]
    ai_summary: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    query: str
    candidates: list[CandidateResult]


class ShortlistRequest(BaseModel):
    employee_id: int
    manager_email: str
    query_text: Optional[str] = None
    match_score: Optional[float] = None


class ShortlistOut(BaseModel):
    id: int
    employee_id: int
    manager_email: str
    query_text: Optional[str]
    match_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    employees_on_bench: int
    employees_allocated: int
    total_employees: int
    skill_distribution: dict[str, int]
    most_requested_skills: list[dict[str, Any]]
    average_allocation_time_days: Optional[float]
