from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from database.database import Base
import enum
from datetime import datetime


class VolunteerStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class Volunteer(Base):
    __tablename__ = "volunteer"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    status = Column(Enum(VolunteerStatus), default=VolunteerStatus.active, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
