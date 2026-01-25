from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum
from sqlalchemy import Enum

from app.database.database import Base
from app.domain.assignment_enum import AssignmentStatus


class Assignment(Base):
    __tablename__ = 'assignments'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
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
    
    