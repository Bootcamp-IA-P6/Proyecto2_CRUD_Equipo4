from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime


from models.assignment_model import Assignment
from models.project_skill_model import ProjectSkill
from models.volunteer_skill_model import volunteer_skills
from models.project_model import Project
from domain.projects_enums import ProjectStatus
from schemas import assignment_schema
from domain.assignment_enum import AssignmentStatus
from config.logging_config import get_logger


logger = get_logger("assignments")


class AssignmentController:
    
    @staticmethod
    def assign_volunteer(db: Session, data: assignment_schema.AssignmentCreate):
        """
        Asigna un voluntario a un proyecto validando:
        - Que el project_skill exista
        - Que el volunteer_skill exista
        - Que ambos tengan la misma skill
        - Que no exista una asignación duplicada activa
        """
        logger.info(f"Creating assignment for project_skill_id={data.project_skill_id} and volunteer_skill_id={data.volunteer_skill_id}")
        
        try:
            #Validar project skill
            project_skill = db.query(ProjectSkill).filter(
                ProjectSkill.id == data.project_skill_id,
                ProjectSkill.deleted_at.is_(None)
            ).first()
            
            if not project_skill:
                logger.warning(f"Project skill with id={data.project_skill_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Project skill not found"
                )
                
            #Validar volunteer skill
            volunteer_skill = db.execute(
                volunteer_skills.select().where(
                    volunteer_skills.c.id == data.volunteer_skill_id,
                    volunteer_skills.c.deleted_at.is_(None)
                )
            ).first()
            
            if not volunteer_skill:
                logger.warning(f"Volunteer skill with id={data.volunteer_skill_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Volunteer skill not found"
                )
                
            #validar que coincidan las skill
            if project_skill.skill_id != volunteer_skill.skill_id:
                logger.warning(f"Skills do not match between project {project_skill.skill_id} and volunteer {volunteer_skill.skill_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Volunteer skill does not match project skill"
                )
            
            #Prevenir duplicacion 
            existing_assignment = db.query(Assignment).filter(
                Assignment.project_skill_id == data.project_skill_id,
                Assignment.volunteer_skill_id == data.volunteer_skill_id,
                Assignment.deleted_at.is_(None),
                Assignment.status.in_([
                    AssignmentStatus.pending,
                    AssignmentStatus.accepted
                ])
            ).first()
            
            if existing_assignment:
                logger.warning(f"Assignment already exists for project_skill_id={data.project_skill_id} and volunteer_skill_id={data.volunteer_skill_id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Assignment already exists for this project and volunteer"
                )
                
            #crear assignment
            assignment = Assignment(
                project_skill_id=data.project_skill_id,
                volunteer_skill_id=data.volunteer_skill_id,
                status = AssignmentStatus.pending
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            
            logger.info(f"Assignment created successfully with id={assignment.id}")
            return assignment
        
        except HTTPException:
            db.rollback()
            raise
        
        except IntegrityError as e:
            db.rollback()
            logger.exception(f"Integrity error creating assignment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error creating assignment")
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creating assignment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error creating assignment")
    
    @staticmethod
    def update_status(
        db: Session, 
        assignment_id: int, 
        new_status: AssignmentStatus
    ):
        """
        Actualiza el estado de una asignación y automáticamente
        actualiza el estado del proyecto asociado:
        - accepted -> proyecto pasa a 'assigned'
        - completed (todas) -> proyecto pasa a 'completed'
        """
        logger.info(f"Updating assignment status to {new_status}")
        
        try: 
            #buscar assignment
            assignment = db.query(Assignment).filter(
                Assignment.id == assignment_id,
                Assignment.deleted_at.is_(None)
            ).first()
            
            if not assignment:
                logger.warning(f"Assignment with id={assignment_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Assignment not found"
                )
                
            #validar transiciones de estado
            if assignment.status == AssignmentStatus.completed:
                logger.warning("Attempt to modify completed assignment")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Completed assignment cannot be modified"
                )
            
            #actualizar estado de la asignacion
            old_status = assignment.status
            assignment.status = new_status
            
            #actualizar estado del proyecto basado en el cambio
            project_skill = db.query(ProjectSkill).filter(
                ProjectSkill.id == assignment.project_skill_id,
                ProjectSkill.deleted_at.is_(None)
            ).first()
            
            if project_skill:
                project = db.query(Project).filter(
                    Project.id == project_skill.project_id,
                    Project.deleted_at.is_(None)
                ).first()
                
                if project:
                    #si la asignacion fue aceptada, maracar proyecto como 'assigned'
                    if new_status == AssignmentStatus.accepted and old_status != AssignmentStatus.accepted:
                        project.status = ProjectStatus.assigned
                        logger.info(f"Project {project.id} status updated to assigned")
                        
                    #si todas las asignaciones estan completadas, marcar proyecto como 'completed'
                    if new_status == AssignmentStatus.completed:
                        # Verificar si hay asignaciones NO completadas para este proyecto
                        incomplete_assignments= db.query(Assignment).join(ProjectSkill).filter(
                            ProjectSkill.project_id == project.id,
                            Assignment.deleted_at.is_(None),
                            Assignment.status == AssignmentStatus.completed
                        ).count() 
                        
                        if incomplete_assignments == 0:
                            project.status = ProjectStatus.completed
                            logger.info(f"Project {project.id} status updated to completed")
                
            db.commit()
            db.refresh(assignment)
            
            logger.info(f"Assignment status updated to {new_status}")
            return assignment
        
        except HTTPException:
            db.rollback()
            raise
        
        except IntegrityError as e:
            db.rollback()
            logger.exception(f"Integrity error updating assignment status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Database integrity error updating assignment status"
                )
            
        except HTTPException as e:
            db.rollback()
            logger.exception(f"Error updating assignment status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error updating assignment status"
            )
            
    @staticmethod
    def get_assignments_by_volunteer(db: Session, volunteer_id: int):
        """Obtiene todas las asignaciones de un voluntario"""
        logger.info(f"Getting assignments for volunteer {volunteer_id}")
        
        try:
            # Buscar volunteer_skill_ids del voluntario
            volunteer_skill_ids = db.execute(
                volunteer_skills.select().where(
                    volunteer_skills.c.volunteer_id == volunteer_id,
                    volunteer_skills.c.deleted_at.is_(None)
                )
            ).fetchall()
            
            volunteer_skill_ids = [vs.id for vs in volunteer_skill_ids]
            
            if not volunteer_skill_ids:
                return []
            
            assignments = db.query(Assignment).filter(
                Assignment.volunteer_skill_id.in_(volunteer_skill_ids),
                Assignment.deleted_at.is_(None)
            ).all()
            
            return assignments
        
        except Exception as e:
            logger.exception(f"Error getting assignments for volunteer {volunteer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving assignments"
            )
    
    
    @staticmethod
    def delete_assignment(db: Session, assignment_id: int):
        """Elimina una asignación (soft delete)"""
        logger.info(f"Deleting assignment {assignment_id}")
        
        try:
            assignment = db.query(Assignment).filter(
                Assignment.id == assignment_id,
                Assignment.deleted_at.is_(None)
            ).first()
            
            if not assignment:
                logger.warning(f"Assignment with id={assignment_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignment not found"
                )
            
            # Soft delete
            assignment.deleted_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Assignment {assignment_id} deleted successfully")
            return {"message": "Assignment deleted successfully"}
        
        except HTTPException:
            db.rollback()
            raise
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error deleting assignment {assignment_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting assignment"
            )