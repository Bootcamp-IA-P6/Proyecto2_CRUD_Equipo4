from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from controllers.assignment_controller import AssignmentController
from schemas import assignment_schema
from domain.assignment_enum import AssignmentStatus
from database.database import get_db

assignment_router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


# CREATE - Asignar voluntario a proyecto
@assignment_router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=assignment_schema.AssignmentCreateResponse
)
def create_assignment(
    data: assignment_schema.AssignmentCreate,
    db: Session = Depends(get_db)
):
    """
    Asignar un voluntario a un proyecto
    
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
    db: Session = Depends(get_db)
):
    """
    Recupera todas las asignaciones de un voluntario específico.
    
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
        },
        {
            "id": 3,
            "status": "completed",
            "created_at": "2024-02-15T09:00:00",
            "project": {
                "id": 8,
                "name": "Limpieza de Playas",
                "description": "Recolección de residuos"
            },
            "matched_skill": {
                "id": 7,
                "name": "Trabajo en Equipo"
            }
        }
    ]
    ```
    """
    return AssignmentController.get_assignments_by_volunteer(db, volunteer_id)


# READ - Obtener asignaciones de un proyecto 
@assignment_router.get(
    "/project/{project_id}", 
    response_model=List[assignment_schema.AssignmentByProject]
)
def get_project_assignments(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Recupera el equipo completo de voluntarios asignados a un proyecto.
    
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
        },
        {
            "id": 2,
            "status": "pending",
            "created_at": "2024-03-02T11:00:00",
            "volunteer": {
                "id": 87,
                "user_id": 456,
                "user_name": "John Doe"
            },
            "matched_skill": {
                "id": 5,
                "name": "Liderazgo"
            }
        }
    ]
    ```
    """
    return AssignmentController.get_assignments_by_project(db, project_id)


# UPDATE - Actualizar estado de asignación
@assignment_router.patch(
    "/{assignment_id}/status", 
    response_model=assignment_schema.AssignmentOut
)
def update_assignment_status(
    assignment_id: int,
    status_update: assignment_schema.AssignmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Modifica el estado de una asignación para seguimiento del ciclo de vida.
    Actualiza automáticamente el estado del proyecto asociado.
    
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
    return AssignmentController.update_status(db, assignment_id, status_update.status)