from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import Shortlist
from app.schemas.schemas import ShortlistOut, ShortlistRequest

router = APIRouter(tags=["shortlist"])


@router.post("/shortlist", response_model=ShortlistOut)
def create_shortlist(payload: ShortlistRequest, db: Session = Depends(get_db)):
    entry = Shortlist(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/shortlist", response_model=list[ShortlistOut])
def list_shortlist(manager_email: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Shortlist)
    if manager_email:
        query = query.filter(Shortlist.manager_email == manager_email)
    return query.order_by(Shortlist.created_at.desc()).all()
