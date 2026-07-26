import os
import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.chatbot.gemini_client import GeminiUnavailable, extract_resume_data
from app.chatbot.resume_parser import extract_text
from app.core.db import get_db
from app.embeddings.faiss_index import employee_index
from app.models.models import Employee
from app.schemas.schemas import EmployeeOut

router = APIRouter(tags=["resumes"])

RESUME_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "resumes")


@router.post("/uploadResume", response_model=EmployeeOut)
async def upload_resume(
    file: UploadFile = File(...),
    name: str = Form(...),
    location: str = Form(""),
    grade: str = Form(""),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX resumes are supported")

    content = await file.read()
    try:
        resume_text = extract_text(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extracted = extract_resume_data(resume_text)

    os.makedirs(RESUME_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    with open(os.path.join(RESUME_DIR, stored_name), "wb") as f:
        f.write(content)

    employee = Employee(
        name=name,
        grade=grade or None,
        location=location or None,
        experience_years=extracted.get("experience_years", 0) or 0,
        skills=extracted.get("skills", []) or [],
        certifications=extracted.get("certifications", []) or [],
        previous_projects=extracted.get("projects", []) or [],
        domain_experience=extracted.get("domain_experience", []) or [],
        availability_date=date.today(),
        resume_path=stored_name,
        resume_text=resume_text,
        performance_rating=4.0,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    # The candidate is already saved; a failed embedding just means they are found
    # by skill matching until the index rebuilds on a later search.
    try:
        employee_index.add_employee(employee)
    except GeminiUnavailable:
        pass

    return employee
