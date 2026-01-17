from sqlalchemy.orm import Session
from models.category_model import Category
from schemas.category_schemas import CategoryCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from config.logging_config import get_logger

logger = get_logger("category")


def create_category(db: Session, data: CategoryCreate):
    category = Category(**data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session):
    return db.query(Category).all()

def get_category(db: Session, id: int):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        logger.warning(f"Category with {id} does not exist")
        raise HTTPException(status_code=404, detail="Category not found")
    return category

def update_category(db: Session, id: int, data: CategoryCreate):
    category = get_category(db, id)
    try:
        """
        if not category:
            return None
        """
        category.name = data.name
        category.description = data.description
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        logger.warning(f"Category with {id} does not exist")
        raise HTTPException(status_code=404, detail="Category not found")


def delete_category(db: Session, id: int):
    category = get_category(db, id)
    try:   
        """
        if not category:
            return None
        """
        db.delete(category)
        db.commit()
        return category
    except IntegrityError:
        db.rollback()
        logger.warning(f"Category with {id} does not exist")
        raise HTTPException(status_code=404, detail="Category not found")


