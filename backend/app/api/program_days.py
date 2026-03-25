import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.program_day import ProgramDay
from app.models.session import Session as SessionModel
from app.schemas.program_day import ProgramDayDetailSchema, ProgramDaySummarySchema
from app.services.legacy_program_days import (
    legacy_program_day_detail,
    legacy_program_day_summaries,
)

router = APIRouter(prefix="/program-days", tags=["program_days"])


@router.get("/", response_model=List[ProgramDaySummarySchema])
def list_program_days(
    include_legacy: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(ProgramDay).order_by(ProgramDay.date.desc().nullslast())
    records = db.scalars(stmt).all()
    if records:
        return records
    if include_legacy:
        return legacy_program_day_summaries(db)
    return []


@router.get("/{day_id}", response_model=ProgramDayDetailSchema)
def get_program_day(
    day_id: str,
    include_legacy: bool = False,
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

    if include_legacy:
        if day_uuid:
            legacy = db.get(SessionModel, day_uuid)
            if legacy:
                return legacy_program_day_detail(legacy)
        legacy = (
            db.scalars(select(SessionModel).where(SessionModel.id == day_id)).first()
        )
        if legacy:
            return legacy_program_day_detail(legacy)

    raise HTTPException(status_code=404, detail="Program day not found")
