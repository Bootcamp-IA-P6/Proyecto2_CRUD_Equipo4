from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from database.database import Base
from domain.assignment_enum import AssignmentStatus


class Assignment(Base):
    __tablename__ = 'assignments'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        utoincrement=True
        )
    project_skill_id: Mapped[int] = mapped_column(
        ForeignKey('project_skills.id'),
        nullable=False
    )
    volunteer_skill_id: Mapped[int] = mapped_column(
        ForeignKey('volunteer_skills.id'),
        nullable=False
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus), 
        default = AssignmentStatus.PENDING, 
        nullable=False)
    
    # Relationships
    project_skill = relationship('ProjectSkill', back_populates='assignments')
    volunteer_skill = relationship('VolunteerSkill', back_populates='assignments')