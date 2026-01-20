from sqlalchemy import Table, Column, Integer, ForeignKey
from database.database import Base

volunteer_skills = Table(
    "volunteer_skills",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True)
    Column("volunteer_id", ForeignKey("volunteers.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)
