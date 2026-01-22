from fastapi import APIRouter, Depends, HTTPException

from fastapi_pagination import Page
from sqlalchemy.orm import Session
from typing import List

from controllers.project_controller import ProjectController
from schemas import project_schema
from database.database import get_db

project_router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

#CREATE PROJECT
@project_router.post("/", response_model=project_schema.ProjectOut)
async def new_project(project: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    """

        Registra un nuevo proyecto en el sistema con información completa.
        Establece la base para asignación de voluntarios y seguimiento de progreso.
        
        
        ##  Respuesta
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
            "status": "planning",
        }
        ```
    """
    
    return await ProjectController.create_project(db, project)
    
#READ PROJECT
@project_router.get("/{project_id}", response_model=project_schema.ProjectOut)
async def read_project(project_id: int, db: Session = Depends(get_db)):
    """
        Recupera el perfil completo de un proyecto mediante su ID.
        Incluye información de categoría, estado y asignaciones actuales.
        
        ## Parámetros
        - **project_id**: Identificador único del proyecto (requerido)
        
        ## Respuesta
        Objeto ProjectOut con información completa del proyecto.
        
        ## 📝 Ejemplo de uso
        `GET /projects/42`
        
    """
    return await ProjectController.get_project(db, project_id=project_id)

#READ ALL PROJECTS
@project_router.get("/", response_model=Page[project_schema.ProjectOut])
async def read_all_projects(db: Session = Depends(get_db)):
    """
        Recupera información completa de todos los proyectos del sistema.
        Implementa paginación para manejar grandes volúmenes eficientemente.
        
        ## Respuesta
        Lista de objetos ProjectOut con información detallada de cada proyecto.

        ## 📝 Ejemplo de uso
        `GET /projects/?page=0&size=10`
    
    """
    return await ProjectController.get_projects(db)

#UPDATE PROJECT
@project_router.put("/{project_id}", response_model=project_schema.ProjectOut)
async def update_project(project_id: int, project: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    """
        Modifica los datos de un proyecto existente.
        Permite actualización parcial y seguimiento del progreso.
        
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
    

# SOFT-DELETE PROJECT
@project_router.delete("/{project_id}", response_model=project_schema.ProjectOut)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
       
        Realiza eliminación lógica del proyecto manteniendo integridad histórica.
        Preserva registros de asignaciones y actividades completadas.
        
        ## Parámetros
        - **project_id**: Identificador único del proyecto a eliminar
        
        ## Respuesta
        Objeto ProjectOut con estado actualizado a eliminado.
        
        ## 📝 Ejemplo de uso
        `DELETE /projects/42`
        
        
    """
    return await ProjectController.delete_project(db, project_id)



#### ENDPOINTS DE PROJECT_SKILLS ####

#READ PROJECT + SKILLS
@project_router.get("/{id}/skills", response_model=project_schema.ProjectSkillsOut)
async def get_skills(id: int, db: Session = Depends(get_db)):
    """
        
        Recupera habilidades asignadas para el proyecto.
        Esencial para matching de voluntarios cualificados.
        
        ## Parámetros
        - **id**: Identificador único del proyecto
        
        ## Respuesta
        Objeto ProjectSkillsOut con información del proyecto y sus habilidades requeridas.
     
        
        ## 📝 Ejemplo de uso
        `GET /projects/42/skills`
        
    """
    return await ProjectController.get_project_with_skills(db, id)

#ADD SKILL TO PROJECT
@project_router.post("/{id}/skills/{skill_id}", response_model=project_schema.ProjectSkillsOut)
async def add_skill(id: int, skill_id: int, db: Session = Depends(get_db)):
    """
        
        Define una habilidad específica como requisito para el proyecto.
        Facilita la búsqueda y asignación de voluntarios cualificados.
        
        ##  Parámetros
        - **id**: ID del proyecto a modificar
        - **skill_id**: ID de la habilidad requerida
        
        ##  Respuesta
        Objeto ProjectSkillsOut actualizado con nueva habilidad requerida.
        
        
        ## 📝 Ejemplo de uso
        `POST /projects/42/skills/7`
        
    """
    return await ProjectController.add_skill_to_project(db, id, skill_id)

#DELETE SKILL FROM PROJECT
@project_router.delete("/{id}/skills/{skill_id}")
async def remove_skill(id: int, skill_id: int, db: Session = Depends(get_db)):
    """
        Remueve una habilidad específico del proyecto.
        
        ## Parámetros
        - **id**: ID del proyecto a modificar
        - **skill_id**: ID de la habilidad a remover
        
        ## Respuesta
        Mensaje de confirmación de eliminación exitosa.
        
        ## 📝 Ejemplo de uso
        `DELETE /projects/42/skills/7`
    
    """
    return await ProjectController.remove_skill_from_project(db, id, skill_id)

#DELETE ALL SKILLS FROM PROJECT
@project_router.delete("/{id}/skills", response_model=project_schema.ProjectSkillsOut)
async def remove_all_skills(id: int, db: Session = Depends(get_db)):
    """
        Limpia completamente las habilidades del proyecto.
        Utilizado para rediseñar los requisitos desde cero.
        
        ## Parámetros
        - **id**: ID del proyecto a limpiar
        
        ## Respuesta
        Objeto ProjectSkillsOut con lista vacía de habilidades.
        
        
        ## 📝 Ejemplo de uso
        `DELETE /projects/42/skills`
    
    """
    return await ProjectController.remove_all_skills_from_project(db, id)


#Matching - no asigna
@project_router.get("/{project_id}/matching-volunteers",status_code=200)
def get_matching_volunteers(project_id: int, db: Session = Depends(get_db)):
    """
        Devuelve los voluntarios que tienen match con las skills del proyecto.
        
        ## Parámetros
        - **id**: ID del proyecto
        
        ## Respuesta
        Lista con:
        - **Volunteer_id**: ID del voluntario.
        - **Volunteer_name**: Nombre del voluntario.
        - **Matched_skills**: Lista de Skills.
            - **id**: ID de la Skill
            - **name**: Nombre de la Skill
        
        
        ## 📝 Ejemplo de uso
        `GET /projects/1/matching-volunteers`
    
    """
    return ProjectController.get_matching_volunteers(db, project_id)
