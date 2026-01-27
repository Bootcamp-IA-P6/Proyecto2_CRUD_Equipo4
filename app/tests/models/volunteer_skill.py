from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base


class VolunteerSkill(Base):
    """Modelo para la tabla intermedia volunteer_skills (solo para tests)"""
    __tablename__ = "volunteer_skills"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
 
    volunteer = relationship("Volunteer")
    skill = relationship("Skill")