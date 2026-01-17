from sqlalchemy.orm import Session
from models.volunteers_model import Volunteer
from models.users_model import User
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

    volunteer = Volunteer(**data.dict())

    try:
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)
        logger.info(f"Volunteer created with id={volunteer.id}")
        return volunteer
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating volunteer: {e}")
        raise HTTPException(status_code=409, detail=f"Volunteer violates a database constraint")


def get_volunteers(db: Session):
    return db.query(Volunteer).all()


def get_volunteer(db: Session, id: int):
    #print("ID recibido:", id)
    volunteer = db.query(Volunteer).filter(Volunteer.id == id,  Volunteer.deleted_at.is_(None)).first()
    #print("Resultado:", volunteer)
    if not volunteer:
        logger.warning(f"Volunteer with id {id} not found")
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer


def update_volunteer(db: Session, id: int, data: VolunteerUpdate):
    volunteer = get_volunteer(db, id)
    if not volunteer:
        raise HTTPException(status_code=404,detail="Volunteer not found")    
    try:
        volunteer.status = data.status
        db.commit()
        db.refresh(volunteer)
        logger.info(f"updated volunteer: {id} status={volunteer.status}")
        return volunteer
    except ValueError as e:
        db.rollback()
        logger.error(f"Invalid status for volunteer {id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid volunteer data")    


def delete_volunteer(db: Session, id: int):
    volunteer = get_volunteer(db, id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    if volunteer.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Volunteer already deleted")
    
    volunteer.status = VolunteerStatus.suspended
    volunteer.deleted_at = datetime.utcnow()
    db.commit()
    logger.info(f"Soft-deleted volunteer id={id}, status={volunteer.status}")
    return volunteer