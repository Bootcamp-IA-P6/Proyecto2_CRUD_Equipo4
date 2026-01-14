from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from typing import List

from controllers.project_controller import ProjectController
from schemas import project_schema
from database.database import get_db

router = APIRouter()

@router.post("/items/", response_model=project_schema.ProjectBase)
async def new_item(item: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    item = await ProjectController.create_item(db, item)
    return item

@router.get("/items/{item_id}", response_model=project_schema.ProjectBase)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = ProjectController.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# Obtener lista de items
@router.get("/items/", response_model=List[project_schema.ProjectBase])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = ProjectController.get_items(db, skip=skip, limit=limit)
    return items

# Actualizar un item
@router.put("/items/{item_id}", response_model=project_schema.ProjectBase)
def update_item(item_id: int, item: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    db_item = ProjectController.update_item(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# Borrar un item
@router.delete("/items/{item_id}", response_model=project_schema.ProjectBase)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = ProjectController.delete_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item