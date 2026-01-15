from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.volunteer_schema import (
    VolunteerCreate,
    VolunteerUpdate,
    VolunteerOut
)
from controllers.volunteer_controller import *

router = APIRouter(
    prefix="/volunteers",
    tags=["Volunteers"]
)

@router.post("/", response_model=VolunteerOut)
def create(volunteer: VolunteerCreate, db: Session = Depends(get_db)):
    return create_volunteer(db, volunteer)

@router.get("/", response_model=list[VolunteerOut])
def list_all(db: Session = Depends(get_db)):
    return get_volunteers(db)

@router.get("/{id}", response_model=VolunteerOut)
def get_one(id: int, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer

@router.put("/{id}", response_model=VolunteerOut)
def update(id: int, data: VolunteerUpdate, db: Session = Depends(get_db)):
    volunteer = update_volunteer(db, id, data)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer

@router.delete("/{id}", response_model=VolunteerOut)
def delete(id: int, db: Session = Depends(get_db)):
    volunteer = delete_volunteer(db, id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer
