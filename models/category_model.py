from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Integer, String, Text
from database.database import Base

class Category(Base):
    __tablename__="categories"
    id:Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    name:Mapped[str]= mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)   