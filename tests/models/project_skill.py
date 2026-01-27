from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from database.database import Base


class ProjectSkill(Base):
    """Modelo para la tabla intermedia project_skills (solo para tests)"""
    __tablename__ = "project_skills"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
   
    
    
    project = relationship("Project")
    skill = relationship("Skill")