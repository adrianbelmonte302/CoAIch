from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.api import auth, program_days, sessions
from app.core.config import get_settings

security = HTTPBasic()
settings = get_settings()


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    correct_username = credentials.username == settings.API_USERNAME
    correct_password = credentials.password == settings.API_PASSWORD
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(sessions.router, dependencies=[Depends(get_current_user)])
app.include_router(program_days.router, dependencies=[Depends(get_current_user)])
