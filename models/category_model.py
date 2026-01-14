from sqlalchemy import Column, Integer, String, Text
from database.database import Base

class Category(Base):
    __tablename__="categories"
    id= Column(Integer, primary_key=True,index=True, autoincrement=True)
    name= Column(String(100), nullable=False)
    description= Column(Text)