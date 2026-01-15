from sqlalchemy.orm import Session
from schemas import category_schemas  
from models.category_model import Category

class CategoryControllers:



    @staticmethod
    async def get_Catecory(db: Session, skip: int = 0, limit: int = 100):
            return db.query(Category).offset(skip).limit(limit).all()

    @staticmethod # Cada función es como un trabajador independiente que llega con su propio conjunto de herramientas (db) y hace su tarea.
    async def get_Category(db: Session, Category_id: int):
        return db.query(Category).filter(Category.id == Category_id).first()

    @staticmethod
    async def create_Category(db: Session, Category: category_schemas.CategoryCreate):
            db_Category = Category(**Category.dict())
            db.add(db_Category)
            db.commit()
            db.refresh(db_Category)
            return db_Category
  
    @staticmethod
    async def update_Category(db: Session, Category_id: int, Category: Category_schemas.CategoryCreate):
        db_Category = db.query(Category).filter(Category.id == Category_id).first()
        if db_Category:
            db_Category.title = Category.title
            db_Category.description = Category.description
            db.commit()
            db.refresh(db_Category)
        return db_Category
    
    @staticmethod
    async def delete_Category(db: Session, Category_id: int):
        db_Category = db.query(Category).filter(Category.id == Category_id).first()
        if db_Category:
            db.delete(db_Category)
            db.commit()
        return db_Category