from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from controllers.skill_controller import get_skills, get_skill, create_skill, update_skill, delete_skill
from schemas.skills_schema import SkillCreate, SkillUpdate, SkillOut
from typing import List

skill_router = APIRouter(prefix="/skills", tags=["Skills"])

@skill_router.get("/", response_model=List[SkillOut])
def read_skills(db: Session = Depends(get_db)):
    """
    Listar todas las habilidades disponibles
    
    ## 🎯 Propósito
    Recupera el catálogo completo de habilidades del sistema.
    Base para asignación a voluntarios y requisitos de proyectos.
    
    ## ✅ Respuesta
    Lista de objetos SkillOut con información de cada habilidad.
    
    ## ⚠️ Errores comunes
    - **500**: Internal Server Error - Error en conexión a base de datos
    
    ## 📝 Ejemplo de uso
    `GET /skills/`
    
    ## 🔗 Relaciones
    Cada habilidad puede ser asignada a múltiples voluntarios y requerida por múltiples proyectos.
    """
    return get_skills(db)

@skill_router.get("/{id}", response_model=SkillOut)
def read_skill(id: int, db: Session = Depends(get_db)):
    """
    Obtener información detallada de una habilidad específica
    
    ## 🎯 Propósito
    Recupera detalles completos de una habilidad mediante su ID.
    Incluye descripción, nivel de experiencia y áreas de aplicación.
    
    ## 📋 Parámetros
    - **id**: Identificador único de la habilidad
    
    ## ✅ Respuesta
    Objeto SkillOut con información completa de la habilidad.
    
    ## ⚠️ Errores comunes
    - **404**: Not Found - Habilidad no existe
    
    ## 📝 Ejemplo de uso
    `GET /skills/7`
    """
    return get_skill(db, id)

@skill_router.post("/", response_model=SkillOut, status_code=201)
def add_skill(data: SkillCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva habilidad en el catálogo del sistema.

    ## Parámetros
    - **data**: Objeto SkillCreate con información de la habilidad
  
    ## Respuesta
    Objeto SkillOut con información de la habilidad creada (Código 201).
    
    
    ## 📝 Ejemplo de uso
    ```json
    POST /skills/
    {
        "name": "Manejo de Herramientas de Jardinería",
        "description": "Experiencia con podadoras, azadas y equipos de jardín",
        "category": "técnica",
        "level": "básico"
    }
    ```
    """
    return create_skill(db, data)

@skill_router.put("/{id}", response_model=SkillOut)
def modify_skill(id: int, data: SkillUpdate, db: Session = Depends(get_db)):
    """

    Modifica los datos de una habilidad existente.
    Permite refinamiento de descripciones y clasificación.
    
    ## Parámetros
    - **id**: Identificador único de la habilidad a actualizar
    - **data**: Objeto SkillUpdate con campos a modificar (opcionales)
    
    ## Respuesta
    Objeto SkillOut con información actualizada.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /skills/7
    {
        "description": "Experiencia avanzada con equipos profesionales de jardinería",
        "level": "intermedio"
    }
    ```
    """
    return update_skill(db, id, data)

@skill_router.delete("/{id}", response_model=SkillOut)
def remove_skill(id: int, db: Session = Depends(get_db)):
    """
    Realiza eliminación lógica manteniendo integridad de asignaciones históricas.
    
    ## Parámetros
    - **id**: Identificador único de la habilidad a eliminar
    
    ## Respuesta
    Objeto SkillOut con estado actualizado a eliminado.
    
    
    ## 📝 Ejemplo de uso
    `DELETE /skills/7`
    """
    return delete_skill(db, id)
