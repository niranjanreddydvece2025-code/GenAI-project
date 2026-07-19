import json

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

_chat_model = genai.GenerativeModel(settings.gemini_chat_model)


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    result = genai.embed_content(
        model=settings.gemini_embed_model,
        content=text,
        task_type=task_type,
    )
    return result["embedding"]


def parse_search_query(query: str) -> dict:
    """Turn a natural-language manager query into structured search criteria."""
    prompt = f"""You are a staffing assistant. Extract structured search criteria from this
project manager request. Respond with ONLY valid JSON, no markdown fences.

Query: "{query}"

JSON schema:
{{
  "skills": ["list of required/related skills mentioned or implied"],
  "domain": "domain/industry experience mentioned, or empty string",
  "location": "location mentioned, or empty string",
  "min_experience_years": <number or 0 if not mentioned>,
  "headcount": <number of people requested, default 1>,
  "availability_required": true/false,
  "certifications": ["any certifications mentioned"]
}}"""
    response = _chat_model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.lower().startswith("json"):
            text = text.split("\n", 1)[1]
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return {
            "skills": [query],
            "domain": "",
            "location": "",
            "min_experience_years": 0,
            "headcount": 1,
            "availability_required": False,
            "certifications": [],
        }


def generate_candidate_summary(employee: dict) -> str:
    prompt = f"""Write a concise 2-3 sentence professional summary for this employee,
in the style of a staffing recommendation. Be factual, use only the data given.

Name: {employee.get('name')}
Experience: {employee.get('experience_years')} years
Skills: {', '.join(employee.get('skills', []))}
Domain experience: {', '.join(employee.get('domain_experience', []))}
Certifications: {', '.join(employee.get('certifications', []))}
Previous projects: {employee.get('previous_projects')}
Availability: {employee.get('availability_date')}
Performance rating: {employee.get('performance_rating')}/5"""
    response = _chat_model.generate_content(prompt)
    return response.text.strip()


def extract_resume_data(resume_text: str) -> dict:
    """Use Gemini to pull structured fields out of raw resume text."""
    prompt = f"""Extract structured fields from this resume text. Respond with ONLY valid JSON,
no markdown fences.

Resume text:
\"\"\"{resume_text[:12000]}\"\"\"

JSON schema:
{{
  "skills": ["list of technical skills"],
  "experience_years": <estimated total years of experience as a number>,
  "certifications": ["list of certifications"],
  "projects": [{{"name": "project or role title", "description": "short description"}}],
  "domain_experience": ["industry domains e.g. Finance, Healthcare"]
}}"""
    response = _chat_model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.lower().startswith("json"):
            text = text.split("\n", 1)[1]
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return {
            "skills": [],
            "experience_years": 0,
            "certifications": [],
            "projects": [],
            "domain_experience": [],
        }
