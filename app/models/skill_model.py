from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship
from app.models.volunteer_skill_model import volunteer_skills
from app.models.project_skill_model import project_skills


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)

    volunteers = relationship("Volunteer", secondary= volunteer_skills, back_populates="skills") 
    projects = relationship("Project", secondary=project_skills, back_populates="skills")   
