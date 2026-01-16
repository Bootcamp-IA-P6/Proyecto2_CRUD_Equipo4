from sqlalchemy.orm import Session
from models.volunteers_model import Volunteer
from models.users_model import User
from schemas.volunteer_schema import VolunteerCreate, VolunteerUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
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
    except IntegrityError:
        db.rollback() #Clean session
        logger.error(f"There is already a volunteer with user_id {data.user_id}")
        raise HTTPException(status_code=409, detail=f"There is already a volunteer with user_id {data.user_id}")



def get_volunteers(db: Session):
    return db.query(Volunteer).all()


def get_volunteer(db: Session, id: int):
    print("ID recibido:", id)
    volunteer = db.query(Volunteer).filter(Volunteer.id == id).first()
    print("Resultado:", volunteer)
    if not volunteer:
        logger.warning(f"User with id {id} does not exist")
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer


def update_volunteer(db: Session, id: int, data: VolunteerUpdate):
    volunteer = get_volunteer(db, id)
    try:
        volunteer.status = data.status
        db.commit()
        db.refresh(volunteer)
        logger.info(f"updated volunteer: {id} status={volunteer.status}")
        return volunteer
    except IntegrityError:
        db.rollback()
        logger.error(f"Invalid data: Error updating volunteer")
        raise HTTPException(status_code=400, detail="Invalid data: Error updating volunteer")
    


def delete_volunteer(db: Session, id: int):
    volunteer = get_volunteer(db, id)
    try:
        volunteer.status = "suspended"
        volunteer.deleted_at = datetime.utcnow()
        db.commit()
        logger.info(f"Eliminated volunteer: {id} status={volunteer.status}")
        return volunteer
    except IntegrityError:
        db.rollback()
        logger.error(f"Invalid data: Error deleting volunteer")
        raise HTTPException(status_code=400, detail="Invalid data: Error deleting volunteer")
