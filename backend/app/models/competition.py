import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    season_year = Column(Integer, nullable=True)
    organizer = Column(String, nullable=True)
    metadata = Column(JSONB, nullable=True)
