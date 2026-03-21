from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.models.session import Session as SessionModel
from app.models.session_block import SessionBlock
from app.schemas.session import SessionDetailSchema, SessionSummarySchema

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=List[SessionSummarySchema])
def list_sessions(db: Session = Depends(get_db)):
    stmt = (
        select(SessionModel)
        .options(selectinload(SessionModel.blocks))
        .order_by(SessionModel.date.desc().nullslast(), SessionModel.title)
    )
    records = db.scalars(stmt).all()
    return records


@router.get("/{session_id}", response_model=SessionDetailSchema)
def get_session(session_id: str, db: Session = Depends(get_db)):
    stmt = (
        select(SessionModel)
        .where(SessionModel.id == session_id)
        .options(
            selectinload(SessionModel.warmup),
            selectinload(SessionModel.blocks).selectinload(SessionBlock.exercises_raw),
            selectinload(SessionModel.blocks).selectinload(SessionBlock.items_canonical),
        )
    )
    session_obj = db.scalars(stmt).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_obj
