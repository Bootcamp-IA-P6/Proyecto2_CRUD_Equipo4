from sqlalchemy import Column, Integer, ForeignKey
from database.database import Base


project_skills = Table(
    "project_skills",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),

    # Restricción única para evitar duplicados
    UniqueConstraint('project_id', 'skill_id', name='uq_project_skill'),
)
