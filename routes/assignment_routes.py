from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from controllers.assignment_controller import AssignmentController
from schemas import assignment_schema
from domain.assignment_enum import AssignmentStatus
from database.database import get_db

assignment_router = APIRouter(
    prefix="/assignments",
    tags=["assignments"]
)

#CREATE - Asignar voluntario a proyecto
@assignment_router.post("/", status_code=status.HTTP_201_CREATED, response_model=assignment_schema.AssignmentOut)
def create_assignment(
    data: assignment_schema.AssignmentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva asignación de voluntario a proyecto.
    Valida que ambos tengan la misma skill.
    """
    return AssignmentController.assign_volunteer(db, data)


# READ - Obtener asignaciones de un voluntario
@assignment_router.get("/volunteer/{volunteer_id}", response_model=List[assignment_schema.AssignmentOut])
def get_volunteer_assignments(
    volunteer_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las asignaciones activas de un voluntario específico.
    """
    return AssignmentController.get_assignments_by_volunteer(db, volunteer_id)


# READ - Obtener asignaciones de un proyecto 
@assignment_router.get("/project/{project_id}", response_model=List[assignment_schema.AssignmentOut])
def get_project_assignments(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las asignaciones activas de un proyecto específico.
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
    Actualiza el estado de una asignación.
    Automáticamente actualiza el estado del proyecto asociado.
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