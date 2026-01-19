from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from models.skill_model import Skill
from schemas.skills_schema import SkillCreate, SkillUpdate
import logging
from datetime import datetime

logger = logging.getLogger("Skills")

def get_skills(db: Session):
    return db.query(Skill).filter(Skill.deleted_at.is_(None)).all()

def get_skill(db: Session, id: int):
    skill = db.query(Skill).filter(Skill.id == id, Skill.deleted_at.is_(None)).first()
    if not skill:
        logger.warning(f"Skill {id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

def create_skill(db: Session, data: SkillCreate):
    skill = Skill(**data.dict())
    try:
        db.add(skill)
        db.commit()
        db.refresh(skill)
        logger.info(f"Skill created: {skill.name}")
        return skill
    except IntegrityError:
        db.rollback()
        logger.warning(f"Skill {data.name} already exists")
        raise HTTPException(status_code=400, detail="Skill already exists")

def update_skill(db: Session, id: int, data: SkillUpdate):
    skill = get_skill(db, id)
    try:
        skill.name = data.name
        db.commit()
        db.refresh(skill)
        logger.info(f"Skill updated: {skill.id} -> {skill.name}")
        return skill
    except IntegrityError:
        db.rollback()
        logger.warning(f"Skill {data.name} already exists")
        raise HTTPException(status_code=400, detail="Skill already exists")

def delete_skill(db: Session, id: int):
    skill = get_skill(db, id)
    if skill.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Skill already deleted")
    skill.deleted_at = datetime.now()
    db.commit()
    db.refresh(skill)
    logger.info(f"Skill deleted: {skill.id}")
    return skill
