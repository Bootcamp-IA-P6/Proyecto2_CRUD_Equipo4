from sqlalchemy.orm import Session
from models.users_model import User
from schemas import users_schema
from fastapi import HTTPException
from utils.security import hash_password
from datetime import datetime


class UserController:

    @staticmethod
    #GET ALL USERS
    async def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).filter(User.deleted_at.is_(None)).offset(skip).limit(limit).all()

    @staticmethod
    #GET USER BY ID
    async def get_one_user(db: Session, user_id: int):
        user =  db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    #CREATE USER
    async def create_user(db: Session, user: users_schema.UserCreate):
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email, 
            name=user.name, 
            password=hashed_password,
            phone=user.phone,
            birth_date=user.birth_date,
            #role_id=user.role_id
            )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    #UPDATE USER
    async def update_user(db: Session, user_id: int, user: users_schema.UserUpdate):
        db_user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        if not db_user:
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
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    #DELETE USER
    async def delete_user(db: Session, user_id: int):
        db_user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        return None