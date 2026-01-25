from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.controllers.role_controller import RoleController
from app.schemas import role_schema
from app.controllers.auth_controller import get_current_user, require_admin
from app.models.users_model import User

role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

# GET ALL - Solo administradores pueden ver roles
@role_router.get("/", response_model=list[role_schema.RoleOut])
def read_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Recupera el catálogo completo de roles disponibles.
    Base para asignación de permisos y gestión de acceso.
    
    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## Respuesta
    Lista de objetos RoleOut con información de cada rol.
    
    ## 📝 Ejemplo de uso
    ```bash
    GET /roles/
    Authorization: Bearer <token_admin>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    """
    return RoleController.get_roles(db)


# GET ROLE BY ID - Solo administradores
@role_router.get("/{role_id}", response_model=role_schema.RoleOut)
def read_role(
    role_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Recupera detalles completos de un rol mediante su ID.

    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## Parámetros
    - **role_id**: Identificador único del rol
    
    ## Respuesta
    Objeto RoleOut con información completa del rol.

    ## 📝 Ejemplo de uso
    ```bash
    GET /roles/3
    Authorization: Bearer <token_admin>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **404 Not Found**: Rol no encontrado
    """
    return RoleController.get_one_role(db, role_id=role_id)


# POST - Solo administradores pueden crear roles
@role_router.post("/", response_model=role_schema.RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    role: role_schema.RoleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Registra un nuevo rol con permisos específicos.
    
    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## Parámetros
    - **role**: Objeto RoleCreate con información del rol
    
    ## Respuesta
    Objeto RoleOut con información del rol creado.
    
    ## 📝 Ejemplo de uso
    ```json
    POST /roles/
    Authorization: Bearer <token_admin>
    
    {
        "name": "Coordinador de Proyectos",
        "description": "Gestiona proyectos, asigna voluntarios y reporta progreso",
        "permissions": ["create_project", "assign_volunteers", "generate_reports"]
    }
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **400 Bad Request**: Rol ya existe o datos inválidos
    """
    return RoleController.create_role(db, role)


# PUT - Solo administradores pueden actualizar roles
@role_router.put("/{role_id}", response_model=role_schema.RoleOut)
def update_role(
    role_id: int,
    role: role_schema.RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualiza información de un rol existente.
    
    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## Parámetros
    - **role_id**: Identificador único del rol
    - **role**: Objeto RoleCreate con información actualizada
    
    ## Respuesta
    Objeto RoleOut con información del rol actualizado.
    
    ## 📝 Ejemplo de uso
    ```json
    PUT /roles/3
    Authorization: Bearer <token_admin>
    
    {
        "name": "Coordinador Senior",
        "description": "Coordinador con permisos extendidos",
        "permissions": ["create_project", "assign_volunteers", "generate_reports", "approve_budget"]
    }
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **404 Not Found**: Rol no encontrado
    """
    return RoleController.update_role(db, role_id=role_id, role=role)


# DELETE - Solo administradores pueden eliminar roles
@role_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Elimina un rol del sistema.
    
    ## 🔒 Permisos requeridos
    - **Administrador (role_id = 1)**
    
    ## ⚠️ Precauciones
    No se puede eliminar un rol si hay usuarios asignados a él.
    
    ## Parámetros
    - **role_id**: Identificador único del rol
    
    ## Respuesta
    204 No Content si la eliminación fue exitosa.
    
    ## 📝 Ejemplo de uso
    ```bash
    DELETE /roles/5
    Authorization: Bearer <token_admin>
    ```
    
    ## ⚠️ Errores posibles
    - **401 Unauthorized**: Token inválido o expirado
    - **403 Forbidden**: Usuario no es administrador
    - **404 Not Found**: Rol no encontrado
    - **400 Bad Request**: Rol tiene usuarios asignados
    """
    RoleController.delete_role(db, role_id=role_id)
    return None