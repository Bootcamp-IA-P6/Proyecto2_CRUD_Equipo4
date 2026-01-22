from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from database.database import get_db
from schemas.category_schemas import (
    CategoryCreate,
    CategoryOut
)
from controllers.category_controller import *


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=CategoryOut)
def create(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Establece una nueva categoría para clasificación de proyectos.
    Facilita la organización y búsqueda de proyectos por temática.
    
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
def list_all(db: Session = Depends(get_db)):
    """
    Recupera todas las categorías activas del sistema.
    Implementa paginación para manejar grandes volúmenes eficientemente.
    
    ## Respuesta
    Lista de objetos CategoryOut con información de cada categoría.
    
    ## 📝 Ejemplo de uso
    `GET /categories/?page=0&size=10`
    
    """
    return get_categories(db)

@router.get("/{id}", response_model=CategoryOut)
def get_one(id: int, db: Session = Depends(get_db)):
    """
    Recupera detalles completos de una categoría mediante su ID.
    
    ## Parámetros
    - **id**: Identificador único de la categoría
    
    ## Respuesta
    Objeto CategoryOut con información completa de la categoría.
    
    
    ## 📝 Ejemplo de uso
    `GET /categories/5`
    """
    return get_category(db, id) 

@router.put("/{id}", response_model=CategoryOut)
def update(id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    """
    Modifica los datos de una categoría existente.
    Permite actualización de nombre, descripción y apariencia visual.
    
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
def delete(id: int, db: Session = Depends(get_db)):
    """
    Realiza eliminación lógica de la categoría manteniendo integridad.
    
    ## Parámetros
    - **id**: Identificador único de la categoría a eliminar
    
    ## Respuesta
    Objeto CategoryOut con estado actualizado a eliminado.
    
    ## 📝 Ejemplo de uso
    `DELETE /categories/5`
    """
    return delete_category(db, id)