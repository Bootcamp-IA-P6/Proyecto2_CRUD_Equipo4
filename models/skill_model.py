from sqlalchemy import Column, Integer, String
from database.database import Base
from sqlalchemy.orm import relationship
from models.volunteer_skill_model import volunteer_skills
from models.project_skill_model import project_skills


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)

    volunteers = relationship("Volunteer", secondary= volunteer_skills, back_populates="skills") 
    projects = relationship("Project", secondary=project_skills, back_populates="skills")   
