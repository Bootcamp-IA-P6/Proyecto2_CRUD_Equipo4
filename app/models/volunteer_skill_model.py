from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from app.database.database import Base


volunteer_skills = Table(
    "volunteer_skills",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("volunteer_id", ForeignKey("volunteers.id"), nullable=False),
    Column("skill_id", ForeignKey("skills.id"), nullable=False),
    Column("deleted_at", DateTime, nullable=True),

)
