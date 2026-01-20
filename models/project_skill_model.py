from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from database.database import Base


project_skills = Table(
    "project_skills",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("project_id", ForeignKey("projects.id"), nullable=False),
    Column("skill_id", ForeignKey("skills.id"), nullable=False),

    # Restricción única para evitar duplicados
    UniqueConstraint('project_id', 'skill_id', name='uq_project_skill'),
)
