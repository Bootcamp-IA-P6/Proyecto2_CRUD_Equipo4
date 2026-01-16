from sqlalchemy import Column, Integer, String
from database.database import Base
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

users: Mapped[List["User"]] = relationship( back_populates="role")