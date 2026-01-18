from sqlalchemy.orm import Session
from models.category_model import Category
from schemas.category_schemas import CategoryCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from config.logging_config import get_logger

logger = get_logger("category")


def create_category(db: Session, data: CategoryCreate):
    logger.info(f"Trying to create category with name {data.name}")

    existing = db.query(Category).filter(Category.name == data.name).first()
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
    return db.query(Category).all()

def get_category(db: Session, id: int):
    logger.info(f"Trying to get category id= {id}")

    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        logger.warning(f"Category with {id} does not exist")
        raise HTTPException(status_code=404, detail="Category not found")
    return category

def update_category(db: Session, id: int, data: CategoryCreate): # comprobar porque usa create en lugar de update
    logger.info(f"Trying to update category id={id}")    
    category = get_category(db, id)

    if not category:
        logger.warning(f"Category id={id} not found")
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        category.name = data.name
        category.description = data.description
        db.commit()
        db.refresh(category)
        logger.info(f"Category updated successfully id={id}")
        return category
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating category id={id}: {e}")
        raise HTTPException(status_code=409, detail="Category violates a database constraint")

def delete_category(db: Session, id: int): # no tiene sof-deleted
    logger.info(f"trying to delete the category")

    category = get_category(db, id)
    if not category:
        logger.warning(f"Category id={id} not found")
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.deleted_at is not None:
        logger.warning(f"Category id={id} already deleted at {category.deleted_at}")
        raise HTTPException(status_code=400, detail="Category already deleted")
    try:   
        """
        if not category:
            return None
        """
        db.delete(category)
        db.commit()
        logger.info(f"Category {category.id} deleted successfully")
        return category
    except IntegrityError:
        db.rollback()
        logger.error(f"Category with {id} does not exist")
        raise HTTPException(status_code=404, detail="Category not found")


