from sqlalchemy.orm import Session
from models.volunteers_model import Volunteer
from models.users_model import User
from models.skill_model import Skill
from schemas.volunteer_schema import VolunteerCreate, VolunteerUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
from domain.volunteer_enum import VolunteerStatus
from config.logging_config import get_logger

logger = get_logger("volunteers")


def create_volunteer(db: Session, data: VolunteerCreate):
    logger.info(f"Trying to create volunteer for user_id={data.user_id}")
    # Existe user
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        logger.warning(f"User with id {data.user_id} does not exist")
        raise HTTPException(status_code=404, detail=f"User with id {data.user_id} does not exist")

    volunteer = Volunteer(**data.dict()) #construcción del objeto ORM

    try:
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)
        logger.info(f"Volunteer with ID {volunteer.id} created successfully.")
        return volunteer
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating volunteer: {e}")
        raise HTTPException(status_code=409, detail=f"Volunteer violates a database constraint")


def get_volunteers(db: Session):
    logger.info(f"Getting volunteers list")
    return db.query(Volunteer).all()


def get_volunteer(db: Session, id: int):
    logger.info(f"Trying to get volunteer id= {id}")

    #print("ID recibido:", id)
    volunteer = db.query(Volunteer).filter(Volunteer.id == id,  Volunteer.deleted_at.is_(None)).first()
    #print("Resultado:", volunteer)
    if not volunteer:
        logger.warning(f"Volunteer with id {id} not found")
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer


def update_volunteer(db: Session, id: int, data: VolunteerUpdate):
    logger.info(f"changing the volunteer's status")
    volunteer = get_volunteer(db, id)

    if not volunteer:
        raise HTTPException(status_code=404,detail="Volunteer not found")    
    try:
        volunteer.status = data.status
        db.commit()
        db.refresh(volunteer)
        logger.info(f"updated volunteer: {volunteer.id} status={volunteer.status}")
        return volunteer
    except ValueError as e:
        db.rollback()
        logger.error(f"Invalid status for volunteer {volunteer.id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid volunteer data")    


def delete_volunteer(db: Session, id: int):
    logger.info(f"trying to delete the volunteer")
    volunteer = get_volunteer(db, id)
    
    if not volunteer:
        logger.warning(f"Volunteer id={id} not found")
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    if volunteer.deleted_at is not None:
        logger.warning(f"Volunteer id={id} already deleted at {volunteer.deleted_at}")
        raise HTTPException(status_code=400, detail="Volunteer already deleted")
    
    volunteer.status = VolunteerStatus.suspended
    volunteer.deleted_at = datetime.utcnow()
    db.commit()
    logger.info(f"Soft-deleted volunteer id={volunteer.id}, status={volunteer.status}")
    return volunteer

####

def get_volunteer_with_skills(db: Session, id: int):
    volunteer = (db.query(Volunteer).options(joinedload(Volunteer.skills)).filter(Volunteer.id == id).first())
    
    if not volunteer:
        logger.warning(f"Volunteer with id {id} not found")
        raise HTTPException(404, "Volunteer not found")
    return volunteer


def add_skill_to_volunteer(db: Session, volunteer_id: int, skill_id: int):
    volunteer = get_volunteer(db, volunteer_id)
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        logger.warning(f"Skill with id {skill_id} not found")
        raise HTTPException(400, "Invalid skill_id")
    
    if skill in volunteer.skills:
        logger.warning(f"Volunteer already has this skill")
        raise HTTPException(409, "Volunteer already has this skill")
    
    volunteer.skills.append(skill)
    db.commit()
    logger.info(f"Skill added to the volunteer")
    return volunteer