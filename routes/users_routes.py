from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List 

from database.database import get_db
from controllers.users_controller import UserController
from schemas import users_schema

user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

#GET ALL USERS
@user_router.get("/", response_model=List[users_schema.UserOut])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return UserController.get_users(db, skip=skip, limit=limit)
    

#GET USER BY ID
@user_router.get("/{user_id}", response_model=users_schema.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return UserController.get_one_user(db, user_id=user_id)


#CREATE USER
@user_router.post("/", response_model=users_schema.UserOut)
def create_user(user: users_schema.UserCreate, db: Session = Depends(get_db)):
    return UserController.create_user(db, user=user)


#UPDATE USER
@user_router.put("/{user_id}", response_model=users_schema.UserOut)
def update_user(user_id: int, user: users_schema.UserUpdate, db: Session = Depends(get_db)):
    return UserController.update_user(db, user_id=user_id, user=user)


#SOFT DELETE USER
@user_router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return UserController.delete_user(db, user_id=user_id)