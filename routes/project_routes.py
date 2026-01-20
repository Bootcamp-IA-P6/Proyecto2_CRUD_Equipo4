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

#CREATE PROJECT
@project_router.post("/", response_model=project_schema.ProjectOut)
async def new_project(item: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    return await ProjectController.create_item(db, item)
    
#READ PROJECT
@project_router.get("/{item_id}", response_model=project_schema.ProjectOut)
async def read_project(item_id: int, db: Session = Depends(get_db)):
    return await ProjectController.get_item(db, item_id=item_id)

#READ ALL PROJECTS
@project_router.get("/", response_model=List[project_schema.ProjectOut])
async def read_all_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await ProjectController.get_items(db, skip=skip, limit=limit)

#UPDATE PROJECT
@project_router.put("/{item_id}", response_model=project_schema.ProjectOut)
async def update_project(item_id: int, item: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    return await ProjectController.update_item(db, item_id, item)
    

# SOFT-DELETE PROJECT
@project_router.delete("/{item_id}", response_model=project_schema.ProjectOut)
async def delete_project(item_id: int, db: Session = Depends(get_db)):
    return await ProjectController.delete_item(db, item_id)



#### ENDPOINTS DE PROJECT_SKILLS ####

#READ PROJECT + SKILLS
@project_router.get("/{id}/skills", response_model=project_schema.ProjectSkillsOut)
async def get_skills(id: int, db: Session = Depends(get_db)):
    return await ProjectController.get_project_with_skills(db, id)

#ADD SKILL TO PROJECT
@project_router.post("/{id}/skills/{skill_id}", response_model=project_schema.ProjectSkillsOut)
async def add_skill(id: int, skill_id: int, db: Session = Depends(get_db)):
    return await ProjectController.add_skill_to_project(db, id, skill_id)

#DELETE SKILL FROM PROJECT
@project_router.delete("/{id}/skills/{skill_id}")
async def remove_skill(id: int, skill_id: int, db: Session = Depends(get_db)):
    return await ProjectController.remove_skill_from_project(db, id, skill_id)

#DELETE ALL SKILLS FROM PROJECT
@project_router.delete("/{id}/skills", response_model=project_schema.ProjectSkillsOut)
async def remove_all_skills(id: int, db: Session = Depends(get_db)):
    return await ProjectController.remove_all_skills_from_project(db, id)