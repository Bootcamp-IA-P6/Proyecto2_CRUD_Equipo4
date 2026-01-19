from sqlalchemy import Column, Integer, ForeignKey
from database.database import Base

class ProjectSkill(Base):
    __tablename__ = "projects_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    project_id : Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))
    skill_id : Mapped[int] = mapped_column(Integer, ForeignKey('skills.id'))

    project = relationship("Project")
    skill = relationship("Skill")

    
    #evitar duplicados project_id+skill_id en DB
    __table_args__ = (
        UniqueConstraint('project_id', 'skill_id', name='uq_project_skill'),
    )