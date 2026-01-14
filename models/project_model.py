import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database.database import Base
from domains.projects_enums import Project_status, Project_priority


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime, nullable=False)
    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    status = Column(Enum(Project_status), default=Project_status.not_asigned, nullable=False)
    priority = Column(Enum(Project_priority), default=Project_priority.medium)

    #category_id = Column(Integer, ForeignKey('category.id'))

    #category = relationship("Category", back_populates="Project")

