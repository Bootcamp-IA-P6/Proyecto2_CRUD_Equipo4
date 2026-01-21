from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List 

from database.database import get_db
from controllers.users_controller import UserController
from schemas import users_schema

user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

#GET ALL USERS
@user_router.get("/", response_model=List[users_schema.UserOut])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Recupera una lista paginada de todos los usuarios activos del sistema.

    
    ## Parámetros
    - **skip**: Número de registros a omitir para paginación (default: 0)
    - **limit**: Máximo número de registros a devolver (default: 100, max: 1000)
    
    ## Respuesta
    Lista de objetos UserOut con información completa de usuarios.
    Incluye: id, name, email, phone, birth_date, created_at, updated_at.
    
    
    ## 📝 Ejemplo de uso
    `GET /users/?skip=0&limit=10`

    """
    return UserController.get_users(db, skip=skip, limit=limit)
    

#GET USER BY ID
@user_router.get("/{user_id}", response_model=users_schema.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """

    Recupera la información completa de un usuario mediante su identificador único.
    
    ## Parámetros
    - **user_id**: Identificador único del usuario (requerido)
    
    ## Respuesta
    Objeto UserOut con información completa del usuario solicitado.
    
    
    ## 📝 Ejemplo de uso
    `GET /users/42`

    """
    return UserController.get_one_user(db, user_id=user_id)


#CREATE USER
@user_router.post("/", response_model=users_schema.UserOut)
def create_user(user: users_schema.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema con validación automática de email único.
    Implementa hashing automático de contraseña para seguridad.
    
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
        "birth_date": "1990-05-15"
    }
    ```
    
    """
    return UserController.create_user(db, user=user)


#UPDATE USER
@user_router.put("/{user_id}", response_model=users_schema.UserOut)
def update_user(user_id: int, user: users_schema.UserUpdate, db: Session = Depends(get_db)):
    """

    Modifica la información de un usuario existente.
    Permite actualización parcial (solo los campos proporcionados).
    
    ## Parámetros
    - **user_id**: Identificador único del usuario a actualizar
    - **user**: Objeto UserUpdate con campos a modificar (opcionales)
    
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
    return UserController.update_user(db, user_id=user_id, user=user)


#SOFT DELETE USER
@user_router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """

    Realiza eliminación lógica del usuario marcándolo como inactivo.
    Mantiene integridad referencial de datos históricos.
    
    ## Parámetros
    - **user_id**: Identificador único del usuario a eliminar
    
    ## Respuesta
    Diccionario con mensaje de confirmación y estado de la operación.
    
    
    ## 📝 Ejemplo de uso
    `DELETE /users/42`
    
    """
    return UserController.delete_user(db, user_id=user_id)
