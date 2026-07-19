import time

from fastapi import APIRouter
from jose import jwt

from app.core.config import settings
from app.schemas.schemas import LoginRequest, LoginResponse

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    """Dummy login for PoC: accepts any non-empty email/password."""
    role = "resource_manager" if "rm" in payload.email.lower() else "project_manager"
    token = jwt.encode(
        {"sub": payload.email, "role": role, "iat": int(time.time())},
        settings.jwt_secret,
        algorithm="HS256",
    )
    return LoginResponse(token=token, email=payload.email, role=role)
