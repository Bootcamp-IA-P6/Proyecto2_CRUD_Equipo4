from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.volunteer_schema import (
    VolunteerCreate,
    VolunteerUpdate,
    VolunteerOut,
    VolunteerWithSkills
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
    return get_volunteer(db, id)

@router.put("/{id}", response_model=VolunteerOut)
def update(id: int, data: VolunteerUpdate, db: Session = Depends(get_db)):
    return update_volunteer(db, id, data)

@router.delete("/{id}", response_model=VolunteerOut)
def delete(id: int, db: Session = Depends(get_db)):
    return delete_volunteer(db, id)

###

@router.get("/{id}/skills", response_model=VolunteerWithSkills)
def get_volunteer_skills(id: int, db: Session = Depends(get_db)):
    return get_volunteer_with_skills(db, id)

@router.post("/{volunteer_id}/skills/{skill_id}", status_code=201)
def add_skill(volunteer_id: int, skill_id: int, db: Session = Depends(get_db)):
    return add_skill_to_volunteer(db, volunteer_id, skill_id)


@router.delete("/{volunteer_id}/skills/{skill_id}", status_code=204)
def remove_skill(volunteer_id: int, skill_id: int, db: Session = Depends(get_db)):
    remove_skill_from_volunteer(db, volunteer_id, skill_id)
    return

