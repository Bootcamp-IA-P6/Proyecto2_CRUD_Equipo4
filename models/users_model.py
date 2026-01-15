from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from database.database import Base
from typing import Optional


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] =mapped_column(String(100),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    #role_id: Mapped[int] = mapped_column(ForeignKey('role.id'), nullable=False)