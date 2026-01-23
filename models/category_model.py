from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime
from datetime import datetime
from database.database import Base

class Category(Base):
    __tablename__="categories"
    id:Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    name:Mapped[str]= mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)   
    deleted_at: Mapped[datetime | None] = mapped_column( DateTime, nullable= True, default= None)
    
    projects = relationship("Project", back_populates="category")
