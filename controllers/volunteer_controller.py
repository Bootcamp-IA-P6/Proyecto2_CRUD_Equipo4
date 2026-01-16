from sqlalchemy.orm import Session
from models.volunteers_model import Volunteer
from models.users_model import User
from schemas.volunteer_schema import VolunteerCreate, VolunteerUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime



def create_volunteer(db: Session, data: VolunteerCreate):
    # Existe user
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {data.user_id} does not exist")

    volunteer = Volunteer(**data.dict())

    try:
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)
        return volunteer
    except IntegrityError:
        db.rollback() #Clean session
        raise HTTPException(status_code=409, detail=f"There is already a volunteer with user_id {data.user_id}")



def get_volunteers(db: Session):
    return db.query(Volunteer).all()


def get_volunteer(db: Session, id: int):
    print("ID recibido:", id)
    volunteer = db.query(Volunteer).filter(Volunteer.id == id).first()
    print("Resultado:", volunteer)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer


def update_volunteer(db: Session, id: int, data: VolunteerUpdate):
    volunteer = get_volunteer(db, id)
    try:
        volunteer.status = data.status
        db.commit()
        db.refresh(volunteer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")
    return volunteer


def delete_volunteer(db: Session, id: int):
    volunteer = get_volunteer(db, id)
    try:
        volunteer.status = "suspended"
        volunteer.deleted_at = datetime.utcnow()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")
    return volunteer
