"""AI calls, with graceful fallbacks at every layer.

Chat runs on OpenRouter's free models; embeddings run on Gemini, because OpenRouter
has no embeddings endpoint and Gemini meters embeddings separately from its very
small free chat quota.

Every call can fail — rate limits on free models are real — so there are three
tiers: the primary chat model, a fallback chat model, and finally a deterministic
non-AI result. Search still ranks candidates on skill overlap, cards still show a
summary, and resumes still import. The app gets less clever without a working key
or quota, but it never returns an error page.
"""

import json
import logging
import re

import google.generativeai as genai
import requests
from google.api_core import exceptions as google_exceptions

from app.core.config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class GeminiUnavailable(RuntimeError):
    """No AI backend could serve the request (no key, rate limited, or unreachable)."""


def _call_openrouter(prompt: str, model: str, timeout: int = 90) -> str:
    response = requests.post(
        _OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1200,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "unknown OpenRouter error"))
    content = payload["choices"][0]["message"].get("content")
    if not content or not content.strip():
        raise RuntimeError("empty response")
    return content.strip()


def _generate(prompt: str) -> str:
    """Try the primary model, then the fallback, then give up so callers can degrade."""
    if not settings.openrouter_api_key:
        raise GeminiUnavailable("no OpenRouter API key configured")

    models = [settings.openrouter_model, settings.openrouter_fallback_model]
    last_error = "no models configured"
    for model in [m for m in models if m]:
        try:
            return _call_openrouter(prompt, model)
        except Exception as exc:  # noqa: BLE001 - any failure should try the next model
            last_error = f"{model}: {exc}"
            logger.warning("OpenRouter call failed (%s); trying next option.", last_error)
    raise GeminiUnavailable(last_error)


def _strip_fences(text: str) -> str:
    if not text.startswith("```"):
        return text
    text = text.strip("`")
    text = text.split("\n", 1)[1] if "\n" in text else text
    if text.lower().startswith("json"):
        text = text.split("\n", 1)[1]
    return text


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Embed text. Raises GeminiUnavailable so callers can skip semantic search."""
    try:
        result = genai.embed_content(
            model=settings.gemini_embed_model,
            content=text,
            task_type=task_type,
        )
    except google_exceptions.ResourceExhausted as exc:
        raise GeminiUnavailable("embedding quota exhausted") from exc
    except google_exceptions.GoogleAPIError as exc:
        raise GeminiUnavailable(str(exc)) from exc
    return result["embedding"]


# Words that carry no signal when we have to parse a query without the model.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "available", "be", "can", "developer",
    "developers", "engineer", "engineers", "experience", "find", "for", "get",
    "give", "have", "i", "in", "is", "me", "need", "of", "on", "one", "or",
    "people", "person", "resource", "resources", "someone", "the", "to", "two",
    "three", "four", "five", "want", "who", "with", "years", "yrs",
}

_NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _fallback_criteria(query: str) -> dict:
    """Pull rough criteria out of a query using plain text rules, no model needed."""
    lowered = query.lower()

    years = 0
    match = re.search(r"(\d+)\s*\+?\s*(?:years|yrs)", lowered)
    if match:
        years = int(match.group(1))

    headcount = 1
    match = re.search(r"\b(\d+)\s+(?!years|yrs)", lowered)
    if match:
        headcount = int(match.group(1))
    else:
        for word, value in _NUMBER_WORDS.items():
            if re.search(rf"\b{word}\b", lowered):
                headcount = value
                break

    # Anything left after removing filler is treated as a skill term.
    tokens = re.findall(r"[a-zA-Z][a-zA-Z+#./-]*", query)
    skills = [t for t in tokens if t.lower() not in _STOPWORDS and len(t) > 1]

    return {
        "skills": skills or [query],
        "domain": "",
        "location": "",
        "min_experience_years": years,
        "headcount": max(headcount, 1),
        "availability_required": any(
            w in lowered for w in ("immediate", "immediately", "available now", "asap")
        ),
        "certifications": [],
    }


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
    try:
        text = _strip_fences(_generate(prompt))
    except GeminiUnavailable:
        return _fallback_criteria(query)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return _fallback_criteria(query)


def _fallback_summary(employee: dict) -> str:
    """Build a factual summary from the employee's own fields."""
    name = employee.get("name") or "This consultant"
    parts = []

    years = employee.get("experience_years")
    skills = [s for s in (employee.get("skills") or []) if s]
    if years and skills:
        parts.append(f"{name} has {years:g} years of experience across {', '.join(skills[:4])}.")
    elif years:
        parts.append(f"{name} has {years:g} years of experience.")
    elif skills:
        parts.append(f"{name} works with {', '.join(skills[:4])}.")
    else:
        parts.append(f"{name} is available for staffing.")

    domains = [d for d in (employee.get("domain_experience") or []) if d]
    if domains:
        parts.append(f"Domain experience spans {', '.join(domains)}.")

    certs = [c for c in (employee.get("certifications") or []) if c]
    if certs:
        parts.append(f"Certified: {', '.join(certs)}.")

    rating = employee.get("performance_rating")
    availability = employee.get("availability_date")
    if rating and availability:
        parts.append(f"Rated {rating}/5, available from {availability}.")
    elif rating:
        parts.append(f"Rated {rating}/5.")
    elif availability:
        parts.append(f"Available from {availability}.")

    return " ".join(parts)


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
    try:
        return _generate(prompt)
    except GeminiUnavailable:
        return _fallback_summary(employee)


# Skill terms recognised when parsing a resume without the model.
_KNOWN_SKILLS = [
    "Oracle EBS", "Oracle SQL", "PL/SQL", "Oracle APEX", "Oracle Forms",
    "Oracle Database", "Oracle Fusion", "SQL", "Java", "Spring Boot", "Python",
    "React", "Angular", "Node.js", "AWS", "Azure", "GCP", "Kubernetes", "Docker",
    "Terraform", "Microservices", "REST APIs", "Data Migration", "ETL",
    "Data Warehousing", "DevOps", "CI/CD", "Kafka", "Machine Learning",
]

_KNOWN_DOMAINS = [
    "Finance", "Banking", "Insurance", "Retail", "Healthcare", "Manufacturing",
    "Telecom", "Automotive", "Logistics", "Energy",
]


def _fallback_resume_data(resume_text: str) -> dict:
    """Keyword-scan a resume when the model is unavailable."""
    lowered = resume_text.lower()

    skills = [s for s in _KNOWN_SKILLS if s.lower() in lowered]
    domains = [d for d in _KNOWN_DOMAINS if d.lower() in lowered]

    years = 0
    for match in re.finditer(r"(\d+)\s*\+?\s*(?:years|yrs)", lowered):
        years = max(years, int(match.group(1)))

    certifications = [
        line.strip(" -•\t")
        for line in resume_text.splitlines()
        if "certifi" in line.lower() and len(line.strip()) > 12
    ]

    return {
        "skills": skills,
        "experience_years": years,
        "certifications": certifications[:5],
        "projects": [],
        "domain_experience": domains,
    }


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
    try:
        text = _strip_fences(_generate(prompt))
    except GeminiUnavailable:
        return _fallback_resume_data(resume_text)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return _fallback_resume_data(resume_text)
