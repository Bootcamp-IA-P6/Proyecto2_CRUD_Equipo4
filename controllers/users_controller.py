from sqlalchemy.orm import Session
from models.users_model import User
from schemas import users_schema as schema
from fastapi import HTTPException
from utils.security import hash_password
from datetime import datetime
import logging


logger = logging.getLogger("app.users")


class UserController:

    @staticmethod
    #GET ALL USERS
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[schema.UserOut]:
        logger.info("Getting users list")
        users = db.query(User).offset(skip).limit(limit).all()
        return [schema.UserOut.model_validate(user) for user in users]  

    @staticmethod
    #GET USER BY ID
    def get_one_user(db: Session, user_id: int) -> schema.UserOut:
        logger.info(f"Getting user with id={user_id}")
        user =  db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        return schema.UserOut.model_validate(user)
    

    @staticmethod
    #CREATE USER
    def create_user(db: Session, user: schema.UserCreate) -> schema.UserOut:
        hashed_password = hash_password(user.password)
        logger.info(f"Creating user with email={user.email}")
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
            logger.info(f"User with id={db_user.id} created")
            return schema.UserOut.model_validate(db_user)
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail="Error creating user")
    
    @staticmethod
    #UPDATE USER
    def update_user(db: Session, user_id: int, user: schema.UserUpdate) -> schema.UserOut:
        logger.info(f"Updating user with id={user_id}")
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning(f"User with id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
    #Actualizar solo los campos que se envian
        if user.name is not None:
            db_user.name = user.name
        if user.email is not None:
            db_user.email = user.email
        if user.password is not None:
            db_user.password = hash_password(user.password)
        if user.phone is not None:
            db_user.phone = user.phone
        if user.birth_date is not None:
            db_user.birth_date = user.birth_date
            
        try:
            db.commit()
            db.refresh(db_user)
            logger.info(f"User with id={db_user.id} updated")
            return schema.UserOut.model_validate(db_user)
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error updating user: {e}")
            raise HTTPException(status_code=500, detail="Error updating user")
    
    @staticmethod
    #DELETE USER
    def delete_user(db: Session, user_id: int):
        logger.info(f"Deleting user with id={user_id}")
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning(f"User with id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            db_user.deleted_at = datetime.utcnow()
            db.commit()
            logger.info(f"User with id={db_user.id} deleted")
            return {"message": "User deleted successfully"}
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error deleting user: {e}")
            raise HTTPException(status_code=500, detail="Error deleting user")