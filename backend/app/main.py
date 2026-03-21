from fastapi import FastAPI

from app.api import sessions
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")
app.include_router(sessions.router)
