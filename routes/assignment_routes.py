from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import select

from controllers.assignment_controller import AssignmentController
from schemas import assignment_schema
from domain.assignment_enum import AssignmentStatus
from database.database import get_db
from controllers.auth_controller import get_current_user, require_admin
from models.users_model import User


assignment_router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)

# Constantes para roles
ROLE_ADMIN = 1
ROLE_VOLUNTEER = 2


# CREATE - Asignar voluntario a proyecto (Solo admin)
@assignment_router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=assignment_schema.AssignmentCreateResponse
)
def create_assignment(
    data: assignment_schema.AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Asignar un voluntario a un proyecto.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede crear asignaciones para cualquier voluntario
    - ❌ Voluntario: no puede crear asignaciones
    
    ## 🎯 Propósito
    Crea una nueva asignación vinculando un volunteer_skill con un project_skill.
    Valida que ambos skills sean la misma (match de habilidades).
    
    ## 📋 Parámetros
    - **data**: Objeto AssignmentCreate con información de la asignación
    - project_skill_id: ID de la relación proyecto-skill (requerido)
    - volunteer_skill_id: ID de la relación voluntario-skill (requerido)
    - status: Estado inicial (default: PENDING)
    
    ## ✅ Respuesta ENRIQUECIDA
    Objeto AssignmentCreateResponse con información completa:
    - Datos básicos del assignment
    - Información del proyecto (id, name, description)
    - Información del voluntario (id, user_id)
    - Skill que hizo match (id, name)
    
    ## ⚠️ Errores comunes
    - **400**: Bad Request - Las skills no coinciden
    - **403**: Forbidden - No tiene permisos de administrador
    - **404**: Not Found - project_skill o volunteer_skill no existen
    - **409**: Conflict - Ya existe una asignación activa para esta combinación
    
    ## 📝 Ejemplo de uso
    ```json
    POST /assignments/
    {
        "project_skill_id": 15,
        "volunteer_skill_id": 42,
        "status": "pending"
    }
    ```
    
    ## 📤 Ejemplo de respuesta
    ```json
    {
        "id": 1,
        "project_skill_id": 15,
        "volunteer_skill_id": 42,
        "status": "pending",
        "created_at": "2024-03-01T10:30:00",
        "updated_at": "2024-03-01T10:30:00",
        "volunteer": {
            "id": 42,
            "user_id": 123
        },
        "project": {
            "id": 5,
            "name": "Reforestación Urbana",
            "description": "Plantación de árboles nativos"
        },
        "matched_skill": {
            "id": 3,
            "name": "Jardinería"
        }
    }
    ```
    """
    return AssignmentController.assign_volunteer(db, data)


# READ - Obtener asignaciones de un voluntario
@assignment_router.get(
    "/volunteer/{volunteer_id}", 
    response_model=List[assignment_schema.AssignmentByVolunteer]
)
def get_volunteer_assignments(
    volunteer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera todas las asignaciones de un voluntario específico.
    
    ## Permisos
    - ✅ Admin: puede ver asignaciones de cualquier voluntario
    - ✅ Voluntario: solo puede ver sus propias asignaciones
    
    ## 🎯 Propósito
    Muestra todos los proyectos en los que está trabajando un voluntario,
    junto con las skills que está utilizando en cada proyecto.
    
    ## 📋 Parámetros
    - **volunteer_id**: Identificador único del voluntario
    
    ## ✅ Respuesta
    Lista de objetos AssignmentByVolunteer, cada uno con:
    - id, status, created_at del assignment
    - Información del proyecto (id, name, description)
    - Skill utilizada (id, name)
    
    ## 📝 Ejemplo de uso
    `GET /assignments/volunteer/42`
    
    ## 📤 Ejemplo de respuesta
    ```json
    [
        {
            "id": 1,
            "status": "accepted",
            "created_at": "2024-03-01T10:30:00",
            "project": {
                "id": 5,
                "name": "Reforestación Urbana",
                "description": "Plantación de árboles"
            },
            "matched_skill": {
                "id": 3,
                "name": "Jardinería"
            }
        }
    ]
    ```
    """
    # Obtener el voluntario para validar que pertenece al current_user
    # Necesitarás importar el modelo Volunteer y hacer una query
    from models.volunteer_model import Volunteer
    
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Verificar permisos: admin puede ver cualquiera, voluntario solo el suyo
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only view your own assignments"
        )
    
    return AssignmentController.get_assignments_by_volunteer(db, volunteer_id)


# READ - Obtener asignaciones de un proyecto
@assignment_router.get(
    "/project/{project_id}", 
    response_model=List[assignment_schema.AssignmentByProject]
)
def get_project_assignments(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera el equipo completo de voluntarios asignados a un proyecto.
    
    ## Permisos
    - ✅ Admin: puede ver asignaciones de cualquier proyecto
    - ✅ Voluntario: puede ver asignaciones del proyecto (para conocer al equipo)
    
    ## 🎯 Propósito
    Muestra todos los voluntarios trabajando en un proyecto específico,
    junto con las skills que cada uno está aportando.
    
    ## 📋 Parámetros
    - **project_id**: Identificador único del proyecto
    
    ## ✅ Respuesta
    Lista de objetos AssignmentByProject, cada uno con:
    - id, status, created_at del assignment
    - Información del voluntario (id, user_id)
    - Skill aportada (id, name)
    
    ## 📝 Ejemplo de uso
    `GET /assignments/project/5`
    
    ## 📤 Ejemplo de respuesta
    ```json
    [
        {
            "id": 1,
            "status": "accepted",
            "created_at": "2024-03-01T10:30:00",
            "volunteer": {
                "id": 42,
                "user_id": 123,
                "user_name": "John Doe"
            },
            "matched_skill": {
                "id": 3,
                "name": "Jardinería"
            }
        }
    ]
    ```
    """
    # Todos pueden ver las asignaciones de un proyecto
    # (útil para que voluntarios sepan con quién trabajarán)
    return AssignmentController.get_assignments_by_project(db, project_id)


# UPDATE - Actualizar estado de asignación
@assignment_router.patch(
    "/{assignment_id}/status", 
    response_model=assignment_schema.AssignmentOut
)
def update_assignment_status(
    assignment_id: int,
    status_update: assignment_schema.AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Modifica el estado de una asignación para seguimiento del ciclo de vida.
    Actualiza automáticamente el estado del proyecto asociado.
    
    ## Permisos
    - ✅ Admin: puede actualizar cualquier asignación a cualquier estado
    - ✅ Voluntario: puede actualizar solo SUS asignaciones y solo a estados específicos:
        - PENDING → ACCEPTED (aceptar la asignación)
        - PENDING → REJECTED (rechazar la asignación)
        - ACCEPTED → COMPLETED (completar la asignación)
    - ❌ Voluntario NO puede: cambiar asignaciones de otros, ni usar estados no permitidos
    
    ## 📋 Parámetros
    - **assignment_id**: Identificador único de la asignación
    - **status_update**: Objeto con nuevo estado
    
    ## ✅ Respuesta
    Objeto AssignmentOut con estado actualizado.

    ## 🔄 Lógica de actualización automática del proyecto
    - `accepted` → Proyecto pasa a 'assigned'
    - `rejected` → Si no quedan asignaciones activas, proyecto vuelve a 'pending'
    - `completed` → Si todas las asignaciones están completadas, proyecto pasa a 'completed'
    
    ## 📝 Ejemplo de uso
    ```json
    PATCH /assignments/123/status
    {
        "status": "accepted"
    }
    ```
    """
    # Obtener la asignación para validar permisos
    from models.assignment_model import Assignment
    from models.volunteers_model import Volunteer
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Obtener el volunteer_skill para validar el dueño
    from models.volunteer_skill_model import volunteer_skills
    # 1. Obtener la fila de la tabla (Core)
    # Usamos .c (columns) para acceder a los campos de la tabla
    stmt = select(volunteer_skills).where(
        volunteer_skills.c.id == assignment.volunteer_skill_id
    )
    volunteer_skill = db.execute(stmt).first()

    if not volunteer_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer skill not found"
        )

    # 2. Obtener el voluntario (ORM)
    # Nota: volunteer_skill actúa como un Row, así que accedemos por nombre de columna
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_skill.volunteer_id
    ).first()

    # --- El resto de tu lógica de permisos se mantiene igual ---

    is_admin = current_user.role_id == ROLE_ADMIN
    is_owner = volunteer and volunteer.user_id == current_user.id

    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only update your own assignments"
        )
    
    # Si es voluntario (no admin), validar transiciones permitidas
    if not is_admin:
        current_status = assignment.status
        new_status = status_update.status
        
        # Definir transiciones permitidas para voluntarios
        allowed_transitions = {
            AssignmentStatus.PENDING: [AssignmentStatus.ACCEPTED, AssignmentStatus.REJECTED],
            AssignmentStatus.ACCEPTED: [AssignmentStatus.COMPLETED]
        }
        
        if current_status not in allowed_transitions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot change assignment from status '{current_status}'"
            )
        
        if new_status not in allowed_transitions[current_status]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Volunteers cannot change status from '{current_status}' to '{new_status}'"
            )
    
    return AssignmentController.update_status(db, assignment_id, status_update.status)