from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.category_schemas import (
    CategoryCreate,
    CategoryOut
)
from controllers.category_controller import *


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=CategoryOut)
def create(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, category)

@router.get("/", response_model=list[CategoryOut])
def list_all(db: Session = Depends(get_db)):
    return get_categories(db)

@router.get("/{id}", response_model=CategoryOut)
def get_one(id: int, db: Session = Depends(get_db)):
    category = get_category(db, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{id}", response_model=CategoryOut)
def update(id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    category = update_category(db, id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{id}", response_model=CategoryOut)
def delete(id: int, db: Session = Depends(get_db)):
    category = delete_category(db, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category