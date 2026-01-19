from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from controllers.skill_controller import get_skills, get_skill, create_skill, update_skill, delete_skill
from schemas.skills_schema import SkillCreate, SkillUpdate, SkillOut
from typing import List

skill_router = APIRouter(prefix="/skills", tags=["Skills"])

@skill_router.get("/", response_model=List[SkillOut])
def read_skills(db: Session = Depends(get_db)):
    return get_skills(db)

@skill_router.get("/{id}", response_model=SkillOut)
def read_skill(id: int, db: Session = Depends(get_db)):
    return get_skill(db, id)

@skill_router.post("/", response_model=SkillOut, status_code=201)
def add_skill(data: SkillCreate, db: Session = Depends(get_db)):
    return create_skill(db, data)

@skill_router.put("/{id}", response_model=SkillOut)
def modify_skill(id: int, data: SkillUpdate, db: Session = Depends(get_db)):
    return update_skill(db, id, data)

@skill_router.delete("/{id}", response_model=SkillOut)
def remove_skill(id: int, db: Session = Depends(get_db)):
    return delete_skill(db, id)
