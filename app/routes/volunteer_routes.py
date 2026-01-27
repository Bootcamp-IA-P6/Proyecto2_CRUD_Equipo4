from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from app.database.database import get_db
from app.schemas.volunteer_schema import (
    VolunteerCreate,
    VolunteerUpdate,
    VolunteerOut,
    VolunteerWithSkills
)
from app.controllers.volunteer_controller import *
from app.controllers.auth_controller import get_current_user, require_admin
from app.models.users_model import User

router = APIRouter(
    prefix="/volunteers",
    tags=["Volunteers"]
)

# Constantes para roles
ROLE_ADMIN = 1
ROLE_VOLUNTEER = 2


@router.post("/", response_model=VolunteerOut)
def create(
    volunteer: VolunteerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra un nuevo voluntario vinculándolo a un usuario existente.
    
    ## Permisos
    - ✅ Admin: puede crear perfil de voluntario para cualquier usuario
    
    ## Parámetros
    - **volunteer**: Objeto VolunteerCreate con información del voluntario
    
    ## Respuesta
    Objeto VolunteerOut con información del voluntario creado.
    
    ## 📝 Ejemplo de uso
    ```json
    POST /volunteers/
    {
        "user_id": 42,
        "status": active
    }
    ```
    """
    # Verificar que el usuario solo pueda crear su propio perfil (a menos que sea admin)
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only create your own volunteer profile"
        )
    
    return create_volunteer(db, volunteer)


@router.get("/", response_model=Page[VolunteerOut])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Recupera información completa de todos los voluntarios activos del sistema.
    Implementa paginación para manejar grandes volúmenes eficientemente.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede ver todos los voluntarios
    - ❌ Voluntario: no tiene acceso a listado completo
    
    ## Respuesta
    Lista paginada de objetos VolunteerOut con información detallada de cada voluntario.
    
    ## 📝 Ejemplo de uso
    `GET /volunteers/?page=1&size=10`
    """
    return get_volunteers(db)


@router.get("/{id}", response_model=VolunteerOut)
def get_one(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera el perfil completo de un voluntario mediante su ID.
    
    ## Permisos
    - ✅ Admin: puede ver cualquier perfil de voluntario
    - ✅ Voluntario: solo puede ver su propio perfil
    
    ## Parámetros
    - **id**: Identificador único del voluntario (requerido)
    
    ## Respuesta
    Objeto VolunteerOut con información completa del voluntario.
    
    ## 📝 Ejemplo de uso
    `GET /volunteers/42`
    """
    # Primero obtener el voluntario para verificar permisos
    volunteer = get_volunteer(db, id)
    
    # Verificar que el usuario pueda ver este perfil
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only view your own volunteer profile"
        )
    
    return volunteer


@router.put("/{id}", response_model=VolunteerOut)
def update(
    id: int,
    data: VolunteerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Modifica los datos del perfil voluntario.
    Permite actualización parcial de disponibilidad y experiencia.
    
    ## Permisos
    - ✅ Admin: puede actualizar cualquier perfil de voluntario
    - ✅ Voluntario: solo puede actualizar su propio perfil
    
    ## Parámetros
    - **id**: Identificador único del voluntario a actualizar
    - **data**: Objeto VolunteerUpdate con campos a modificar (opcionales)
    
    ## Respuesta
    Objeto VolunteerOut con información actualizada del voluntario.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /volunteers/42
    {
        "availability": "Tardes y fines de semana",
        "experience": "5 años en ONGs internacionales"
    }
    ```
    """
    # Primero obtener el voluntario para verificar permisos
    volunteer = get_volunteer(db, id)
    
    # Verificar que el usuario pueda actualizar este perfil
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only update your own volunteer profile"
        )
    
    return update_volunteer(db, id, data)


@router.delete("/{id}", response_model=VolunteerOut)
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Realiza eliminación lógica del voluntario manteniendo integridad de datos.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede eliminar cualquier perfil de voluntario
    - ❌ Voluntario: no puede eliminar perfiles
    
    ## Parámetros
    - **id**: Identificador único del voluntario a eliminar
    
    ## Respuesta
    Objeto VolunteerOut con estado actualizado a inactivo.
    
    ## 📝 Ejemplo de uso
    `DELETE /volunteers/42`
    """
    return delete_volunteer(db, id)


### RUTAS DE HABILIDADES (SKILLS) ###

@router.get("/{id}/skills", response_model=VolunteerWithSkills)
def get_volunteer_skills(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera las habilidades de un voluntario.
    Esencial para asignación inteligente a proyectos requeridos.
    
    ## Permisos
    - ✅ Admin: puede ver habilidades de cualquier voluntario
    - ✅ Voluntario: solo puede ver sus propias habilidades
    
    ## Parámetros
    - **id**: Identificador único del voluntario
    
    ## Respuesta
    Objeto VolunteerWithSkills con información del voluntario y sus habilidades.
    
    ## 📝 Ejemplo de uso
    `GET /volunteers/42/skills`
    """
    # Obtener el voluntario con sus habilidades
    volunteer = get_volunteer_with_skills(db, id)
    
    # Verificar permisos
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only view your own skills"
        )
    
    return volunteer


@router.post("/{volunteer_id}/skills/{skill_id}", response_model=VolunteerWithSkills)
def add_skill(
    volunteer_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Vincula una habilidad existente al perfil del voluntario.
    Expande las capacidades del voluntario para futuras asignaciones.
    
    ## Permisos
    - ✅ Admin: puede agregar habilidades a cualquier voluntario
    - ✅ Voluntario: solo puede agregar habilidades a su propio perfil
    
    ## Parámetros
    - **volunteer_id**: ID del voluntario a modificar
    - **skill_id**: ID de la habilidad a asignar
    
    ## Respuesta
    Objeto VolunteerWithSkills con la nueva habilidad agregada.
    
    ## 📝 Ejemplo de uso
    `POST /volunteers/42/skills/7`
    """
    # Primero obtener el voluntario para verificar permisos
    volunteer = get_volunteer(db, volunteer_id)
    
    # Verificar que el usuario pueda modificar este perfil
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only add skills to your own profile"
        )
    
    return add_skill_to_volunteer(db, volunteer_id, skill_id)


@router.delete("/{volunteer_id}/skills/{skill_id}", status_code=204)
def remove_skill(
    volunteer_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una habilidad específica del perfil del voluntario.
    Utilizado cuando la habilidad ya no es relevante o correcta.
    
    ## Permisos
    - ✅ Admin: puede remover habilidades de cualquier voluntario
    - ✅ Voluntario: solo puede remover habilidades de su propio perfil
    
    ## Parámetros
    - **volunteer_id**: ID del voluntario a modificar
    - **skill_id**: ID de la habilidad a remover
    
    ## Respuesta
    Código 204 No Content con operación completada exitosamente.
    
    ## 📝 Ejemplo de uso
    `DELETE /volunteers/42/skills/7`
    """
    # Primero obtener el voluntario para verificar permisos
    volunteer = get_volunteer(db, volunteer_id)
    
    # Verificar que el usuario pueda modificar este perfil
    if current_user.role_id != ROLE_ADMIN and volunteer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only remove skills from your own profile"
        )
    
    return remove_skill_from_volunteer(db, volunteer_id, skill_id)