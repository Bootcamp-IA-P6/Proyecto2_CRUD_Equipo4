from sqlalchemy.orm import Session
from models.volunteers_model import Volunteer
from schemas.volunteer_schema import VolunteerCreate, VolunteerUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime



def create_volunteer(db: Session, data: VolunteerCreate):
    volunteer = Volunteer(**data.dict())
    try:
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)
        return volunteer
    except IntegrityError:
        db.rollback() #Clean session
        raise HTTPException(status_code=400, detail=f"There is already a volunteer with user_id {data.user_id}")



def get_volunteers(db: Session):
    return db.query(Volunteer).all()


def get_volunteer(db: Session, id: int):
    return db.query(Volunteer).filter(Volunteer.id == id).first()


def update_volunteer(db: Session, id: int, data: VolunteerUpdate):
    volunteer = get_volunteer(db, id)
    if not volunteer:
        return None

    volunteer.status = data.status
    db.commit()
    db.refresh(volunteer)
    return volunteer


def delete_volunteer(db: Session, id: int):
    volunteer = get_volunteer(db, id)
    if not volunteer:
        return None

    volunteer.status = "suspended"
    volunteer.deleted_at = datetime.utcnow()
    db.commit()
    return volunteer
