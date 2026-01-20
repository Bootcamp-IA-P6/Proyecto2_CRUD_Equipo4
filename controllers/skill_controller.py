from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
from config.logging_config import get_logger

from models.skill_model import Skill
from schemas.skills_schema import SkillCreate, SkillUpdate

logger = get_logger("Skills")

#Get all skills
def get_skills(db: Session):
    logger.info(f"Getting skills list")
    return db.query(Skill).filter(Skill.deleted_at.is_(None)).all()

#Get skill by ID
def get_skill(db: Session, id: int):
    logger.info(f"Trying to get skill {id}")
    skill = db.query(Skill).filter(Skill.id == id, Skill.deleted_at.is_(None)).first()

    if not skill:
        logger.warning(f"Skill {id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")  #Not found
    return skill

#Create Skill
def create_skill(db: Session, data: SkillCreate):
    logger.info(f"Trying to create Skill: {data.name}")
    skill = Skill(**data.dict())

    try:
        db.add(skill)
        db.commit()
        db.refresh(skill)
        logger.info(f"Skill {skill.name} created")
        return skill
    
    except IntegrityError:
        db.rollback()
        logger.warning(f"Skill {data.name} already exists")
        raise HTTPException(status_code=409, detail="Skill already exists")     #Conflict

#Update Skill
def update_skill(db: Session, id: int, data: SkillUpdate):
    logger.info(f"Trying to update skill")
    skill = get_skill(db, id)

    try:
        skill.name = data.name
        db.commit()
        db.refresh(skill)
        logger.info(f"Skill updated: {skill.id} -> {skill.name}") #Comprobar relación....
        return skill
    
    except IntegrityError:
        db.rollback()
        logger.warning(f"Skill {data.name} already exists")
        raise HTTPException(status_code=409, detail="Skill already exists")     #Conflict

#Remove Skill
def delete_skill(db: Session, id: int):
    logger.info(f"Trying to delete skill")
    skill = get_skill(db, id)

    if skill.deleted_at is not None:
        logger.warning(f"Skill already deleted")
        raise HTTPException(status_code=400, detail="Skill already deleted")    #Bad request
    
    skill.deleted_at = datetime.now()
    db.commit()
    db.refresh(skill)
    logger.info(f"Skill deleted: {skill.id}")
    return skill
