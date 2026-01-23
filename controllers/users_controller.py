from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from fastapi import HTTPException
from datetime import datetime

from models.users_model import User
from schemas import users_schema
from utils.security import hash_password
from config.logging_config import get_logger


logger = get_logger("Users")


class UserController:

    @staticmethod
    #GET ALL USERS
    def get_users(db: Session) -> Page[users_schema.UserOut]:
        logger.info("Getting users list")
        
        return paginate (db.query(User).filter(User.deleted_at.is_(None)))
        
        

    @staticmethod
    #GET USER BY ID
    def get_one_user(db: Session, user_id: int):
        logger.info(f"Getting user with ID {user_id}")
        
        user =  (
            db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")   #Not found
        
        return users_schema.UserOut.model_validate(user)
    

    @staticmethod
    #CREATE USER
    def create_user(db: Session, user: users_schema.UserCreate):
        logger.info(f"Creating user")
        
        hashed_password = hash_password(user.password)
        
        if db.query(User).filter(User.email == user.email).first():
            logger.warning(f"User with email: {user.email} already exists")
            raise HTTPException(status_code=409, detail="User already exists")  #Conflict
        
        try:
            db_user = User(
                email=user.email, 
                name=user.name, 
                password=hashed_password,
                phone=user.phone,
                birth_date=user.birth_date,
                )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User with ID {db_user.id} created")
            return users_schema.UserOut.model_validate(db_user)
        
        except IntegrityError as e: 
            db.rollback()
            logger.exception(f"Integrity error creating user: {e}")
            raise HTTPException(status_code=409, detail="User already exists")     #Conflict
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Unexpected error creating user: {e}")
            raise HTTPException(status_code=500, detail="Error creating user")      #Internal server error
        
    
    @staticmethod
    #UPDATE USER
    def update_user(db: Session, user_id: int, user: users_schema.UserUpdate):
        logger.info(f"Updating user with ID: {user_id}")
        
        db_user = (
            db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        
        if not db_user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")   #Not found
        
        #Actualizar solo los campos que se envian
        try:
            if user.name is not None:
                db_user.name = user.name
            if user.email is not None:
                #validar email único si cambia
                if (
                    db.query(User)
                    .filter(User.email == user.email, User.id != user_id)
                    .first()
                ):
                    logger.warning(f"Email {user.email} already exists for another user")
                    raise HTTPException(
                        status_code=409, detail="Email already exists"      #Conflict
                )
                db_user.email = user.email
            if user.password is not None:
                db_user.password = hash_password(user.password)
            if user.phone is not None:
                db_user.phone = user.phone
            if user.birth_date is not None:
                db_user.birth_date = user.birth_date
        
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User with ID {user_id} updated")
            return users_schema.UserOut.model_validate(db_user)
        
        except HTTPException:
            db.rollback()
            raise
        
        except IntegrityError:
            db.rollback()
            logger.warning(f"Integrity error updating user {user_id}")
            raise HTTPException( status_code=409, detail="Email already exists")    #Conflict
            
        except Exception as e:
            db.rollback()
            logger.exception(f"Error updating user with ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Error updating user")      #Internal server Error
    
    @staticmethod
    #DELETE USER
    def delete_user(db: Session, user_id: int):
        logger.info(f"Deleting user with ID {user_id}")
        
        db_user = (
            db.query(User).filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        
        if not db_user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")       #Not found
        
        try:
            db_user.deleted_at = datetime.utcnow()
            db.commit()
            logger.info(f"User with ID {user_id} deleted")
            return {"message": "User deleted successfully"}
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error deleting user ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Error deleting user")      #Internal server error