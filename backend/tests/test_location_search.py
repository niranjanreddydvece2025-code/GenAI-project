from datetime import date

from app.chatbot.gemini_client import parse_search_query
from app.chatbot.ranking import score_candidate
from app.models.models import Employee


def test_parse_search_query_extracts_location_from_key_value_query():
    criteria = parse_search_query("location: Hyderabad")

    assert criteria["location"] == "Hyderabad"
    assert criteria["skills"] == []


def test_location_score_counts_toward_rank_for_location_only_searches():
    employee = Employee(
        id=1,
        name="Test User",
        location="Hyderabad",
        skills=[],
        certifications=[],
        previous_projects=[],
        domain_experience=[],
        experience_years=0,
        availability_date=date.today(),
        performance_rating=0,
    )

    total, breakdown, _ = score_candidate(employee, {"location": "Hyderabad", "skills": []}, 0.0)

    assert breakdown["location"] == 100.0
    assert total > 20
