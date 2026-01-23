from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime

from models.assignment_model import Assignment
from models.project_skill_model import project_skills 
from models.volunteer_skill_model import volunteer_skills
from models.project_model import Project
from models.volunteers_model import Volunteer
from models.skill_model import Skill
from models.users_model import User
from domain.projects_enums import Project_status as ProjectStatus
from schemas import assignment_schema
from domain.assignment_enum import AssignmentStatus
from config.logging_config import get_logger


logger = get_logger("Assignments")


class AssignmentController:
    
    @staticmethod
    def _get_enriched_assignment_data(db: Session, assignment: Assignment):
        """
        Helper para obtener los datos enriquecidos de un assignment.
        Devuelve: project, volunteer, y skill que hizo match
        """
        # Obtener project_skill
        project_skill = db.execute(
            project_skills.select().where(
                project_skills.c.id == assignment.project_skill_id
            )
        ).first()
        
        # Obtener volunteer_skill
        volunteer_skill = db.execute(
            volunteer_skills.select().where(
                volunteer_skills.c.id == assignment.volunteer_skill_id
            )
        ).first()
        
        if not project_skill or not volunteer_skill:
            return None
        
        # Obtener el proyecto
        project = db.query(Project).filter(
            Project.id == project_skill.project_id
        ).first()
        
        # Obtener el voluntario
        volunteer = db.query(Volunteer).filter(
            Volunteer.id == volunteer_skill.volunteer_id
        ).first()
        
        # Obtener la skill que hizo match (es la misma en ambos)
        skill = db.query(Skill).filter(
            Skill.id == project_skill.skill_id
        ).first()
        
        return {
            'project': project,
            'volunteer': volunteer,
            'skill': skill
        }
    
    @staticmethod
    def assign_volunteer(db: Session, data: assignment_schema.AssignmentCreate):
        """
        Asigna un voluntario a un proyecto validando:
        - Que el project_skill exista
        - Que el volunteer_skill exista
        - Que ambos tengan la misma skill
        - Que no exista una asignación duplicada activa
        
        Devuelve respuesta enriquecida con datos del proyecto, voluntario y skill
        """
        logger.info(f"Creating assignment for project_skill_id={data.project_skill_id} and volunteer_skill_id={data.volunteer_skill_id}")
        
        try:
            # Validar project skill
            project_skill = db.execute(
                project_skills.select().where(
                    project_skills.c.id == data.project_skill_id
                )
            ).first()
            
            if not project_skill:
                logger.warning(f"Project skill with id={data.project_skill_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Project skill not found"
                )
                
            # Validar volunteer skill
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
                
            # Validar que coincidan las skills
            if project_skill.skill_id != volunteer_skill.skill_id:
                logger.warning(f"Skills do not match between project {project_skill.skill_id} and volunteer {volunteer_skill.skill_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Volunteer skill does not match project skill"
                )
            
            # Prevenir duplicación 
            existing_assignment = db.query(Assignment).filter(
                Assignment.project_skill_id == data.project_skill_id,
                Assignment.volunteer_skill_id == data.volunteer_skill_id,
                Assignment.deleted_at.is_(None),
                Assignment.status.in_([
                    AssignmentStatus.PENDING,
                    AssignmentStatus.ACCEPTED
                ])
            ).first()
            
            if existing_assignment:
                logger.warning(f"Assignment already exists for project_skill_id={data.project_skill_id} and volunteer_skill_id={data.volunteer_skill_id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Assignment already exists for this project and volunteer"
                )
                
            # Crear assignment
            assignment = Assignment(
                project_skill_id=data.project_skill_id,
                volunteer_skill_id=data.volunteer_skill_id,
                status=AssignmentStatus.PENDING
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            
            # Obtener datos enriquecidos
            enriched_data = AssignmentController._get_enriched_assignment_data(db, assignment)
            
            if not enriched_data:
                logger.error("Failed to retrieve enriched data for assignment")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error retrieving assignment details"
                )
            
            # Agregar los datos enriquecidos al objeto assignment
            assignment.project = enriched_data['project']
            assignment.volunteer = enriched_data['volunteer']
            assignment.matched_skill = enriched_data['skill']
            
            logger.info(f"Assignment created successfully with id={assignment.id}")
            return assignment
        
        except HTTPException:
            db.rollback()
            raise
        
        except IntegrityError as e:
            db.rollback()
            logger.exception(f"Integrity error creating assignment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Database integrity error creating assignment"
            )
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creating assignment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error creating assignment"
            )
    
    @staticmethod
    def update_status(
        db: Session, 
        assignment_id: int, 
        new_status: AssignmentStatus
    ):
        """
        Actualiza el estado de una asignación y automáticamente
        actualiza el estado del proyecto asociado.
        """
        logger.info(f"Updating assignment status to {new_status}")
        
        try: 
            # Buscar assignment
            assignment = db.query(Assignment).filter(
                Assignment.id == assignment_id,
                Assignment.deleted_at.is_(None)
            ).first()
            
            if not assignment:
                logger.warning(f"Assignment with ID {assignment_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Assignment not found"
                )
                
            # Validar transiciones de estado
            if assignment.status == AssignmentStatus.COMPLETED:
                logger.warning("Attempt to modify completed assignment")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Completed assignment cannot be modified"
                )
            
            # Actualizar estado de la asignación
            old_status = assignment.status
            assignment.status = new_status
            
            # Actualizar estado del proyecto basado en el cambio
            project_skill = db.execute(
                project_skills.select().where(
                    project_skills.c.id == assignment.project_skill_id
                )
            ).first()
            
            if project_skill:
                project = db.query(Project).filter(
                    Project.id == project_skill.project_id,
                    Project.deleted_at.is_(None)
                ).first()
                
                if project:
                    # Si la asignación fue aceptada, marcar proyecto como 'assigned'
                    if new_status == AssignmentStatus.ACCEPTED and old_status != AssignmentStatus.ACCEPTED:
                        project.status = ProjectStatus.assigned
                        logger.info(f"Project {project.id} status updated to assigned")
                    
                    elif new_status == AssignmentStatus.REJECTED:
                        active_assignments = db.query(Assignment).join(
                            project_skills, 
                            Assignment.project_skill_id == project_skills.c.id
                        ).filter(
                            project_skills.c.project_id == project.id,
                            project_skills.c.deleted_at.is_(None),
                            Assignment.deleted_at.is_(None),
                            Assignment.status != AssignmentStatus.REJECTED
                        ).count()
                        
                        if active_assignments == 0:
                            project.status = ProjectStatus.pending
                            logger.info(f"Project {project.id} status updated to pending")
                        
                    # Si todas las asignaciones están completadas, marcar proyecto como 'completed'
                    elif new_status == AssignmentStatus.COMPLETED:
                        incomplete_assignments = db.query(Assignment).join(
                            project_skills, 
                            Assignment.project_skill_id == project_skills.c.id
                        ).filter(
                            project_skills.c.project_id == project.id,
                            project_skills.c.deleted_at.is_(None),
                            Assignment.deleted_at.is_(None),
                            Assignment.status != AssignmentStatus.COMPLETED
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
            
        except Exception as e:
            db.rollback()
            logger.exception(f"Error updating assignment status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error updating assignment status"
            )
    
    @staticmethod
    def get_assignments_by_volunteer(db: Session, volunteer_id: int):
        """
        Obtiene todas las asignaciones de un voluntario.
        Muestra: proyectos asignados y skills utilizadas
        """
        logger.info(f"Getting assignments for volunteer {volunteer_id}")
        
        try:
            # Buscar volunteer_skill_ids del voluntario
            volunteer_skill_rows = db.execute(
                volunteer_skills.select().where(
                    volunteer_skills.c.volunteer_id == volunteer_id,
                    volunteer_skills.c.deleted_at.is_(None)
                )
            ).fetchall()
            
            volunteer_skill_ids = [vs.id for vs in volunteer_skill_rows]
            
            if not volunteer_skill_ids:
                return []
            
            # Obtener assignments
            assignments = db.query(Assignment).filter(
                Assignment.volunteer_skill_id.in_(volunteer_skill_ids),
                Assignment.deleted_at.is_(None)
            ).all()
            
            # Enriquecer cada assignment con project y skill
            enriched_assignments = []
            for assignment in assignments:
                enriched_data = AssignmentController._get_enriched_assignment_data(db, assignment)
                
                if enriched_data:
                    assignment.project = enriched_data['project']
                    assignment.matched_skill = enriched_data['skill']
                    enriched_assignments.append(assignment)
            
            return enriched_assignments
        
        except Exception as e:
            logger.exception(f"Error getting assignments for volunteer {volunteer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving assignments"
            )
    
    @staticmethod
    def get_assignments_by_project(db: Session, project_id: int):
        """
        Obtiene todas las asignaciones de un proyecto.
        Muestra: voluntarios asignados y sus skills
        """
        logger.info(f"Getting assignments for project {project_id}")
        
        try:
            # Buscar project_skill_ids del proyecto
            project_skill_rows = db.execute(
                project_skills.select().where(
                    project_skills.c.project_id == project_id,
                    project_skills.c.deleted_at.is_(None)
                )
            ).fetchall()
            
            project_skill_ids_list = [ps.id for ps in project_skill_rows]
            
            if not project_skill_ids_list:
                return []
            
            # Obtener assignments
            assignments = db.query(Assignment).filter(
                Assignment.project_skill_id.in_(project_skill_ids_list),
                Assignment.deleted_at.is_(None)
            ).all()
            
            # Enriquecer cada assignment con volunteer y skill
            enriched_assignments = []
            for assignment in assignments:
                enriched_data = AssignmentController._get_enriched_assignment_data(db, assignment)
                
                if enriched_data:
                    volunteer_db = enriched_data['volunteer']
                    # Buscar el nombre en la tabla User ---
                    # Usamos el user_id que viene dentro del objeto volunteer
                    user_data = db.query(User).filter(User.id == volunteer_db.user_id).first()
                    
                    # Inyectamos el nombre (o el objeto usuario completo) en el volunteer
                    # para que sea fácil de acceder 
                    volunteer_db.user_name = user_data.name if user_data else "Nombre no encontrado"
                    
                    # Asignamos los objetos al assignment
                    assignment.volunteer = volunteer_db
                    assignment.matched_skill = enriched_data['skill']
                    enriched_assignments.append(assignment)
            
            return enriched_assignments
        
        except Exception as e:
            logger.exception(f"Error getting assignments for project {project_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving assignments"
            )