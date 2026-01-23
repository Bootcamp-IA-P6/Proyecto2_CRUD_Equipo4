from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_pagination import Page

from database.database import get_db
from controllers.users_controller import UserController
from controllers.auth_controller import get_current_user, require_admin, require_owner_or_admin
from schemas import users_schema
from models.users_model import User

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Constantes para roles
ROLE_ADMIN = 1
ROLE_VOLUNTEER = 2


# GET ALL USERS - Solo admin puede ver todos los usuarios
@user_router.get("/", response_model=Page[users_schema.UserOut])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Recupera una lista paginada de todos los usuarios activos del sistema.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede ver todos los usuarios
    - ❌ Voluntario: no tiene acceso
    
    ## Parámetros
    - **page**: Número de página (default: 1)
    - **size**: Tamaño de página (default: 50)
    
    ## Respuesta
    Lista paginada de objetos UserOut con información completa de usuarios.
    
    ## 📝 Ejemplo de uso
    `GET /users/?page=1&size=10`
    """
    return UserController.get_users(db)


# GET USER BY ID - Usuario puede ver su propio perfil, admin puede ver cualquiera
@user_router.get("/{user_id}", response_model=users_schema.UserOut)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera la información completa de un usuario mediante su identificador único.
    
    ## Permisos
    - ✅ Admin: puede ver cualquier usuario
    - ✅ Voluntario: solo puede ver su propio perfil
    
    ## Parámetros
    - **user_id**: Identificador único del usuario (requerido)
    
    ## Respuesta
    Objeto UserOut con información completa del usuario solicitado.
    
    ## 📝 Ejemplo de uso
    `GET /users/42`
    """
    # Verificar permisos: admin puede ver cualquiera, usuario solo a sí mismo
    if current_user.role_id != ROLE_ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only view your own profile"
        )
    
    return UserController.get_one_user(db, user_id=user_id)


# CREATE USER - Solo admin puede crear usuarios directamente
@user_router.post("/", response_model=users_schema.UserOut)
def create_user_by_admin(
    user: users_schema.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Registra un nuevo usuario en el sistema con validación automática de email único.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede crear usuarios con cualquier rol
    - ❌ Voluntario: debe usar /auth/register
    
    ## Parámetros
    - **user**: Objeto UserCreate con información del nuevo usuario
    
    ## Respuesta
    Objeto UserOut con información del usuario recién creado (sin contraseña).
    
    ## 📝 Ejemplo de uso
    ```json
    POST /users/
    {
        "name": "María García",
        "email": "maria.garcia@empresa.com",
        "password": "SecurePass123!",
        "phone": "+34 600 123 456",
        "birth_date": "1990-05-15",
        "role_id": 1
    }
    ```
    
    **Nota:** El público general debe usar `/auth/register` para auto-registrarse como voluntario.
    """
    return UserController.create_user(db, user=user)


# UPDATE USER - Usuario actualiza su propio perfil, admin puede actualizar cualquiera
@user_router.put("/{user_id}", response_model=users_schema.UserOut)
def update_user_profile(
    user_id: int,
    user: users_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Modifica la información del usuario existente.
    Permite actualización parcial (solo los campos proporcionados).
    
    ## Permisos
    - ✅ Admin: puede actualizar cualquier usuario
    - ✅ Voluntario: solo puede actualizar su propio perfil
    
    ## Parámetros
    - **user_id**: Identificador único del usuario a actualizar
    - **user**: Objeto UserUpdate con campos a modificar (opcionales)
    
    ## Restricciones
    - Los voluntarios NO pueden cambiar su propio `role_id`
    - Solo admin puede cambiar roles
    
    ## Respuesta
    Objeto UserOut con la información actualizada del usuario.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /users/42
    {
        "name": "María García López",
        "phone": "+34 600 999 888"
    }
    ```
    """
    # Verificar permisos: admin puede actualizar cualquiera, usuario solo a sí mismo
    if current_user.role_id != ROLE_ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only update your own profile"
        )
    
    # Si no es admin e intenta cambiar el role_id, denegar
    if current_user.role_id != ROLE_ADMIN and user.role_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You cannot change your own role"
        )
    
    return UserController.update_user(db, user_id=user_id, user=user)


# SOFT DELETE USER - Solo admin puede eliminar usuarios
@user_router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Realiza eliminación lógica del usuario marcándolo como inactivo.
    Mantiene integridad referencial de datos históricos.
    **Requiere permisos de administrador.**
    
    ## Permisos
    - ✅ Admin: puede eliminar cualquier usuario
    - ❌ Voluntario: no puede eliminar usuarios
    
    ## Parámetros
    - **user_id**: Identificador único del usuario a eliminar
    
    ## Respuesta
    Diccionario con mensaje de confirmación y estado de la operación.
    
    ## 📝 Ejemplo de uso
    `DELETE /users/42`
    
    **Nota:** Esta es una eliminación lógica (soft delete). 
    El usuario se marca como inactivo pero permanece en la base de datos.
    """
    return UserController.delete_user(db, user_id=user_id)