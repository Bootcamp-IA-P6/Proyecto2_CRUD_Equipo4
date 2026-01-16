from sqlalchemy.orm import Session
from models.category_model import Category
from schemas.category_schemas import CategoryCreate


def create_category(db: Session, data: CategoryCreate):
    category = Category(**data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session):
    return db.query(Category).all()

def get_category(db: Session, id: int):
    return db.query(Category).filter(Category.id == id).first()

def update_category(db: Session, id: int, data: CategoryCreate):
    category = get_category(db, id)

    if not category:
        return None

    category.name = data.name
    category.description = data.description
    db.commit()
    db.refresh(category)

    return category

def delete_category(db: Session, id: int):
    category = get_category(db, id)

    if not category:
        return None

    db.delete(category)
    db.commit()
    return category

