from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.database import get_db
from controllers import auth_controller
from schemas import auth_schema

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


#Registro de Usuario
@auth_router.post("/register", response_model=auth_schema.Token, status_code=status.HTTP_201_CREATED)
def register(user: auth_schema.UserRegister, db: Session = Depends(get_db)):
    return auth_controller.register_user(user, db)


#Login de Usuario
@auth_router.post("/login", response_model=auth_schema.Token)
def login(user: auth_schema.UserLogin, db: Session = Depends(get_db)):
    return auth_controller.login_user(user, db)


#Dependencia para obtener usuario actual
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return auth_controller.get_current_user(token, db)


#Dependencia para permisos de admin
def require_admin(current_user: User = Depends(get_current_user)):
    return auth_controller.require_admin(current_user)