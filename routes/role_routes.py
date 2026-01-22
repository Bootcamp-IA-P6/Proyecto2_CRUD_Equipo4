from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy.orm import Session

from database.database import get_db
from controllers.role_controller import RoleController
from schemas import role_schema

role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

#GET ALL
@role_router.get("/", response_model=list[role_schema.RoleOut])
def read_roles(db: Session = Depends(get_db)):
    """
    Recupera el catálogo completo de roles disponibles.
    Base para asignación de permisos y gestión de acceso.
    
    ## Respuesta
    Lista de objetos RoleOut con información de cada rol.
    
    
    ## 📝 Ejemplo de uso
    `GET /roles/`

    """
    return RoleController.get_roles(db)

#GET ROLE BY ID
@role_router.get("/{role_id}", response_model=role_schema.RoleOut)
def read_role(role_id: int, db: Session = Depends(get_db)):
    """
    Recupera detalles completos de un rol mediante su ID.

    ## Parámetros
    - **role_id**: Identificador único del rol
    
    ## Respuesta
    Objeto RoleOut con información completa del rol.

    
    ## 📝 Ejemplo de uso
    `GET /roles/3`
    """
    return RoleController.get_one_role(db, role_id=role_id)

#POST 
@role_router.post("/", response_model=role_schema.RoleOut)
def create_role(role: role_schema.RoleCreate, db: Session = Depends(get_db)):
    #permisos futuros para admin
    """
    Registra un nuevo rol con permisos específicos.
    
    ## Parámetros
    - **role**: Objeto RoleCreate con información del rol
    
    ## Respuesta
    Objeto RoleOut con información del rol creado.
    
    ## 📝 Ejemplo de uso
    ```json
    POST /roles/
    {
        "name": "Coordinador de Proyectos",
        "description": "Gestiona proyectos, asigna voluntarios y reporta progreso",
        "permissions": ["create_project", "assign_volunteers", "generate_reports"]
    }
    ```
    """
    return RoleController.create_role(db, role)