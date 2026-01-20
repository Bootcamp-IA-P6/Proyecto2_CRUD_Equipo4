import enum
from datetime import datetime
from sqlalchemy import  Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from database.database import Base
from domain.projects_enums import Project_status, Project_priority
from models.project_skill_model import project_skills


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[Project_status] = mapped_column(Enum(Project_status), default=Project_status.not_assigned, nullable=False)
    priority: Mapped[Project_priority] = mapped_column(Enum(Project_priority), default=Project_priority.medium)

    category_id : Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))

    category = relationship("Category")

    skills = relationship("Skill", secondary=project_skills, back_populates="projects")

