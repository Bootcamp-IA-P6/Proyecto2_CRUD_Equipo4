from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy.orm import Session
from typing import List 

from database.database import get_db
from controllers.users_controller import UserController
from schemas import users_schema

user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

#GET ALL
@user_router.get("/", response_model=List[users_schema.UserOut])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = await UserController.get_users(db, skip=skip, limit=limit)
    return users

#GET USER BY ID
@user_router.get("/{user_id}", response_model=users_schema.UserOut)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = await UserController.get_one_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#CREATE USER
@user_router.post("/", response_model=users_schema.UserOut)
async def create_user(user: users_schema.UserCreate, db: Session = Depends(get_db)):
    new_user = await UserController.create_user(db, user=user)
    return new_user

#UPDATE USER
@user_router.put("/{user_id}", response_model=users_schema.UserOut)
async def update_user(user_id: int, user: users_schema.UserUpdate, db: Session = Depends(get_db)):
    updated_user = await UserController.update_user(db, user_id=user_id, user=user)
    if updated_user is None: 
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

#SOFT DELETE USER
@user_router.delete("/{user_id}", response_model=users_schema.UserOut)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = await UserController.delete_user(db, user_id=user_id)
    return deleted_user