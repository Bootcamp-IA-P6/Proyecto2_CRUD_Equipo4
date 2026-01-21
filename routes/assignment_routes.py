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

#CREATE - Asignar voluntario a proyecto
@assignment_router.post("/", status_code=status.HTTP_201_CREATED, response_model=assignment_schema.AssignmentOut)
def create_assignment(
    data: assignment_schema.AssignmentCreate,
    db: Session = Depends(get_db)
):
    """
    Asignar un voluntario a un proyecto
    
    ## 🎯 Propósito
    Crea una nueva asignación vinculando voluntario con proyecto.
    Valida compatibilidad de habilidades y disponibilidad.
    
    ## 📋 Parámetros
    - **data**: Objeto AssignmentCreate con información de la asignación
      - volunteer_id: ID del voluntario a asignar (requerido)
      - project_id: ID del proyecto destino (requerido)
      - start_date: Fecha de inicio de la asignación
      - expected_hours: Horas estimadas de compromiso
      - role_description: Descripción específica del rol en el proyecto
    
    ## ✅ Respuesta
    Objeto AssignmentOut con información completa de la asignación (Código 201).
    
    ## ⚠️ Errores comunes
    - **400**: Bad Request - Voluntario no disponible o proyecto completo
    - **404**: Not Found - Voluntario o proyecto no existen
    - **422**: Unprocessable Entity - Incompatibilidad de habilidades
    
    ## 📝 Ejemplo de uso
    ```json
    POST /assignments/
    {
        "volunteer_id": 42,
        "project_id": 15,
        "start_date": "2024-03-01",
        "expected_hours": 40,
        "role_description": "Coordinador de equipo de plantación"
    }
    ```
    
    ## 🔗 Relaciones
    Conecta voluntarios con proyectos, generando seguimiento y métricas de impacto.
    """
    return AssignmentController.assign_volunteer(db, data)


# READ - Obtener asignaciones de un voluntario
@assignment_router.get("/volunteer/{volunteer_id}", response_model=List[assignment_schema.AssignmentOut])
def get_volunteer_assignments(
    volunteer_id: int,
    db: Session = Depends(get_db)
):
    """
    Recupera el historial completo de asignaciones de un voluntario específico.
    Utilizado para gestión de perfil y seguimiento de participación.
    
    ## Parámetros
    - **volunteer_id**: Identificador único del voluntario
    
    ## Respuesta
    Lista de objetos AssignmentOut con historial de asignaciones del voluntario.
    
    ## 📝 Ejemplo de uso
    `GET /assignments/volunteer/42`
    """
    return AssignmentController.get_assignments_by_volunteer(db, volunteer_id)


# READ - Obtener asignaciones de un proyecto 
@assignment_router.get("/project/{project_id}", response_model=List[assignment_schema.AssignmentOut])
def get_project_assignments(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Recupera el equipo completo de voluntarios asignados a un proyecto.
    
    ## Parámetros
    - **project_id**: Identificador único del proyecto
    
    ## Respuesta
    Lista de objetos AssignmentOut con equipo del proyecto.
    
    
    ## 📝 Ejemplo de uso
    `GET /assignments/project/15`
    
    """
    return AssignmentController.get_assignments_by_project(db, project_id)


# UPDATE - Actualizar estado de asignación
@assignment_router.patch("/{assignment_id}/status", response_model=assignment_schema.AssignmentOut)
def update_assignment_status(
    assignment_id: int,
    status_update: assignment_schema.AssignmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Modifica el estado de una asignación para seguimiento del ciclo de vida.
    Actualiza automáticamente el estado del proyecto asociado.
    
    ## Parámetros
    - **assignment_id**: Identificador único de la asignación
    - **status_update**: Objeto con nuevo estado
    
    ## Respuesta
    Objeto AssignmentOut con estado actualizado.

    
    ## 📝 Ejemplo de uso
    ```json
    PATCH /assignments/123/status
    {
        "status": "completed"
    }
    ```
    """
    return AssignmentController.update_status(db, assignment_id, status_update.status)


# # DELETE - Eliminar asignación (soft delete)
# @asignment_router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_assignment(
#     assignment_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Elimina una asignación (soft delete).
#     """
#     AssignmentController.delete_assignment(db, assignment_id)
#     return