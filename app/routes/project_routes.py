from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from typing import List

from app.controllers.project_controller import ProjectController
from app.schemas import project_schema
from app.database.database import get_db
from app.controllers.auth_controller import get_current_user, require_admin
from app.models.users_model import User

project_router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# Constantes para roles
ROLE_ADMIN = 1
ROLE_VOLUNTEER = 2


# CREATE PROJECT - Solo admin puede crear proyectos
@project_router.post("/", response_model=project_schema.ProjectOut)
async def new_project(
    project: project_schema.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Registra un nuevo proyecto en el sistema con información completa.
    Establece la base para asignación de voluntarios y seguimiento de progreso.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede crear proyectos
    - ❌ Voluntario: no puede crear proyectos
    
    ## Respuesta
    Objeto ProjectOut con información completa del proyecto creado.
    
    ## 📝 Ejemplo de uso
    ```json
    POST /projects/
    {
        "name": "CREACION WEBSITE",
        "description": "Website para asociacion de animales",
        "category_id": 3,
        "start_date": "2024-03-01",
        "end_date": "2024-06-30",
        "status": "planning"
    }
    ```
    """
    return await ProjectController.create_project(db, project)


# READ ALL PROJECTS - Todos pueden ver la lista de proyectos
@project_router.get("/", response_model=Page[project_schema.ProjectOut])
async def read_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera información completa de todos los proyectos del sistema.
    Implementa paginación para manejar grandes volúmenes eficientemente.
    
    ## Permisos
    - ✅ Admin: puede ver todos los proyectos
    - ✅ Voluntario: puede ver todos los proyectos disponibles
    
    ## Respuesta
    Lista paginada de objetos ProjectOut con información detallada de cada proyecto.

    ## 📝 Ejemplo de uso
    `GET /projects/?page=1&size=10`
    """
    return await ProjectController.get_projects(db)


# READ PROJECT - Todos pueden ver un proyecto específico
@project_router.get("/{project_id}", response_model=project_schema.ProjectOut)
async def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera el perfil completo de un proyecto mediante su ID.
    Incluye información de categoría, estado y asignaciones actuales.
    
    ## Permisos
    - ✅ Admin: puede ver cualquier proyecto
    - ✅ Voluntario: puede ver cualquier proyecto
    
    ## Parámetros
    - **project_id**: Identificador único del proyecto (requerido)
    
    ## Respuesta
    Objeto ProjectOut con información completa del proyecto.
    
    ## 📝 Ejemplo de uso
    `GET /projects/42`
    """
    return await ProjectController.get_project(db, project_id=project_id)


# UPDATE PROJECT - Solo admin puede actualizar proyectos
@project_router.put("/{project_id}", response_model=project_schema.ProjectOut)
async def update_project(
    project_id: int,
    project: project_schema.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Modifica los datos de un proyecto existente.
    Permite actualización parcial y seguimiento del progreso.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede actualizar cualquier proyecto
    - ❌ Voluntario: no puede actualizar proyectos
    
    ## Parámetros
    - **project_id**: Identificador único del proyecto a actualizar
    - **project**: Objeto ProjectUpdate con campos a modificar (opcionales)
    
    ## Respuesta
    Objeto ProjectOut con información actualizada del proyecto.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /projects/42
    {
        "status": "in_progress",
        "end_date": "2024-07-15"
    }
    ```
    """
    return await ProjectController.update_project(db, project_id, project)


# SOFT-DELETE PROJECT - Solo admin puede eliminar proyectos
@project_router.delete("/{project_id}", response_model=project_schema.ProjectOut)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Realiza eliminación lógica del proyecto manteniendo integridad histórica.
    Preserva registros de asignaciones y actividades completadas.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede eliminar cualquier proyecto
    - ❌ Voluntario: no puede eliminar proyectos
    
    ## Parámetros
    - **project_id**: Identificador único del proyecto a eliminar
    
    ## Respuesta
    Objeto ProjectOut con estado actualizado a eliminado.
    
    ## 📝 Ejemplo de uso
    `DELETE /projects/42`
    """
    return await ProjectController.delete_project(db, project_id)


#### ENDPOINTS DE PROJECT_SKILLS ####

# READ PROJECT + SKILLS - Todos pueden ver las habilidades requeridas
@project_router.get("/{id}/skills", response_model=project_schema.ProjectSkillsOut)
async def get_skills(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera habilidades asignadas para el proyecto.
    Esencial para matching de voluntarios cualificados.
    
    ## Permisos
    - ✅ Admin: puede ver habilidades de cualquier proyecto
    - ✅ Voluntario: puede ver habilidades de cualquier proyecto
    
    ## Parámetros
    - **id**: Identificador único del proyecto
    
    ## Respuesta
    Objeto ProjectSkillsOut con información del proyecto y sus habilidades requeridas.
    
    ## 📝 Ejemplo de uso
    `GET /projects/42/skills`
    """
    return await ProjectController.get_project_with_skills(db, id)


# ADD SKILL TO PROJECT - Solo admin puede agregar habilidades
@project_router.post("/{id}/skills/{skill_id}", response_model=project_schema.ProjectSkillsOut)
async def add_skill(
    id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Define una habilidad específica como requisito para el proyecto.
    Facilita la búsqueda y asignación de voluntarios cualificados.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede agregar habilidades a proyectos
    - ❌ Voluntario: no puede modificar habilidades de proyectos
    
    ## Parámetros
    - **id**: ID del proyecto a modificar
    - **skill_id**: ID de la habilidad requerida
    
    ## Respuesta
    Objeto ProjectSkillsOut actualizado con nueva habilidad requerida.
    
    ## 📝 Ejemplo de uso
    `POST /projects/42/skills/7`
    """
    return await ProjectController.add_skill_to_project(db, id, skill_id)


# DELETE SKILL FROM PROJECT - Solo admin puede remover habilidades
@project_router.delete("/{id}/skills/{skill_id}")
async def remove_skill(
    id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Remueve una habilidad específica del proyecto.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede remover habilidades de proyectos
    - ❌ Voluntario: no puede modificar habilidades de proyectos
    
    ## Parámetros
    - **id**: ID del proyecto a modificar
    - **skill_id**: ID de la habilidad a remover
    
    ## Respuesta
    Mensaje de confirmación de eliminación exitosa.
    
    ## 📝 Ejemplo de uso
    `DELETE /projects/42/skills/7`
    """
    return await ProjectController.remove_skill_from_project(db, id, skill_id)


# DELETE ALL SKILLS FROM PROJECT - Solo admin puede limpiar habilidades
@project_router.delete("/{id}/skills", response_model=project_schema.ProjectSkillsOut)
async def remove_all_skills(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Limpia completamente las habilidades del proyecto.
    Utilizado para rediseñar los requisitos desde cero.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede limpiar todas las habilidades de un proyecto
    - ❌ Voluntario: no puede modificar habilidades de proyectos
    
    ## Parámetros
    - **id**: ID del proyecto a limpiar
    
    ## Respuesta
    Objeto ProjectSkillsOut con lista vacía de habilidades.
    
    ## 📝 Ejemplo de uso
    `DELETE /projects/42/skills`
    """
    return await ProjectController.remove_all_skills_from_project(db, id)


# MATCHING VOLUNTEERS - Todos pueden ver matching
@project_router.get("/{project_id}/matching-volunteers", status_code=200)
def get_matching_volunteers(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve los voluntarios que tienen match con las skills del proyecto.
    Útil para que voluntarios vean si califican y para que admin asigne.
    
    ## Permisos
    - ✅ Admin: puede ver voluntarios que coinciden con cualquier proyecto
    - ✅ Voluntario: puede ver si califica para proyectos
    
    ## Parámetros
    - **project_id**: ID del proyecto
    
    ## Respuesta
    Lista con:
    - **volunteer_id**: ID del voluntario
    - **volunteer_name**: Nombre del voluntario
    - **matched_skills**: Lista de Skills
        - **id**: ID de la Skill
        - **name**: Nombre de la Skill
    
    ## 📝 Ejemplo de uso
    `GET /projects/1/matching-volunteers`
    """
    return ProjectController.get_matching_volunteers(db, project_id)