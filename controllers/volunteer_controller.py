from sqlalchemy.orm import Session
from models.volunteers_model import Volunteer
from models.users_model import User
from models.skill_model import Skill
from models.volunteer_skill_model import volunteer_skills
from schemas.volunteer_schema import VolunteerCreate, VolunteerUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
from domain.volunteer_enum import VolunteerStatus
from config.logging_config import get_logger
from sqlalchemy import select, update, join, and_


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

def get_volunteer_with_skills(db: Session, volunteer_id: int):
    # Traer el volunteer
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        logger.warning(f"Volunteer with id {volunteer_id} not found")
        raise HTTPException(404, "Volunteer not found")

    # Traer skills activas usando join con tabla intermedia
    stmt = (
        select(Skill)
        .select_from(
            join(Skill, volunteer_skills, Skill.id == volunteer_skills.c.skill_id)
        )
        .where(
            volunteer_skills.c.volunteer_id == volunteer_id,
            volunteer_skills.c.deleted_at.is_(None)
        )
    )
    skills = db.execute(stmt).scalars().all()

    # Asignar skills manualmente para usar en el schema
    volunteer.skills = skills
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

def remove_skill_from_volunteer(db: Session, volunteer_id: int, skill_id: int):
    logger.info(f"Removing skill {skill_id} from volunteer {volunteer_id}")

    stmt = select(volunteer_skills).where(
    volunteer_skills.c.volunteer_id == volunteer_id,
    volunteer_skills.c.skill_id == skill_id)

    skill = db.execute(stmt).first()

    #skill = db.query(volunteer_skills).filter(volunteer_skills.volunteer_id == volunteer_id, volunteer_skills.skill_id, volunteer_skills.deleted_at.is_(None)).first()

    if not skill:
        logger.warning(f"VolunteerSkill not found for volunteer_id={volunteer_id} and skill_id={skill_id}")
        raise HTTPException(status_code=404, detail="Skill not assigned to volunteer")
    
    upd = (
        update(volunteer_skills)
        .where(
            and_(
            volunteer_skills.c.volunteer_id == volunteer_id,
            volunteer_skills.c.skill_id == skill_id,
            volunteer_skills.c.deleted_at.is_(None)
            )
        )
        .values(deleted_at=datetime.utcnow())
    )
    
    try:
        db.execute(upd)
        db.commit()
        logger.info(f"Skill {skill_id} soft-deleted for volunteer {volunteer_id}")
        return skill
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing skill: {e}")
        raise HTTPException(status_code=500, detail="Error removing skill")