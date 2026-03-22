from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    settings = get_settings()
    if payload.username != settings.API_USERNAME or payload.password != settings.API_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return LoginResponse(status="ok")
