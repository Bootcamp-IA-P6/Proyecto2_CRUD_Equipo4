from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi_pagination import Page

from app.database.database import get_db
from app.controllers.skill_controller import get_skills, get_skill, create_skill, update_skill, delete_skill
from app.schemas.skills_schema import SkillCreate, SkillUpdate, SkillOut
from app.controllers.auth_controller import get_current_user, require_admin
from app.models.users_model import User

skill_router = APIRouter(prefix="/skills", tags=["Skills"])

# GET ALL - Usuarios autenticados pueden ver habilidades
@skill_router.get("/", response_model=Page[SkillOut])
def read_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera el catálogo completo de habilidades del sistema.
    Implementa paginación para manejar grandes volúmenes eficientemente.
    
    ## 🔒 Permisos requeridos
    - Usuario autenticado (cualquier rol)
    
    ## Respuesta
    Lista de objetos SkillOut con información de cada habilidad.
    
    ## 📝 Ejemplo de uso
    ```bash
    GET /skills/?page=1&size=10
    Authorization: Bearer <token>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    """
    return get_skills(db)


# GET BY ID - Usuarios autenticados pueden ver detalle de habilidades
@skill_router.get("/{id}", response_model=SkillOut)
def read_skill(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener información detallada de una habilidad específica
    
    ## 🎯 Propósito
    Recupera detalles completos de una habilidad mediante su ID.
    Incluye descripción, nivel de experiencia y áreas de aplicación.
    
    ## 🔒 Permisos requeridos
    - Usuario autenticado (cualquier rol)
    
    ## 📋 Parámetros
    - **id**: Identificador único de la habilidad
    
    ## ✅ Respuesta
    Objeto SkillOut con información completa de la habilidad.
    
    ## ⚠️ Errores comunes
    - **401 Unauthorized**: Token inválido o expirado
    - **404 Not Found**: Habilidad no existe
    
    ## 📝 Ejemplo de uso
    ```bash
    GET /skills/7
    Authorization: Bearer <token>
    ```
    """
    return get_skill(db, id)


# POST - Solo administradores pueden crear habilidades
@skill_router.post("/", response_model=SkillOut, status_code=201)
def add_skill(
    data: SkillCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Registra una nueva habilidad en el catálogo del sistema.

    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**

    ## Parámetros
    - **data**: Objeto SkillCreate con información de la habilidad

    ## Respuesta
    Objeto SkillOut con información de la habilidad creada (Código 201).
    
    ## 📝 Ejemplo de uso
    ```json
    POST /skills/
    Authorization: Bearer <token_admin>
    
    {
        "name": "Manejo de Herramientas de Jardinería",
        "description": "Experiencia con podadoras, azadas y equipos de jardín",
        "category": "técnica",
        "level": "básico"
    }
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **400 Bad Request**: Habilidad ya existe o datos inválidos
    """
    return create_skill(db, data)


# PUT - Solo administradores pueden actualizar habilidades
@skill_router.put("/{id}", response_model=SkillOut)
def modify_skill(
    id: int, 
    data: SkillUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Modifica los datos de una habilidad existente.
    Permite refinamiento de descripciones y clasificación.
    
    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## Parámetros
    - **id**: Identificador único de la habilidad a actualizar
    - **data**: Objeto SkillUpdate con campos a modificar (opcionales)
    
    ## Respuesta
    Objeto SkillOut con información actualizada.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /skills/7
    Authorization: Bearer <token_admin>
    
    {
        "description": "Experiencia avanzada con equipos profesionales de jardinería",
        "level": "intermedio"
    }
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **404 Not Found**: Habilidad no encontrada
    """
    return update_skill(db, id, data)


# DELETE - Solo administradores pueden eliminar habilidades
@skill_router.delete("/{id}", response_model=SkillOut)
def remove_skill(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Realiza eliminación lógica manteniendo integridad de asignaciones históricas.
    
    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## Parámetros
    - **id**: Identificador único de la habilidad a eliminar
    
    ## Respuesta
    Objeto SkillOut con estado actualizado a eliminado.
    
    ## 📝 Ejemplo de uso
    ```bash
    DELETE /skills/7
    Authorization: Bearer <token_admin>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **404 Not Found**: Habilidad no encontrada
    - **400 Bad Request**: Habilidad tiene asignaciones activas
    """
    return delete_skill(db, id)