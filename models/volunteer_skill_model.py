from sqlalchemy import Column, Integer, ForeignKey
from database.database import Base

class VolunteerSkill(Base):
    __tablename__ = "volunteers_skills"

    id = Column(Integer, primary_key=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
