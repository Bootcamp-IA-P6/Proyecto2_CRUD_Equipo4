from config.logging_config import get_logger
from sqlalchemy.orm import Session
from models.users_model import User
from utils.security import * 
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

logger = get_logger("auth")


#Registro de Usuario
def register_user(user_data, db: Session):
    logger.info(f"Trying to register user with email={user_data.email}")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Register Error: User with email={user_data.email} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password=hashed_pwd,
        phone=user_data.phone,
        birth_date=user_data.birth_date,
        role_id=2
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User with email={user_data.email} registered successfully")
    token_data = {
        "id": new_user.id,
        "email": new_user.email,
        "role_id": new_user.role_id
    }
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


#Login de Usuario

def login_user(user_data, db: Session):
    logger.info(f"Trying to login user with email={user_data.email}")
    
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if not db_user or not verify_password(user_data.password, db_user.password):
        logger.warning(f"Login Error: Invalid email or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    token_data = {
        "email": db_user.email,
        "role_id": db_user.role_id
    }
    access_token = create_access_token(token_data) 
    logger.info(f"User with email={user_data.email} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

#Dependencia para obtener usuario actual
def get_current_user(token: str , db: Session):
    logger.info("Getting current user")
    payload = decode_access_token(token)
    if not payload:
        logger.warning("Invalid token or expired token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.email== payload.get("email")).first()
    if not user:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

#Dependencia para permisos de admin
def require_admin(current_user: User):
    if current_user.role_id !=1:
        logger.warning(f"Access Denied for {current_user.email}: User is not an admin")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied: User don't have permissions for this action")
    logger.info(f"Access Granted for {current_user.email}: User is an admin")
    return current_user