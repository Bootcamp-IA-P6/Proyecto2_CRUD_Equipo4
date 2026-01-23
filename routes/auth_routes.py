from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from controllers import auth_controller
from controllers.auth_controller import get_current_user
from schemas import auth_schema, users_schema
from models.users_model import User

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================
# RUTAS PÚBLICAS (sin autenticación)
# ============================================

@auth_router.post("/register", response_model=auth_schema.Token, status_code=status.HTTP_201_CREATED)
def register(user: auth_schema.UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema como voluntario.
    
    ## 🔓 Acceso público
    No requiere autenticación. Cualquiera puede registrarse.
    
    ## Parámetros
    - **user**: Objeto UserRegister con datos del nuevo usuario
    
    ## Respuesta
    Token JWT para acceso inmediato tras registro exitoso.
    El usuario se crea automáticamente con role_id=2 (Voluntario).
    
    ## 📝 Ejemplo de uso
    ```json
    POST /auth/register
    
    {
        "email": "voluntario@example.com",
        "password": "Password123!",
        "name": "Juan Pérez",
        "phone": "+34612345678",
        "birth_date": "1990-05-15"
    }
    ```
    
    ## ⚠️ Errores posibles
    - **400 Bad Request**: Email ya registrado o datos inválidos
    """
    return auth_controller.register_user(user, db)


@auth_router.post("/login", response_model=auth_schema.Token)
def login(user: auth_schema.UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión y obtiene token de acceso.
    
    ## 🔓 Acceso público
    No requiere autenticación.
    
    ## Parámetros
    - **user**: Objeto UserLogin con credenciales
    
    ## Respuesta
    Token JWT para autenticación en peticiones futuras.
    Incluye información del usuario (id, email, role_id) en el token.
    
    ## 📝 Ejemplo de uso
    ```json
    POST /auth/login
    
    {
        "email": "voluntario@example.com",
        "password": "Password123!"
    }
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Credenciales incorrectas
    - **403 Forbidden**: Cuenta inactiva
    """
    return auth_controller.login_user(user, db)


# ============================================
# RUTAS PROTEGIDAS (requieren autenticación)
# ============================================

@auth_router.get("/me", response_model=users_schema.UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado.
    
    ## 🔒 Permisos requeridos
    - Usuario autenticado (cualquier rol)
    
    ## Respuesta
    Información completa del perfil del usuario actual.
    Incluye: id, email, name, phone, birth_date, role_id, created_at, updated_at.
    
    ## 📝 Ejemplo de uso
    ```bash
    GET /auth/me
    Authorization: Bearer <token>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Cuenta inactiva
    - **404 Not Found**: Usuario no encontrado
    
    ## 💡 Nota
    Esta ruta es equivalente a GET /users/{user_id} cuando user_id es el del usuario actual.
    Útil para que el frontend obtenga datos del usuario sin conocer su ID.
    """
    return current_user


@auth_router.put("/me", response_model=users_schema.UserOut)
def update_my_profile(
    user_data: users_schema.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado.
    
    ## 🔒 Permisos requeridos
    - Usuario autenticado (cualquier rol)
    
    ## Parámetros
    - **user_data**: Objeto UserUpdate con campos a actualizar (todos opcionales)
    
    ## Restricciones
    - El usuario NO puede cambiar su propio `role_id`
    - Solo admin puede cambiar estos campos vía PUT /users/{id}
    
    ## Respuesta
    Objeto UserOut con información actualizada del usuario.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /auth/me
    Authorization: Bearer <token>
    
    {
        "name": "Juan Carlos Pérez",
        "phone": "+34687654321",
        "birth_date": "1990-05-15"
    }
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **400 Bad Request**: Datos inválidos o email ya existe
    - **403 Forbidden**: Intento de cambiar role_id
    
    ## 💡 Nota
    Esta ruta es equivalente a PUT /users/{user_id} pero siempre actualiza
    al usuario autenticado, sin necesidad de especificar el ID.
    """
    # Validar que el usuario no intente cambiar su role_id 
    if user_data.role_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own role. Contact an administrator."
        )
    
    # Usar el UserController para actualizar
    from controllers.users_controller import UserController
    return UserController.update_user(db, user_id=current_user.id, user=user_data)


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)):
    """
    Cierra la sesión del usuario.
    
    ## 🔒 Permisos requeridos
    - Usuario autenticado (cualquier rol)
    
    ## Nota técnica
    Con JWT, el logout es manejado del lado del cliente eliminando el token.
    Este endpoint existe principalmente para:
    - Mantener consistencia REST
    - Registrar el evento de logout en logs
    - Permitir extensión futura (lista negra de tokens, etc.)
    
    ## 📝 Ejemplo de uso
    ```bash
    POST /auth/logout
    Authorization: Bearer <token>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    
    ## 💡 Implementación en cliente
    El cliente debe:
    1. Llamar a este endpoint
    2. Eliminar el token del almacenamiento local
    3. Redirigir al usuario a la página de login
    """
    # Con JWT no hay invalidación server-side real
    # El cliente debe eliminar el token
    # Aquí solo registramos el evento en logs
    return None