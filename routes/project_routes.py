from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from typing import List

from controllers.project_controller import ProjectController
from schemas import project_schema
from database.database import get_db

project_router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@project_router.post("/items/", response_model=project_schema.ProjectOut)
async def new_item(item: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    return await ProjectController.create_item(db, item)
    

@project_router.get("/items/{item_id}", response_model=project_schema.ProjectOut)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    return await ProjectController.get_item(db, item_id=item_id)

# Obtener lista de items
@project_router.get("/items/", response_model=List[project_schema.ProjectOut])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await ProjectController.get_items(db, skip=skip, limit=limit)

# Actualizar un item
@project_router.put("/items/{item_id}", response_model=project_schema.ProjectOut)
async def update_item(item_id: int, item: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    return await ProjectController.update_item(db, item_id, item)
    

# Borrar un item
@project_router.delete("/items/{item_id}", response_model=project_schema.ProjectOut)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    return await ProjectController.delete_item(db, item_id)