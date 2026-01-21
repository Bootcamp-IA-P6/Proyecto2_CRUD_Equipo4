from sqlalchemy import update
from datetime import datetime

from sqlalchemy.orm import Session
from schemas import project_schema as schema
from models.project_model import Project
from models.project_skill_model import project_skills
from models.skill_model import Skill
from controllers.skill_controller import get_skill
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from config.logging_config import get_logger

logger = get_logger("project")

class ProjectController:


    @staticmethod
    async def get_all_items(db: Session) -> list[schema.ProjectOut]:
        items = db.query(Project).all()
        return [schema.ProjectOut.model_validate(item) for item in items]

    @staticmethod
    async def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[schema.ProjectOut]:
        items = db.query(Project).offset(skip).limit(limit).all()
        return [schema.ProjectOut.model_validate(item) for item in items]

    @staticmethod
    async def get_item(db: Session, item_id: int) -> schema.ProjectOut:
        logger.info(f"Trying to get project id= {item_id}")
        item = db.query(Project).filter(Project.id == item_id, Project.deleted_at.is_(None)).first()

        if not item:
            logger.warning(f"Project with id {item_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")
        return schema.ProjectOut.model_validate(item) if item else None

    @staticmethod
    async def create_item(db: Session, item: schema.ProjectCreate)-> schema.ProjectOut:
        logger.info(f"Trying to create project for ={item.name}")
        
        existing = db.query(Project).filter(Project.name == item.name).first()

        if existing:
            logger.warning(f"Project {item.name} already exist (id={existing.id})")
            raise HTTPException(status_code=400, detail="Project already exist")

        db_item = Project(**item.dict())

        try:
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            logger.info(f"Project {item.name} created successfully.")
            return schema.ProjectOut.model_validate(db_item)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating project: {e}")
            raise HTTPException(status_code=409, detail=f"Project violates a database constraint")



    @staticmethod
    async def update_item(db: Session, item_id: int, item: schema.ProjectUpdate) -> schema.ProjectOut:
        logger.info(f"Trying to update project {item_id}")
        db_item = db.query(Project).filter(Project.id == item_id).first()

        if not db_item:
            logger.info(f"Project with ID {item_id} not found")
            raise HTTPException(status_code=404, detail="Project no found")
        
        try:     
            if item.name is not None:
                db_item.name = item.name
            if item.description is not None:
                db_item.description = item.description
            if item.deadline is not None:
                db_item.deadline = item.deadline
            if item.status is not None:
                db_item.status = item.status
            if item.priority is not None:
                db_item.priority = item.priority
                
            db.commit()
            db.refresh(db_item)
            logger.info(f"updated project: {item_id}")
            return schema.ProjectOut.model_validate(db_item)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Invalid data for project: {e}")
            raise HTTPException(status_code=400, detail="Invalid data: Error updating project")
    



    @staticmethod
    async def delete_item(db: Session, item_id: int):
        logger.info(f"trying to delete the project")
        project = db.query(Project).filter(Project.id == item_id).first()
        
        if not project:
            logger.warning(f"Project {item_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")

        if project.deleted_at is not None:
            logger.warning(f"Project id={id} already deleted at {project.deleted_at}")
            raise HTTPException(status_code=400, detail="Project already deleted")
            
        
        project.deleted_at = datetime.utcnow()
        db.commit()
        logger.info(f"Soft-deleted project id={project.id}")
        
        
        return schema.ProjectOut.model_validate(project)

    #PROJECT+SKILLS

    #add skill
    @staticmethod
    async def add_skill_to_project(db: Session, project_id: int, skill_id: int):
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        if not project:
            logger.warning(f"Project with id {project_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")

        skill = get_skill(db, skill_id)

        existing = db.execute(
            project_skills.select().where(
                project_skills.c.project_id == project_id,
                project_skills.c.skill_id == skill_id
            )
        ).first()

        if existing:
            logger.warning(f"project {project_id} already has this skill {skill_id}")
            raise HTTPException(409, "project already has this skill")
        
        project.skills.append(skill)
        db.commit()
        db.refresh(project)
        logger.info(f"Skill added to project")
        return schema.ProjectSkillsOut.model_validate(project)

    #read project+skill
    @staticmethod
    async def get_project_with_skills(db: Session, project_id: int):
    
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        if not project:
            logger.warning(f"Project with id {project_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")
        
        skills = db.query(Skill).join(project_skills).filter(
            project_skills.c.project_id == project_id,
            Skill.deleted_at.is_(None)
        ).all()
        
        
        project.skills = skills
        return schema.ProjectSkillsOut.model_validate(project)

    #remove one skill
    @staticmethod
    async def remove_skill_from_project(db: Session, project_id: int, skill_id: int):
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        if not project:
            logger.warning(f"Project with id {project_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")
            
        #verificar que el skill existe
        skill = get_skill(db, skill_id)
        
        #verificar que existe la relacion activa
        existing = db.execute(
            project_skills.select().where(
                project_skills.c.project_id == project_id,
                project_skills.c.skill_id == skill_id,
                project_skills.c.deleted_at.is_(None)
            )
        ).first()
        
        if not existing:
            logger.warning(f"Skill {skill_id} not in project {project_id}")
            raise HTTPException(404, "Skill not assigned to project")
        
        # Soft delete
        upd = (
            update(project_skills)
            .where(
                    project_skills.c.project_id == project_id,
                    project_skills.c.skill_id == skill_id,
                    project_skills.c.deleted_at.is_(None)
            )
            .values(deleted_at=datetime.utcnow())
        )

        db.execute(upd)
        db.commit()
        
        logger.info(f"Skill {skill_id} removed from project {project_id}")
        
        return schema.ProjectSkillsOut.model_validate(project)


