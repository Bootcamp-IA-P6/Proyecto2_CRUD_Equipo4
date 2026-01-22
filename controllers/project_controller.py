import datetime
from sqlalchemy import select, update, insert
from sqlalchemy.orm import Session
from schemas import project_schema as schema
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from config.logging_config import get_logger

from models.project_model import Project
from models.project_skill_model import project_skills
from models.skill_model import Skill
from controllers.skill_controller import get_skill

logger = get_logger("project")

class ProjectController:

    #READ ALL PROJECTS
    @staticmethod
    async def get_projects(db: Session, skip: int = 0, limit: int = 100) -> list[schema.ProjectOut]:
        logger.info(f"Trying to get all projects")
        projects = db.query(Project).filter(Project.deleted_at.is_(None)).offset(skip).limit(limit).all()
        return [schema.ProjectOut.model_validate(project) for project in projects]
    
    
    #READ ONE PROJECT
    @staticmethod
    async def get_project(db: Session, project_id: int) -> schema.ProjectOut:
        logger.info(f"Trying to get project id= {project_id}")
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()

        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found") #not found
        return schema.ProjectOut.model_validate(project) if project else None

    
    #CREATE PROJECT
    @staticmethod
    async def create_project(db: Session, project: schema.ProjectCreate)-> schema.ProjectOut:
        logger.info(f"Trying to create project for ={project.name}")
        
        existing = db.query(Project).filter(Project.name == project.name).first()

        if existing:
            logger.warning(f"Project {project.name} already exist with ID {existing.id})")
            raise HTTPException(status_code=409, detail="Project already exist")

        db_project = Project(**project.dict())

        try:
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            logger.info(f"Project {project.name} created successfully.")
            return schema.ProjectOut.model_validate(db_project)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Project already exist: {e}")
            raise HTTPException(status_code=409, detail=f"Project already exist")   #conflict
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating project: {e}")
            raise HTTPException(status_code=500, detail="Error creating project")   #Internal server error



    @staticmethod
    async def update_project(db: Session, project_id: int, project: schema.ProjectUpdate) -> schema.ProjectOut:
        logger.info(f"Trying to update project {project_id}")
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            logger.info(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project no found") #Not found
        
        try:     
            if project.name is not None:
                db_project.name = project.name
            if project.description is not None:
                db_project.description = project.description
            if project.deadline is not None:
                db_project.deadline = project.deadline
            if project.status is not None:
                db_project.status = project.status
            if project.priority is not None:
                db_project.priority = project.priority
                
            db.commit()
            db.refresh(db_project)
            logger.info(f"{db_project.name} projects has been updated with ID {project_id}")
            return schema.ProjectOut.model_validate(db_project)
            
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=400, detail="Project not found")    #Not found
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating project: {e}")
            raise HTTPException(status_code=500, detail="Error updating project")   #Internal server error


    @staticmethod
    async def delete_project(db: Session, project_id: int):
        logger.info(f"trying to delete the project")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")

        if project.deleted_at is not None:
            logger.warning(f"Project {project_id} already deleted at {project.deleted_at}")
            raise HTTPException(status_code=400, detail="Project already deleted")      #Bad request
        
        project.deleted_at = datetime.utcnow()
        db.commit()
        logger.info(f"Soft-deleted for project with ID {project.id}")
        
        return schema.ProjectOut.model_validate(project)


    ###PROJECT+SKILLS###

    #add skill
    @staticmethod
    async def add_skill_to_project(db: Session, project_id: int, skill_id: int):
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")    #Not found

        skill = get_skill(db, skill_id)

        existing_relation = db.execute(
            select(project_skills)
            .where(
                project_skills.c.project_id == project_id,
                project_skills.c.skill_id == skill_id
            )
        ).first()

        if existing_relation:
            #reactivar la relacion
            if existing_relation.deleted_at is not None:
                db.execute(
                    update(project_skills)
                    .where(
                        project_skills.c.project_id == project_id,
                        project_skills.c.skill_id == skill_id
                    )
                    .values(deleted_at=None)
                )
                logger.info(f"Skill {skill_id} reactivated for project {project_id}")
            else:
                # Si ya está activa, error de duplicado
                logger.warning(f"Project already has this skill")
                raise HTTPException(status_code=409, detail="project already has this skill")   #Bad Request
        else:
        
            db.execute(
                insert(project_skills).values(
                    project_id=project_id,
                    skill_id=skill_id,
                    deleted_at=None
                )
            )
            logger.info(f"Skill {skill_id}:{skill.name} added to {project.name} project")
    
        db.commit()
        db.refresh(project)
        logger.info(f"Skill added to project successfully")
        return schema.ProjectSkillsOut.model_validate(project)


    #read project+skill
    @staticmethod
    async def get_project_with_skills(db: Session, project_id: int):
    
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")    #Not found
        
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
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")    #Not found
            
        #verificar que el skill existe
        get_skill(db, skill_id)
        
        #verificar que existe la relacion activa
        existing = db.execute(
            project_skills.select().where(
                project_skills.c.project_id == project_id,
                project_skills.c.skill_id == skill_id,
                project_skills.c.deleted_at.is_(None)
            )
        ).first()
        
        if not existing:
            logger.warning(f"Skill {skill_id} not assigned to project {project_id}")
            raise HTTPException(404, "Skill not assigned to project")       #Not found
        
        try:
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
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error removing skill from project: {e}")
            raise HTTPException(status_code=500, detail="Error removing skill from project")    #Internal server error
        


    #remove all skills from project
    @staticmethod
    async def remove_all_skills_from_project(db: Session, project_id: int):
    
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        
        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")   #Not found
        
        

        try:

            update_stmt = update(project_skills).where(
                                project_skills.c.project_id == project_id,
                                project_skills.c.deleted_at.is_(None)
                                    ).values(deleted_at=datetime.utcnow())
        
            db.execute(update_stmt)
            db.commit()
            db.refresh(project)
            project.skills = []
            
            logger.info(f"All skills soft-deleted for project {project_id}")
            return schema.ProjectSkillsOut.model_validate(project)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error soft-deleting all skills: {e}")
            raise HTTPException(status_code=500, detail="Error soft-deleting all skills")   #Internal server error


