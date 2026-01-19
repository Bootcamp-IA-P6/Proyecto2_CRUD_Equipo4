from sqlalchemy.orm import Session
from models.category_model import Category
from schemas.category_schemas import CategoryCreate, CategoryUpdate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from config.logging_config import get_logger
from datetime import datetime, timezone

logger = get_logger("category")


def create_category(db: Session, data: CategoryCreate):
    logger.info(f"Trying to create category with name {data.name}")

    existing = db.query(Category).filter(Category.name == data.name, Category.deleted_at.is_(None)).first()
    if existing:
        logger.warning(f"Category {data.name} already exist (id={existing.id})")
        raise HTTPException(status_code=400, detail="Category already exist")
    
    category = Category(**data.dict())
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        logger.info(f"Category with ID {category.id} created successfully.")
        return category
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating category '{data.name}': {e}")
        raise HTTPException(status_code=409, detail=f"Category violates a database constraint")


def get_categories(db: Session):
    logger.info(f"Getting categories list")
    return db.query(Category).filter(Category.deleted_at.is_(None)).all()

def get_category(db: Session, id: int):
    logger.info(f"Trying to get category id= {id}")

    category = db.query(Category).filter(Category.id == id, Category.deleted_at.is_(None)).first()
    if not category:
        logger.warning(f"Category with {id} does not exist or was deleted")
        raise HTTPException(status_code=404, detail="Category not found")
    return category

def update_category(db: Session, id: int, data: CategoryUpdate):
    logger.info(f"Trying to update category id={id}")    
    category = get_category(db, id)

    try:
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description

        db.commit()
        db.refresh(category)
        logger.info(f"Category updated successfully id={id}")
        return category

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating category id={id}: {e}")
        raise HTTPException(
            status_code=409, detail="Category violates a database constraint"
        )

def delete_category (db: Session, id: int): 
    logger.info(f"Trying to delete the category id={id}")

    category = get_category(db, id)
    
    if category.deleted_at is not None:
        logger.warning(f"Category id={id} already deleted at {category.deleted_at}")
        raise HTTPException(status_code=400, detail="Category already deleted")
    try:   
        """
        if not category:
            return None
        """
        category.deleted_at =datetime.now(timezone.utc)
        db.commit()
        db.refresh(category)
        logger.info(f"Category {category.id} soft deleted successfully")
        return category
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error deleting category id={id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


