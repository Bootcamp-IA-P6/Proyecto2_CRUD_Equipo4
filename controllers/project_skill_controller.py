from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from models.project_skill_model import ProjectSkill
from models.project_model import Project
from models.skill_model import Skill
from schemas import project_skill_schema as schema
from config.logging_config import get_logger

logger = get_logger("project+skills")


class ProjectSkillController:
    @staticmethod
    async def add_skill_to_project(db: Session, item: schema.ProjectSkillCreate) -> schema.ProjectSkillOut:
        logger.info(f"Trying to asign skill to project ={item.project_id}")  

        existing = db.query(ProjectSkill).filter(
            and_(ProjectSkill.project_id == item.project_id, ProjectSkill.skill_id == item.skill_id)
        ).first()
            
        if existing:
            logger.warning(f"This Project+Skill already exist (id={existing.id})")
            raise HTTPException(status_code=400, detail="Skill already added in this Project")
            
        # 2. Verificar que existen project y skill
        project = db.query(Project).filter(Project.id == item.project_id).first()
        skill = db.query(Skill).filter(Skill.id == item.skill_id).first()
            
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
            
        project_skill = ProjectSkill(**item.dict())

        try:
            db.add(project_skill)
            db.commit()
            db.refresh(project_skill)
            logger.info(f"Skill {item.skill_id} added to Project {item.project_id} successfully.")
            return schema.ProjectSkillOut.model_validate(project_skill)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error adding skill to project: {e}")
            raise HTTPException(status_code=409, detail=f"This violates a database constraint")
    

    @staticmethod
    async def get_project_skills(db: Session, project_id: int) -> ProjectSkillsListResponse:
        """Obtener TODAS las skills de UN proyecto"""
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_skills = db.query(ProjectSkill).filter(
            ProjectSkill.project_id == project_id
        ).all()
        
        skills_data = []
        for ps in project_skills:
            skills_data.append({
                "id": ps.skill.id,
                "name": ps.skill.name,
                "added_at": ps.added_at.isoformat()
            })
        
        return ProjectSkillsListResponse(
            project_id=project.id,
            project_name=project.name,
            skills=skills_data
        )



    @staticmethod
    async def remove_skill_from_project(db: Session, project_id: int, skill_id: int) -> dict:
        """Quitar UNA skill de UN proyecto"""
        
        project_skill = db.query(ProjectSkill).filter(
            and_(ProjectSkill.project_id == project_id, 
                 ProjectSkill.skill_id == skill_id)
        ).first()
        
        if not project_skill:
            raise HTTPException(
                status_code=404, 
                detail="Esta skill no está asignada a este proyecto"
            )
        
        db.delete(project_skill)
        db.commit()
        
        return {"message": "Skill removida del proyecto exitosamente"}
        