import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.program_day import ProgramDay
from app.schemas.program_day import ProgramDayDetailSchema, ProgramDaySummarySchema

router = APIRouter(prefix="/program-days", tags=["program_days"])


@router.get("/", response_model=List[ProgramDaySummarySchema])
def list_program_days(
    db: Session = Depends(get_db),
):
    stmt = select(ProgramDay).order_by(ProgramDay.date.desc().nullslast())
    records = db.scalars(stmt).all()
    return records


@router.get("/{day_id}", response_model=ProgramDayDetailSchema)
def get_program_day(
    day_id: str,
    db: Session = Depends(get_db),
):
    filters = [ProgramDay.day_id == day_id]
    try:
        day_uuid = uuid.UUID(day_id)
        filters.append(ProgramDay.id == day_uuid)
    except ValueError:
        day_uuid = None

    stmt = select(ProgramDay).where(or_(*filters))
    program_day = db.scalars(stmt).first()
    if program_day:
        return program_day

    raise HTTPException(status_code=404, detail="Program day not found")
