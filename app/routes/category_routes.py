from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from app.database.database import get_db
from app.schemas.category_schemas import (
    CategoryCreate,
    CategoryOut
)
from app.controllers.category_controller import *
from app.controllers.auth_controller import get_current_user, require_admin
from app.models.users_model import User


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# Constantes para roles
ROLE_ADMIN = 1
ROLE_VOLUNTEER = 2


@router.post("/", response_model=CategoryOut)
def create(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Establece una nueva categoría para clasificación de proyectos.
    Facilita la organización y búsqueda de proyectos por temática.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede crear categorías
    - ❌ Voluntario: no puede crear categorías
    
    ## Parámetros
    - **category**: Objeto CategoryCreate con información de la categoría
    ## Respuesta
    Objeto CategoryOut con información completa de la categoría creada.

    ## 📝 Ejemplo de uso
    ```json
    POST /categories/
    {
        "name": "Medio Ambiente",
        "description": "Proyectos de conservación y sostenibilidad ambiental",
        "color": "#4CAF50"
    }
    ```
    """
    return create_category(db, category)


@router.get("/", response_model=Page[CategoryOut])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera todas las categorías activas del sistema.
    Implementa paginación para manejar grandes volúmenes eficientemente.
    
    ## Permisos
    - ✅ Admin: puede ver todas las categorías
    - ✅ Voluntario: puede ver todas las categorías
    
    ## Respuesta
    Lista paginada de objetos CategoryOut con información de cada categoría.
    
    ## 📝 Ejemplo de uso
    `GET /categories/?page=1&size=10`
    """
    return get_categories(db)


@router.get("/{id}", response_model=CategoryOut)
def get_one(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera detalles completos de una categoría mediante su ID.
    
    ## Permisos
    - ✅ Admin: puede ver cualquier categoría
    - ✅ Voluntario: puede ver cualquier categoría
    
    ## Parámetros
    - **id**: Identificador único de la categoría
    
    ## Respuesta
    Objeto CategoryOut con información completa de la categoría.
    
    ## 📝 Ejemplo de uso
    `GET /categories/5`
    """
    return get_category(db, id)


@router.put("/{id}", response_model=CategoryOut)
def update(
    id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Modifica los datos de una categoría existente.
    Permite actualización de nombre, descripción y apariencia visual.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede actualizar categorías
    - ❌ Voluntario: no puede actualizar categorías
    
    ## Parámetros
    - **id**: Identificador único de la categoría a actualizar
    - **data**: Objeto CategoryCreate con nuevos valores
    
    ## Respuesta
    Objeto CategoryOut con información actualizada.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /categories/5
    {
        "name": "Conservación Ambiental",
        "description": "Proyectos focused en protección de ecosistemas",
        "color": "#2E7D32"
    }
    ```
    """
    return update_category(db, id, data)


@router.delete("/{id}", response_model=CategoryOut)
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Realiza eliminación lógica de la categoría manteniendo integridad.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede eliminar categorías
    - ❌ Voluntario: no puede eliminar categorías
    
    ## Parámetros
    - **id**: Identificador único de la categoría a eliminar
    
    ## Respuesta
    Objeto CategoryOut con estado actualizado a eliminado.
    
    ## 📝 Ejemplo de uso
    `DELETE /categories/5`
    """
    return delete_category(db, id)