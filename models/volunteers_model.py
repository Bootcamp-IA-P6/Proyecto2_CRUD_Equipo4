from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
import enum
from datetime import datetime
from domain.volunteer_enum import VolunteerStatus
from models.volunteer_skill_model import volunteer_skills


class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    status = Column(Enum(VolunteerStatus), default=VolunteerStatus.active, nullable=False)

        # Relación con Skills
    skills = relationship("Skill", secondary=volunteer_skills, back_populates="volunteers")
