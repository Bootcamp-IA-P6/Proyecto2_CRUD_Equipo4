from sqlalchemy.orm import Session
from models.category_model import Category
from schemas.category_schemas import CategoryCreate, CategoryUpdate, CategoryOut
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from config.logging_config import get_logger
from datetime import datetime, timezone

logger = get_logger("category")


def create_category(db: Session, data: CategoryCreate):
    logger.info(f"Trying to create category {data.name}")

    existing = db.query(Category).filter(Category.name == data.name, Category.deleted_at.is_(None)).first()
    if existing:
        logger.warning(f"Category {data.name} already exist with ID {existing.id})")
        raise HTTPException(status_code=400, detail="Category already exist")   #Bad Request
    
    category = Category(**data.dict())
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        logger.info(f"Category with ID {category.id} created successfully.")
        return category
    
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Error creating category '{data.name}': {e}")
        raise HTTPException(status_code=409, detail=f"Category violates a database constraint")     #Conflict


def get_categories(db: Session) -> Page[CategoryOut]:
    logger.info(f"Getting categories list")
    return paginate(db.query(Category).filter(Category.deleted_at.is_(None)))

def get_category(db: Session, id: int):
    logger.info(f"Trying to get category with ID {id}")

    category = db.query(Category).filter(Category.id == id, Category.deleted_at.is_(None)).first()
    if not category:
        logger.warning(f"Category with ID {id} not found")
        raise HTTPException(status_code=404, detail="Category not found")   #Not found
    return category

def update_category(db: Session, id: int, data: CategoryUpdate):
    logger.info(f"Trying to update category with ID {id}")    
    category = get_category(db, id)

    try:
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description

        db.commit()
        db.refresh(category)
        logger.info(f"Category with ID {id} updated successfully")
        return category

    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Integrity error updating category with ID {id}: {e}")
        raise HTTPException(
            status_code=409, detail="Category violates a database constraint")      #Conflict

def delete_category (db: Session, id: int): 
    logger.info(f"Trying to delete the category")

    category = get_category(db, id)
    
    if category.deleted_at is not None:
        logger.warning(f"{category.name} category with ID {id} already deleted at {category.deleted_at}")
        raise HTTPException(status_code=400, detail="Category already deleted")     #Bad request
    
    try:   
        category.deleted_at =datetime.now(timezone.utc)
        db.commit()
        db.refresh(category)
        logger.info(f"Category {category.id} soft deleted successfully")
        return category
    
    except Exception as e:
        db.rollback()
        logger.error(f"Integrity error deleting category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")        #Internal server error


