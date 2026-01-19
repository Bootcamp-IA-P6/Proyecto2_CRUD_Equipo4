from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from database.database import Base
import enum
from datetime import datetime
from domain.volunteer_enum import VolunteerStatus

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    status = Column(Enum(VolunteerStatus), default=VolunteerStatus.active, nullable=False)
