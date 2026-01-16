from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy.orm import Session

from database.database import get_db
from controllers.role_controller import RoleController
from schemas import role_schema

role_router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)

#GET ALL
@role_router.get("/", response_model=list[role_schema.RoleOut])
def read_roles(db: Session = Depends(get_db)):
    return RoleController.get_roles(db)

#GET ROLE BY ID
@role_router.get("/{role_id}", response_model=role_schema.RoleOut)
def read_role(role_id: int, db: Session = Depends(get_db)):
    role = RoleController.get_one_role(db, role_id=role_id)

#POST 
@role_router.post("/", response_model=role_schema.RoleOut)
def create_role(role: role_schema.RoleCreate, db: Session = Depends(get_db)):
    #permisos futuros para admin
    return RoleController.create_role(db, role)