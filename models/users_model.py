from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from database.database import Base
from typing import Optional



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] =mapped_column(String(100),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    #role_id: Mapped[int] = mapped_column(ForeignKey('role.id'), nullable=False)
