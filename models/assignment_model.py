from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base
import enum
from domain.assignment_enum import AssignmentStatus



class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_skill_id = Column(
        Integer,
        ForeignKey('project_skills.id'),
        nullable=False
    )
    volunteer_skill_id = Column(
        Integer,
        ForeignKey('volunteer_skills.id'),
        nullable=False
    )
    status = Column(Enum(AssignmentStatus), default = AssignmentStatus.pending, nullable=False)
    
    # Relationships
    project_skill = relationship('ProjectSkill', back_populates='assignments')
    volunteer_skill = relationship('VolunteerSkill', back_populates='assignments')