from app.config.logging_config import get_logger
from sqlalchemy.orm import Session
from app.models.users_model import User
from app.utils.security import * 
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.database import get_db

logger = get_logger("Authentication")
security = HTTPBearer()


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
        role_id=2  # Voluntario por defecto
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
        "id": db_user.id,
        "email": db_user.email,
        "role_id": db_user.role_id
    }
    access_token = create_access_token(token_data) 
    logger.info(f"User with email={user_data.email} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}


# Dependencia para obtener usuario actual
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extrae y valida el token JWT del header Authorization.
    Retorna el usuario autenticado.
    """
    logger.info("Getting current user")
    token = credentials.credentials
    
    payload = decode_access_token(token)
    if not payload:
        logger.warning("Invalid token or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_email = payload.get("email")
    if not user_email:
        logger.warning("Token payload missing email")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        logger.warning(f"User not found: {user_email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    logger.info(f"User authenticated: {user.email} (role_id={user.role_id})")
    return user


# Dependencia para requerir permisos de admin
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Valida que el usuario actual tenga rol de administrador (role_id = 1).
    Debe usarse después de get_current_user.
    """
    if current_user.role_id != 1:
        logger.warning(f"Access Denied for {current_user.email}: User is not an admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Admin permissions required"
        )
    
    logger.info(f"Admin access granted for {current_user.email}")
    return current_user


# Dependencia para verificar que el usuario accede a sus propios datos o es admin
def require_owner_or_admin(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    """
    Valida que el usuario actual sea el dueño del recurso o sea administrador.
    """
    if current_user.role_id != 1 and current_user.id != user_id:
        logger.warning(
            f"Access Denied for {current_user.email}: "
            f"Not owner (id={current_user.id}) and not admin"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You can only access your own data"
        )
    
    return current_user