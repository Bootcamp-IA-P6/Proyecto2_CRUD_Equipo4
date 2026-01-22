from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from database.database import get_db
from schemas.volunteer_schema import (
    VolunteerCreate,
    VolunteerUpdate,
    VolunteerOut,
    VolunteerWithSkills
)
from controllers.volunteer_controller import *

router = APIRouter(
    prefix="/volunteers",
    tags=["Volunteers"]
)

@router.post("/", response_model=VolunteerOut)
def create(volunteer: VolunteerCreate, db: Session = Depends(get_db)):
    """

    Registra un nuevo voluntario vinculándolo a un usuario existente.
    
    ## Parámetros
    - **volunteer**: Objeto VolunteerCreate con información del voluntario
    
    ## Respuesta
    Objeto VolunteerOut con información del voluntario creado.
    
    ## 📝 Ejemplo de uso
    ```json
    POST /volunteers/
    {
        "user_id": 42,
        "availability": "Fin de semana",
        "experience": "3 años en ONGs",
        "motivation": "Ayudar a la comunidad"
    }
    ```
    
    """
    return create_volunteer(db, volunteer)

@router.get("/", response_model=Page[VolunteerOut])
def list_all(db: Session = Depends(get_db)):
    """
    Recupera información completa de todos los voluntarios activos del sistema.
    Implementa paginación para manejar grandes volúmenes eficientemente.
    
    ## Respuesta
    Lista de objetos VolunteerOut con información detallada de cada voluntario.
    
    ## 📝 Ejemplo de uso
    `GET /volunteers/?page=0&size=10`

    """
    return get_volunteers(db)

@router.get("/{id}", response_model=VolunteerOut)
def get_one(id: int, db: Session = Depends(get_db)):
    """
    Recupera el perfil completo de un voluntario mediante su ID.
    
    ## Parámetros
    - **id**: Identificador único del voluntario (requerido)
    
    ## Respuesta
    Objeto VolunteerOut con información completa del voluntario.

    
    ## 📝 Ejemplo de uso
    `GET /volunteers/42`
    """
    return get_volunteer(db, id)

@router.put("/{id}", response_model=VolunteerOut)
def update(id: int, data: VolunteerUpdate, db: Session = Depends(get_db)):
    """

    Modifica los datos del perfil voluntario.
    Permite actualización parcial de disponibilidad y experiencia.
    
    ## Parámetros
    - **id**: Identificador único del voluntario a actualizar
    - **data**: Objeto VolunteerUpdate con campos a modificar (opcionales)
    
    ## Respuesta
    Objeto VolunteerOut con información actualizada del voluntario.
  
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /volunteers/42
    {
        "availability": "Tardes y fines de semana"
    }
    ```
    """
    return update_volunteer(db, id, data)

@router.delete("/{id}", response_model=VolunteerOut)
def delete(id: int, db: Session = Depends(get_db)):
    """
    Realiza eliminación lógica del voluntario manteniendo integridad de datos.
    
    ## Parámetros
    - **id**: Identificador único del voluntario a eliminar
    
    ## Respuesta
    Objeto VolunteerOut con estado actualizado a inactivo.

    
    ## 📝 Ejemplo de uso
    `DELETE /volunteers/42`

    """
    return delete_volunteer(db, id)

###

@router.get("/{id}/skills", response_model=VolunteerWithSkills)
def get_volunteer_skills(id: int, db: Session = Depends(get_db)):
    """
    Recupera las habilidades de un voluntario.
    Esencial para asignación inteligente a proyectos requeridos.
    
    ## Parámetros
    - **id**: Identificador único del voluntario
    
    ## Respuesta
    Objeto VolunteerWithSkills con información del voluntario y sus habilidades.
    
    ## 📝 Ejemplo de uso
    `GET /volunteers/42/skills`
    
    """
    return get_volunteer_with_skills(db, id)

@router.post("/{volunteer_id}/skills/{skill_id}", response_model=VolunteerWithSkills)
def add_skill(volunteer_id: int, skill_id: int, db: Session = Depends(get_db)):
    """
    Vincula una habilidad existente al perfil del voluntario.
    Expande las capacidades del voluntario para futuras asignaciones.
    
    ## Parámetros
    - **volunteer_id**: ID del voluntario a modificar
    - **skill_id**: ID de la habilidad a asignar
    
    ## Respuesta
    Código 201 Created con mensaje de confirmación.
    
    ## 📝 Ejemplo de uso
    `POST /volunteers/42/skills/7`
    
    """
    return add_skill_to_volunteer(db, volunteer_id, skill_id)


@router.delete("/{volunteer_id}/skills/{skill_id}", status_code=204)
def remove_skill(volunteer_id: int, skill_id: int, db: Session = Depends(get_db)):
    """

    Elimina una habilidad específica del perfil del voluntario.
    Utilizado cuando la habilidad ya no es relevante o correcta.
    
    ## Parámetros
    - **volunteer_id**: ID del voluntario a modificar
    - **skill_id**: ID de la habilidad a remover
    
    ## Respuesta
    Código 204 No Content con operación completada exitosamente.
 
    
    ## 📝 Ejemplo de uso
    `DELETE /volunteers/42/skills/7`
    
    """
    return remove_skill_from_volunteer(db, volunteer_id, skill_id)
    

