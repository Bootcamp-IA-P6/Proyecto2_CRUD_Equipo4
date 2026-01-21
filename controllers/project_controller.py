import datetime
from sqlalchemy import select, update
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
            logger.warning(f"Project with id {project_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")
        return schema.ProjectOut.model_validate(project) if project else None

    
    #CREATE PROJECT
    @staticmethod
    async def create_project(db: Session, project: schema.ProjectCreate)-> schema.ProjectOut:
        logger.info(f"Trying to create project for ={project.name}")
        
        existing = db.query(Project).filter(Project.name == project.name).first()

        if existing:
            logger.warning(f"Project {project.name} already exist (id={existing.id})")
            raise HTTPException(status_code=400, detail="Project already exist")

        db_project = Project(**project.dict())

        try:
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            logger.info(f"Project {project.name} created successfully.")
            return schema.ProjectOut.model_validate(db_project)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating project: {e}")
            raise HTTPException(status_code=409, detail=f"Project violates a database constraint")



    @staticmethod
    async def update_project(db: Session, project_id: int, project: schema.ProjectUpdate) -> schema.ProjectOut:
        logger.info(f"Trying to update project {project_id}")
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            logger.info(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project no found")
        
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
            logger.info(f"updated project: {project_id}")
            return schema.ProjectOut.model_validate(db_project)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Invalid data for project: {e}")
            raise HTTPException(status_code=400, detail="Invalid data: Error updating project")
    



    @staticmethod
    async def delete_project(db: Session, project_id: int):
        logger.info(f"trying to delete the project")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            logger.warning(f"Project {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")

        if project.deleted_at is not None:
            logger.warning(f"Project id={id} already deleted at {project.deleted_at}")
            raise HTTPException(status_code=400, detail="Project already deleted")
            
        
        project.deleted_at = datetime.utcnow()
        db.commit()
        logger.info(f"Soft-deleted project id={project.id}")
        
        
        return schema.ProjectOut.model_validate(project)


    ###PROJECT+SKILLS###

    #add skill
    @staticmethod
    async def add_skill_to_project(db: Session, project_id: int, skill_id: int):
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        if not project:
            logger.warning(f"Project with id {project_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")

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
                raise HTTPException(status_code=409, detail="project already has this skill")
        else:
        
            db.execute(
                insert(project_skills).values(
                    project_id=project_id,
                    skill_id=skill_id,
                    deleted_at=None
                )
            )
            logger.info(f"Skill {skill_id} added to project {project_id}")
    
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

    #remove all skills from project
    @staticmethod
    async def remove_all_skills_from_project(db: Session, project_id: int):
    
        project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
        
        if not project:
            logger.warning(f"Project with id {project_id} does not exist")
            raise HTTPException(status_code=404, detail="Project not found")
        
        
        update_stmt = update(project_skills).where(
            project_skills.c.project_id == project_id,
            project_skills.c.deleted_at.is_(None)
        ).values(deleted_at=datetime.utcnow())
        
        try:
            db.execute(update_stmt)
            db.commit()
            
            db.refresh(project)
            project.skills = []
            
            logger.info(f"All skills soft-deleted for project {project_id}")
            return schema.ProjectSkillsOut.model_validate(project)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error soft-deleting all skills: {e}")
            raise HTTPException(status_code=500, detail="Error soft-deleting all skills")


